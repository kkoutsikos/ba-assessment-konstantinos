from pydantic import BaseModel, Field, model_validator
from typing import List
from datetime import date
from decimal import Decimal

class AddressInfo(BaseModel):
    name: str = Field(description="Το πλήρες όνομα της εταιρείας/οντότητας")
    street: str
    zip_code: str
    city: str
    vat_id: str

class InvoiceItem(BaseModel):
    pos: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    total: Decimal

    @model_validator(mode='after')
    def validate_line_total(self) -> 'InvoiceItem':
        
        expected = round(self.quantity * self.unit_price, 2)
        if abs(self.total - expected) > Decimal('0.01'):
            raise ValueError(f"Σφάλμα υπολογισμού στη θέση {self.pos}: {self.quantity} * {self.unit_price} != {self.total}")
        return self

class Invoice(BaseModel):
    invoice_number: str
    date: date
    seller: AddressInfo
    buyer: AddressInfo
    items: List[InvoiceItem]
    net_amount: Decimal
    vat_rate: Decimal = Field(description="Ο συντελεστής ΦΠΑ όπως αναγράφεται στο τιμολόγιο (π.χ. 19.0)")
    vat_amount: Decimal
    gross_amount: Decimal
    payment_terms: str
    iban: str

    @model_validator(mode='after')
    def validate_invoice_totals(self) -> 'Invoice':
        # 1. Επαλήθευση ότι το άθροισμα των γραμμών συμφωνεί με το καθαρό ποσό [cite: 39]
        calculated_net = sum(item.total for item in self.items)
        if abs(self.net_amount - calculated_net) > Decimal('0.01'):
            raise ValueError(f"Ασυμφωνία καθαρού ποσού: {self.net_amount} != άθροισμα γραμμών {calculated_net}")
        
        # 2. Δυναμικός έλεγχος ΦΠΑ βάσει του εξαχθέντος vat_rate [cite: 32, 40]
        expected_vat = round(self.net_amount * (self.vat_rate / Decimal('100')), 2)
        if abs(self.vat_amount - expected_vat) > Decimal('0.01'):
            raise ValueError(f"Λάθος υπολογισμός ΦΠΑ: Αναμενόμενο {expected_vat} βάσει συντελεστή {self.vat_rate}%")
            
        # 3. Έλεγχος μικτού ποσού [cite: 33, 39]
        expected_gross = round(self.net_amount + self.vat_amount, 2)
        if abs(self.gross_amount - expected_gross) > Decimal('0.01'):
            raise ValueError(f"Ασυμφωνία μικτού ποσού: {self.gross_amount} != {self.net_amount} + {self.vat_amount}")
        return self