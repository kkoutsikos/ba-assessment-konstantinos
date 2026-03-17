INVOICES = [
    {
        "id": "INV-001", 
        "customer": "Digital Services AG",
        "date": "2024-01-15", 
        "net_total": 2500.00, 
        "vat_rate": 0.19,
        "vat_amount": 475.00, 
        "gross_total": 2975.00, 
        "status": "paid",
        "items": [
            {"description": "Cloud Hosting Q1", "quantity": 1, "unit_price": 1500.00, "total": 1500.00},
            {"description": "Support Hours", "quantity": 10, "unit_price": 100.00, "total": 1000.00}
        ]
    },
    {
        "id": "INV-002", 
        "customer": "Digital Services AG",
        "date": "2024-04-15", 
        "net_total": 3200.00, 
        "gross_total": 3808.00,
        "status": "pending",
        "items": [
            {"description": "Custom Development", "quantity": 1, "unit_price": 3200.00, "total": 3200.00}
        ]
    },
    {
        "id": "INV-003", 
        "customer": "Munchen Logistics GmbH",
        "date": "2024-03-01", 
        "net_total": 8500.00, 
        "gross_total": 10115.00,
        "status": "overdue",
        "items": [
            {"description": "Logistics Software License", "quantity": 1, "unit_price": 6500.00, "total": 6500.00},
            {"description": "On-site Training", "quantity": 2, "unit_price": 1000.00, "total": 2000.00}
        ]
    },
    {
        "id": "INV-004", 
        "customer": "Berlin Startup Hub",
        "date": "2024-02-20", 
        "net_total": 1200.00, 
        "gross_total": 1428.00,
        "status": "paid",
        "items": [
            {"description": "Consulting", "quantity": 8, "unit_price": 150.00, "total": 1200.00}
        ]
    }
]