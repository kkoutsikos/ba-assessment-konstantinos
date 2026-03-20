import sys
import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "section-1"))
sys.path.append(os.path.join(BASE_DIR, "section-2"))
sys.path.append(os.path.join(BASE_DIR, "section-3"))

# Section imports
import extract
import agent
import transform as transformer
import database

app = FastAPI(title="Invoice Processing App", version="1.0.0")

# Χρήση βάσης δεδομένων από το Section 2
INMEMORY_DB = database.INVOICES

class ExtractRequest(BaseModel):
    text: str = Field(..., description="Raw text of the invoice to extract")

class QueryRequest(BaseModel):
    question: str = Field(..., description="Natural language question about invoices")

class TransformRequest(BaseModel):
    records: List[Dict[str, Any]] = Field(..., description="Flat CSV-style records from System A")

class QueryResponse(BaseModel):
    answer: str
    tools_called: List[str]

@app.get("/invoices", response_model=List[Dict[str, Any]])
def get_all_invoices():
    """Returns all invoices currently stored in memory."""
    return INMEMORY_DB

@app.post("/invoices/extract")
def extract_invoice_endpoint(request: ExtractRequest):
    """
    Accepts raw invoice text, uses LangChain LLM extraction, validates with Pydantic.
    """
    result = extract.extract_invoice(request.text)
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="LLM failed to produce valid JSON after maximum retries."
        )
    
    
    extracted_dict = result.model_dump()
    INMEMORY_DB.append(extracted_dict)
    
    return extracted_dict

@app.post("/invoices/transform")
def transform_invoices_endpoint(request: TransformRequest):
    """
    Transforms System A flat records to System B nested format using actual Section 3 logic.
    """
    result = transformer.transform(request.records)
    
    # Εάν υπάρξουν validation errors κατά τον μετασχηματισμό, επιστρέφουμε HTTP 422
    if result.get("validation_errors"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=result["validation_errors"]
        )
        
    return result

@app.post("/invoices/query", response_model=QueryResponse)
def query_invoices_endpoint(request: QueryRequest):
    """
    Accepts a natural language question and uses the actual LangGraph agent to answer it.
    """
    config = {"configurable": {"thread_id": "api_thread"}}
    
    
    final_state = agent.app.invoke({"messages": [("user", request.question)]}, config)
    
    
    last_message = final_state['messages'][-1].content
    
    # Δυναμικός εντοπισμός των εργαλείων που αποφάσισε να καλέσει το μοντέλο
    tools_called = []
    for msg in final_state['messages']:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool in msg.tool_calls:
                tools_called.append(tool['name'])
                
    return QueryResponse(answer=last_message, tools_called=list(set(tools_called)))