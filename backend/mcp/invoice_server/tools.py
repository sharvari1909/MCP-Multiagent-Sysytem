from utils import generate_invoice_number
from mcp.invoice_server.pdf_generator import generate_invoice_pdf


def calculate_invoice(product, quantity, customer_email):
    subtotal = product["price"] * quantity
    gst = round(subtotal * 0.18, 2)
    total = round(subtotal + gst, 2)

    invoice = {
        "invoice_id": generate_invoice_number(),
        "customer_email": customer_email,
        "product": product["name"],
        "sku": product["sku"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal,
        "gst": gst,
        "total": total,
    }

    return invoice


def generate_invoice_tool(product, quantity, customer_email):
    invoice = calculate_invoice(product, quantity, customer_email)
    pdf_path = generate_invoice_pdf(invoice)

    invoice["pdf_path"] = pdf_path

    return {
        "tool": "Invoice MCP",
        "status": "generated",
        "invoice": invoice,
    }