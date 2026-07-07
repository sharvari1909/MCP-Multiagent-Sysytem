def validate_email_request(email_data: dict):
    checks = []

    checks.append({
        "name": "Sender email present",
        "passed": bool(email_data.get("from")),
    })

    checks.append({
        "name": "Subject present",
        "passed": bool(email_data.get("subject")),
    })

    checks.append({
        "name": "Body present",
        "passed": bool(email_data.get("body")),
    })

    return checks


def validate_inventory(stock_result: dict):
    return [
        {
            "name": "Product found",
            "passed": bool(stock_result.get("product")),
        },
        {
            "name": "Stock available",
            "passed": bool(stock_result.get("available")),
        },
    ]


def validate_invoice(invoice: dict):
    return [
        {
            "name": "Invoice number generated",
            "passed": bool(invoice.get("invoice_id")),
        },
        {
            "name": "Amount calculated",
            "passed": invoice.get("total", 0) > 0,
        },
    ]