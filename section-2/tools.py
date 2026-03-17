from langchain_core.tools import tool
from database import INVOICES

@tool
def search_invoices(query: str, date_from: str = None, date_to: str = None) -> list[dict]:
    """Search invoices by customer name, invoice number, status, or keyword."""
    print(f"\n[EXECUTION] search_invoices called with query='{query}'...")
    results = []
    query_lower = query.lower()
    
    for inv in INVOICES:
        # A simple search checking ID, customer name, and status
        if (query_lower in inv["id"].lower() or 
            query_lower in inv["customer"].lower() or 
            query_lower in inv["status"].lower()):
            
            # Return a summary to save token space
            summary = {k: v for k, v in inv.items() if k != "items"}
            results.append(summary)
            
    return results

@tool
def get_invoice_details(invoice_id: str) -> dict:
    """Get full details for a specific invoice including line items."""
    print(f"\n[EXECUTION] get_invoice_details called for '{invoice_id}'...")
    for inv in INVOICES:
        if inv["id"] == invoice_id:
            return inv
    return {"error": f"Invoice {invoice_id} not found."}

@tool
def calculate_total(invoice_ids: list[str]) -> dict:
    """Calculate net, vat, and gross totals across multiple invoices."""
    print(f"\n[EXECUTION] calculate_total called for {invoice_ids}...")
    net_total = 0.0
    gross_total = 0.0
    
    for inv_id in invoice_ids:
        for inv in INVOICES:
            if inv["id"] == inv_id:
                net_total += inv.get("net_total", 0)
                gross_total += inv.get("gross_total", 0)
                
    return {
        "calculated_net_total": round(net_total, 2),
        "calculated_gross_total": round(gross_total, 2)
    }

agent_tools = [search_invoices, get_invoice_details, calculate_total]