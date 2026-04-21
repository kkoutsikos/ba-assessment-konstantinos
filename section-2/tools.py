from langchain_core.tools import tool
from database import INVOICES
from collections import defaultdict
import datetime

@tool
def search_invoices(query: str, date_from: str = None, date_to: str = None) -> list[dict]:
    """Search invoices by customer name, invoice number, status, or keyword."""
    print(f"\n[EXECUTION] search_invoices called with query='{query}'...")
    results = []
    query_lower = query.lower()
    
    for inv in INVOICES:
        
        id_str = inv.get("id") or ""
        cust_str = inv.get("customer") or ""
        status_str = inv.get("status") or ""
        
        if (query_lower in id_str.lower() or 
            query_lower in cust_str.lower() or 
            query_lower in status_str.lower()):
            
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

@tool
def find_top_customers(limit: int = 3) -> str:
    """Finds the top customers based on total gross billing. Useful for revenue analysis."""
    revenue_by_customer = defaultdict(float)
    for invoice in INVOICES:
        cust = invoice.get("customer", "Unknown")
        # Ensure we handle missing or string-based numbers gracefully
        try:
            amount = float(invoice.get("gross_total", 0.0))
        except ValueError:
            amount = 0.0
        revenue_by_customer[cust] += amount
    
    sorted_customers = sorted(revenue_by_customer.items(), key=lambda x: x[1], reverse=True)
    top_list = sorted_customers[:limit]
    
    if not top_list:
        return "No customer data available to rank."
        
    result = [f"{c}: {amt:.2f}" for c, amt in top_list]
    return f"Top {limit} customers by revenue: " + " | ".join(result)

@tool
def get_overdue_invoices(current_date_str: str) -> str:
    """Finds invoices that are past their due date AND are not paid. Expects date format: YYYY-MM-DD."""
    overdue = []
    try:
        current_date = datetime.datetime.strptime(current_date_str, "%Y-%m-%d")
        for inv in INVOICES:
            inv_date_str = inv.get("date")
            status = inv.get("status", "").lower()
            
            if inv_date_str:
                inv_date = datetime.datetime.strptime(inv_date_str, "%Y-%m-%d")
                
                
                if inv_date < current_date and status != "paid":
                    overdue.append(f"ID: {inv.get('id')} ({inv.get('customer')})")
    except ValueError:
        return "Error: Could not parse dates. Please ensure dates are in YYYY-MM-DD format."
    
    if not overdue:
        return "No unpaid overdue invoices found for the specified date."
    return "Overdue unpaid invoices: " + ", ".join(overdue)

@tool
def detect_anomaly(customer: str, current_amount: float) -> str:
    """Checks if a new invoice amount is unusually high compared to historical averages for a customer."""
    past_amounts = []
    for inv in INVOICES:
        if inv.get("customer", "").lower() == customer.lower():
            try:
                past_amounts.append(float(inv.get("gross_total", 0.0)))
            except ValueError:
                continue
                
    if not past_amounts:
        return f"No historical data for '{customer}' to establish a baseline."
    
    average = sum(past_amounts) / len(past_amounts)
    # Define an anomaly as being 200% higher than the average
    if current_amount > average * 2:
        return f"ANOMALY DETECTED: The amount {current_amount} is significantly higher than the historical average of {average:.2f} for {customer}."
    return f"Status Normal: Amount {current_amount} aligns with the average {average:.2f} for {customer}."

@tool
def convert_currency(amount: float, target_currency: str) -> str:
    """Converts an amount to the target currency using mocked standard exchange rates."""
    # Mock rates assuming the base system currency is EUR
    rates = {
        "EUR": 1.0, 
        "USD": 1.08, 
        "GBP": 0.85,
        "JPY": 163.50
    }
    target = target_currency.upper()
    
    if target not in rates:
        return f"Error: Exchange rate for {target} is not currently supported by the system."
    
    converted = amount * rates[target]
    return f"Conversion successful: {amount} EUR is approximately {converted:.2f} {target}."

@tool
def verify_vat_number(vat_id: str) -> str:
    """Verifies if a VAT number format is valid (Mock VIES API check)."""
    # Stripping spaces and standardizing
    clean_vat = vat_id.strip().upper()
    
    # A basic validation: starts with 2 letters (country code) followed by digits
    if len(clean_vat) > 4 and clean_vat[:2].isalpha() and clean_vat[2:].isdigit():
        return f"VIES Check Passed: VAT number {clean_vat} is VALID and active."
    return f"VIES Check Failed: VAT number {clean_vat} has an INVALID format."

agent_tools = [
    search_invoices, 
    get_invoice_details, 
    calculate_total,
    find_top_customers,
    get_overdue_invoices,
    detect_anomaly,
    convert_currency,
    verify_vat_number
]