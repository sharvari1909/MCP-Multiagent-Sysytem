workflow_store = {}


def save_invoice_workflow(
    invoice_id: str,
    email: dict,
    stock: dict,
    invoice: dict,
    approval: dict,
    logs: list | None = None,
    mcp_calls: list | None = None,
    guardrails: list | None = None,
    agents: dict | None = None,
):
    workflow_store[invoice_id] = {
        "email": email,
        "stock": stock,
        "invoice": invoice,
        "approval": approval,
        "client_delivery": None,
        "logs": logs or [],
        "mcp_calls": mcp_calls or [],
        "guardrails": guardrails or [],
        "agents": agents or {},
    }
    return workflow_store[invoice_id]


def save_failed_workflow(
    workflow_id: str,
    email: dict,
    stock: dict | None,
    message: str,
    logs: list,
    mcp_calls: list | None = None,
    guardrails: list | None = None,
    agents: dict | None = None,
):
    workflow_store[workflow_id] = {
        "email": email,
        "stock": stock,
        "invoice": None,
        "approval": {
            "status": "failed",
            "reason": message,
        },
        "client_delivery": None,
        "logs": logs,
        "mcp_calls": mcp_calls or [],
        "guardrails": guardrails or [],
        "agents": agents or {},
    }
    return workflow_store[workflow_id]


def get_invoice_workflow(invoice_id: str):
    return workflow_store.get(invoice_id)


def update_invoice_workflow(invoice_id: str, **updates):
    workflow = workflow_store.get(invoice_id)
    if not workflow:
        return None

    workflow.update(updates)
    return workflow
