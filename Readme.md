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