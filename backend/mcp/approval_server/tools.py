approval_store = {}


def create_approval_request(invoice_id: str, manager_email: str, amount: float):
    approval_store[invoice_id] = {
        "invoice_id": invoice_id,
        "manager_email": manager_email,
        "amount": amount,
        "status": "pending",
    }

    return {
        "tool": "Approval MCP",
        "status": "pending",
        "invoice_id": invoice_id,
        "manager_email": manager_email,
        "amount": amount,
    }


def approve_invoice(invoice_id: str):
    if invoice_id in approval_store:
        approval_store[invoice_id]["status"] = "approved"
        return approval_store[invoice_id]

    approval_store[invoice_id] = {
        "invoice_id": invoice_id,
        "status": "approved",
    }
    return approval_store[invoice_id]


def reject_invoice(invoice_id: str):
    if invoice_id in approval_store:
        approval_store[invoice_id]["status"] = "rejected"
        return approval_store[invoice_id]

    approval_store[invoice_id] = {
        "invoice_id": invoice_id,
        "status": "rejected",
    }
    return approval_store[invoice_id]


def get_approval_status(invoice_id: str):
    return approval_store.get(
        invoice_id,
        {
            "invoice_id": invoice_id,
            "status": "not_found",
        },
    )