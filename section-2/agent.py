# section-2/agent.py

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver # Προσθήκη μνήμης
from langchain_groq import ChatGroq # Αλλαγή σε Groq για αξιοπιστία
from tools import agent_tools
from langchain_core.messages import SystemMessage
import os
from dotenv import load_dotenv
import json

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
llm_with_tools = llm.bind_tools(agent_tools)

SYSTEM_PROMPT = """You are a precise financial AI agent. 
IMPORTANT RULES FOR TOOL USAGE:
1. NEVER call multiple tools at once if they depend on each other.
2. EXECUTE TOOLS STRICTLY ONE AT A TIME. 
3. NEVER guess, hallucinate, or invent arguments (like IDs or VAT numbers) for a tool. 
4. If you need data from Tool A to use in Tool B, you MUST call Tool A first, wait for the actual result, and only then call Tool B using the real data.
"""

def chatbot_node(state: State):
    processed_messages = []
    
    # Βάζουμε το System Prompt στην αρχή της μνήμης (αν δεν υπάρχει ήδη)
    if not any(isinstance(m, SystemMessage) for m in state["messages"]):
        processed_messages.append(SystemMessage(content=SYSTEM_PROMPT))
        
    for msg in state["messages"]:
        if hasattr(msg, "tool_call_id") and not isinstance(msg.content, str):
            msg.content = json.dumps(msg.content)
        processed_messages.append(msg)
    
    # Προσθήκη παραμέτρου (αν υποστηρίζεται από το ChatGroq) για να αποτρέψει τις παράλληλες κλήσεις
    llm_with_tools_strict = llm.bind_tools(agent_tools, parallel_tool_calls=False)
    
    response = llm_with_tools_strict.invoke(processed_messages)
    return {"messages": [response]}

# Graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_node("tools", ToolNode(tools=agent_tools))

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

# Προσθήκη Checkpointer για να δουλεύει το thread_id (μνήμη)
memory = MemorySaver()
app = graph_builder.compile(checkpointer=memory)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("      INVOICE AI AGENT READY (LANGGRAPH)")
    print("="*50)
    
    config = {"configurable": {"thread_id": "1"}}
    
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            
            for event in app.stream({"messages": [("user", user_input)]}, config, stream_mode="values"):
                last_msg = event["messages"][-1]
                
                # Αν το μήνυμα έχει tool_calls, το τυπώνουμε για να φαίνεται το reasoning
                if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                    for tc in last_msg.tool_calls:
                        print(f"  [AI is calling tool: {tc['name']} with args: {tc['args']}]")
            
            # Τυπώνουμε μόνο την τελική απάντηση του AI (το τελευταίο AIMessage)
            print(f"\nAgent: {last_msg.content}")
            
        except Exception as e:
            print(f"\n[ERROR]: {e}")