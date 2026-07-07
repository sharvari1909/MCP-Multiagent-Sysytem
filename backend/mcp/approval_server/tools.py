from config import settings


approval_store = {}


def build_approval_links(invoice_id: str):
    base_url = settings.BACKEND_PUBLIC_URL.rstrip("/")
    return {
        "approve_url": f"{base_url}/api/approval/approve/{invoice_id}",
        "reject_url": f"{base_url}/api/approval/reject/{invoice_id}",
    }


def build_approval_channels(invoice_id: str, manager_email: str):
    links = build_approval_links(invoice_id)
    return {
        "dashboard": {
            "status": "active",
            "label": "Dashboard approval",
        },
        "email": {
            "status": "active",
            "label": "Manager email approval",
            "to": manager_email,
            **links,
        },
    }


def create_approval_request(invoice_id: str, manager_email: str, amount: float):
    channels = build_approval_channels(invoice_id, manager_email)
    approval_store[invoice_id] = {
        "invoice_id": invoice_id,
        "manager_email": manager_email,
        "amount": amount,
        "status": "pending",
        "channels": channels,
    }

    return {
        "tool": "Approval MCP",
        "status": "pending",
        "invoice_id": invoice_id,
        "manager_email": manager_email,
        "amount": amount,
        "channels": channels,
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
