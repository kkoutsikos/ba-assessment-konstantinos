# AI Invoice Processing & Querying System

A comprehensive AI-powered API built with FastAPI, LangGraph, and LLMs to automate the extraction, transformation, and querying of invoice data.

## System Architecture & Modules

The project is strictly modularized into 5 distinct sections, each handling a specific part of the data pipeline:

* **Section 1: LLM-Powered Extraction (/section-1)**
  Responsible for converting raw, unstructured invoice text into structured JSON. It utilizes an LLM to parse the text and strictly validates the output using Pydantic models. It includes logic validation to ensure mathematical consistency (e.g., Net Amount + VAT = Gross Amount).

* **Section 2: Conversational AI Agent (/section-2)**
  Implements a LangGraph-based ReAct agent equipped with custom Python tools (`search_invoices`, `calculate_total`, `get_invoice_details`). This agent can understand natural language queries, search the shared in-memory database, perform aggregations, and return precise answers about the processed invoices.

* **Section 3: Data Transformation (/section-3)**
  Acts as an ETL adapter. It receives deeply nested legacy data ("System A" format), validates it against strict business rules (e.g., valid IBAN formats, strictly positive item quantities) using Pydantic, and transforms it into a modern, flattened schema ("System B").

* **Section 4: System Design (/section-4)**
  Contains the architectural documentation addressing scalability, reliability, and cost-efficiency for a production-grade deployment of this system.

* **Section 5: FastAPI Backend & Testing (/section-5)**
  The central application layer. It exposes RESTful endpoints (`/invoices/extract`, `/invoices/transform`, `/invoices/query`, `/invoices`) that integrate the modules above. It handles the mapping of different data schemas into a unified `INMEMORY_DB` so the Agent can query all data seamlessly. It also contains the `pytest` suite which thoroughly tests integration, edge cases, and robustness.

## Setup & Installation

### 1. Prerequisites
* Python 3.10+
* Docker (optional, for containerized execution)

### 2. Virtual Environment & Dependencies
Create a virtual environment and install the required packages:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

### 4. Running the Application
**Locally via Uvicorn:**
```bash
uvicorn section-5.app:app --reload
```
Access the Swagger UI at: http://127.0.0.1:8000/docs

**Via Docker:**
```bash
docker build -t ai-invoice-app .
docker run -p 8000:8000 --env-file .env ai-invoice-app
```

### 3. Environment Variables
Create a `.env` file in the root directory. You will need an API key for the LLM provider:

```env
# Required for Section 1 (Extraction) & Section 2 (Agent)
GROQ_API_KEY=your_groq_api_key_here

# Optional: For LangSmith tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_key
```

## LLM Provider Choice

Initially, Google's Gemini was considered for the extraction and agent logic. However, during extensive integration testing, strict free-tier rate limits were encountered (`429 RESOURCE_EXHAUSTED`). 

To ensure a robust, production-like experience without quota bottlenecks, the provider was switched to **Groq** (using Llama-3 models). 

**Why Groq?**
1. **Speed:** Lightning-fast inference, which is crucial for synchronous API endpoints like `/extract`.
2. **Reliability:** Avoided the frequent quota exhaustion seen in other free tiers.
3. **JSON Capabilities:** Excellent at adhering to strict Pydantic schemas for structured data extraction.

## Assumptions Made

During the development of this middleware, the following assumptions were made:

1. **Unified Schema Mapping:** The Agent (Section 2) searches for a generic `customer` field. I assumed that for extracted unstructured invoices, the "Seller" acts as the primary entity, whereas for transformed legacy records (System A), the "Buyer" is the mapped entity. Both are routed to the `customer` key in the database so the Agent can query them seamlessly.
2. **In-Memory Storage:** `INMEMORY_DB` is implemented as a simple Python list. I assumed data persistence across server restarts was not required for the scope of this assessment.
3. **Currency:** The system assumes all monetary values are in a single, unified currency (or currency conversion is handled upstream), as the agent currently aggregates raw numbers without currency conversion logic.
4. **Error Serialization:** Pydantic `ValueError` objects cannot be natively converted to JSON by FastAPI. I assumed that converting the inner error details to standard strings before raising the `HTTP 422` exception is the optimal way to inform the client without causing a `500 Internal Server Error`.

## Future Improvements

If given more time to expand this project for a true production environment, I would implement:

1. **Persistent Database:** Replace the in-memory list with a real database like PostgreSQL (with SQLAlchemy) for transactional data, and Pinecone or Milvus (Vector DB) for semantic search over invoice descriptions.
2. **Authentication & Security:** Add API Key validation or JWT-based authentication for the FastAPI endpoints to secure sensitive financial data.
3. **Robust Retry Logic:** Implement `Tenacity` for automatic retries with exponential backoff on LLM API calls, guarding against transient network failures.
4. **Asynchronous Processing:** Move the `/extract` endpoint to a background task queue (e.g., Celery or FastAPI BackgroundTasks) with webhooks, preventing HTTP timeouts for extremely large invoice texts.
5. **Frontend Dashboard:** Build a React or Streamlit UI for users to upload PDF invoices (incorporating OCR before the LLM step) and chat with the Agent visually.
