from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from logger import log_event
from mcp.approval_server.tools import approve_invoice, reject_invoice, get_approval_status
from mcp.email_server.tools import send_invoice_email_tool
from mcp.invoice_server.pdf_generator import generate_invoice_pdf
from mcp.audit_server.tools import save_audit_event
from agents.workflow_store import get_invoice_workflow, update_invoice_workflow
from websocket import manager
from pathlib import Path

router = APIRouter()


@router.get("/status/{invoice_id}")
def status(invoice_id: str):
    return get_approval_status(invoice_id)


@router.post("/approve/{invoice_id}")
async def approve(invoice_id: str):
    result = _approve_and_send(invoice_id)
    await _broadcast_workflow(invoice_id)
    return result


@router.get("/approve/{invoice_id}", response_class=HTMLResponse)
async def approve_from_email(invoice_id: str):
    result = _approve_and_send(invoice_id)
    await _broadcast_workflow(invoice_id)
    delivery = result.get("client_delivery", {})

    return _approval_page(
        title="Invoice Approved",
        message=f"Invoice {invoice_id} has been approved.",
        detail=f"Client email status: {delivery.get('status', 'unknown')}",
        accent="#047857",
    )


def _approve_and_send(invoice_id: str):
    workflow = get_invoice_workflow(invoice_id)

    if workflow and workflow.get("approval", {}).get("status") == "approved":
        existing_delivery = workflow.get("client_delivery")
        _mark_approval_agent(
            workflow=workflow,
            status="completed",
            context="Manager approved from email/dashboard. Invoice already sent to client.",
            delivery=existing_delivery,
        )
        if existing_delivery:
            return {
                **workflow["approval"],
                "client_delivery": existing_delivery,
                "message": "Invoice was already approved and sent.",
            }

    approval = approve_invoice(invoice_id)

    if not workflow:
        return {
            **approval,
            "client_delivery": {
                "status": "skipped",
                "note": "No workflow data found for this invoice. The invoice may have been created before the server restarted.",
            },
        }

    invoice = workflow["invoice"]
    client_email = invoice["customer_email"]
    attachment_path = _ensure_invoice_pdf(invoice)
    try:
        delivery = send_invoice_email_tool(
            client_email=client_email,
            invoice=invoice,
            attachment_path=attachment_path,
        )
    except Exception as e:
        delivery = {
            "tool": "Email MCP",
            "status": "failed",
            "to": client_email,
            "subject": f"Invoice {invoice['invoice_id']} from Anvenssa",
            "error": str(e),
        }

    _mark_approval_agent(
        workflow=workflow,
        status="completed",
        context="Manager approved. Invoice PDF sent to client.",
        delivery=delivery,
    )
    if delivery.get("status") == "sent":
        workflow.setdefault("logs", []).append(log_event(
            f"Manager approved invoice and client invoice was sent via {delivery.get('provider', 'email')}"
        ))
    else:
        attempted_ports = _format_smtp_attempts(delivery)
        provider_attempts = _format_provider_attempts(delivery)
        workflow.setdefault("logs", []).append(log_event(
            f"Manager approved invoice but client email {delivery.get('status')}: {delivery.get('error') or delivery.get('note', 'unknown email issue')}{attempted_ports}{provider_attempts}",
            "error",
        ))
    update_invoice_workflow(
        invoice_id,
        approval=approval,
        client_delivery=delivery,
        agents=workflow.get("agents", {}),
        mcp_calls=workflow.get("mcp_calls", []),
        guardrails=workflow.get("guardrails", []),
        logs=workflow.get("logs", []),
    )
    save_audit_event("invoice_sent_to_client", {
        "invoice_id": invoice_id,
        "client_email": client_email,
        "delivery": delivery,
    })

    return {
        **approval,
        "client_delivery": delivery,
    }


def _ensure_invoice_pdf(invoice: dict):
    pdf_path = invoice.get("pdf_path")
    if pdf_path and Path(pdf_path).exists():
        return pdf_path

    pdf_path = generate_invoice_pdf(invoice)
    invoice["pdf_path"] = pdf_path
    return pdf_path


def _format_smtp_attempts(delivery):
    attempts = delivery.get("attempts") or []
    if not attempts:
        return ""

    ports = ", ".join(
        f"{attempt.get('port')}={attempt.get('status')}"
        for attempt in attempts
    )
    return f" (SMTP attempts: {ports})"


def _format_provider_attempts(delivery):
    attempts = delivery.get("provider_attempts") or []
    if not attempts:
        return ""

    providers = ", ".join(
        f"{attempt.get('provider', 'smtp')}={attempt.get('status')}"
        for attempt in attempts
    )
    return f" (Provider attempts: {providers})"


@router.post("/reject/{invoice_id}")
async def reject(invoice_id: str):
    result = _reject_invoice(invoice_id)
    await _broadcast_workflow(invoice_id)
    return result


@router.get("/reject/{invoice_id}", response_class=HTMLResponse)
async def reject_from_email(invoice_id: str):
    _reject_invoice(invoice_id)
    await _broadcast_workflow(invoice_id)

    return _approval_page(
        title="Invoice Rejected",
        message=f"Invoice {invoice_id} has been rejected.",
        detail="No invoice was sent to the client.",
        accent="#b91c1c",
    )


def _reject_invoice(invoice_id: str):
    rejection = reject_invoice(invoice_id)
    workflow = get_invoice_workflow(invoice_id)
    if workflow:
        _mark_approval_agent(
            workflow=workflow,
            status="failed",
            context="Manager rejected invoice. No invoice was sent to client.",
            delivery=None,
        )
        workflow.setdefault("logs", []).append(log_event("Manager rejected invoice", "error"))
        update_invoice_workflow(
            invoice_id,
            approval=rejection,
            agents=workflow.get("agents", {}),
            guardrails=workflow.get("guardrails", []),
            logs=workflow.get("logs", []),
        )
    else:
        update_invoice_workflow(invoice_id, approval=rejection)
    return rejection


def _approval_page(title: str, message: str, detail: str, accent: str):
    return f"""
<!doctype html>
<html>
  <head>
    <title>{title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>
  <body style="margin:0;background:#f8fafc;font-family:Arial,sans-serif;color:#111827;">
    <main style="min-height:100vh;display:grid;place-items:center;padding:24px;">
      <section style="max-width:560px;background:white;border:1px solid #e2e8f0;border-radius:16px;padding:28px;box-shadow:0 18px 45px rgba(15,23,42,0.10);">
        <div style="width:56px;height:56px;border-radius:999px;background:{accent};color:white;display:grid;place-items:center;font-size:28px;font-weight:700;margin-bottom:16px;">✓</div>
        <h1 style="margin:0 0 10px;font-size:28px;color:{accent};">{title}</h1>
        <p style="font-size:16px;line-height:1.5;margin:0 0 8px;">{message}</p>
        <p style="font-size:14px;color:#64748b;margin:0;">{detail}</p>
      </section>
    </main>
  </body>
</html>
"""


async def _broadcast_workflow(invoice_id: str):
    workflow = get_invoice_workflow(invoice_id)
    if not workflow:
        return

    await manager.broadcast({
        "type": "workflow_complete",
        "payload": workflow,
    })


def _mark_approval_agent(workflow: dict, status: str, context: str, delivery: dict | None):
    agents = workflow.setdefault("agents", {})
    approval_agent = agents.setdefault("approval", {
        "title": "Approval Agent",
        "status": "pending",
        "tokens": 20,
        "latency": 150,
        "context": "Invoice summary + manager approval rules",
    })
    approval_agent.update({
        "status": status,
        "tokens": max(approval_agent.get("tokens", 0), 45),
        "latency": max(approval_agent.get("latency", 0), 220),
        "context": context,
    })

    mcp_calls = workflow.setdefault("mcp_calls", [])
    if delivery and not _has_call(mcp_calls, "Email MCP", "send_invoice_email"):
        mcp_calls.append({
            "tool": "Email MCP",
            "action": "send_invoice_email",
            "params": workflow.get("invoice", {}).get("customer_email", ""),
            "agent": "Approval Agent",
        })

    guardrails = workflow.setdefault("guardrails", [])
    _upsert_guardrail(guardrails, {
        "name": "Manager approval received",
        "passed": status == "completed",
        "agent": "Approval Agent",
    })

    if delivery:
        _upsert_guardrail(guardrails, {
            "name": "Client invoice email sent",
            "passed": delivery.get("status") == "sent",
            "agent": "Approval Agent",
        })


def _has_call(calls: list, tool: str, action: str):
    return any(call.get("tool") == tool and call.get("action") == action for call in calls)


def _upsert_guardrail(guardrails: list, check: dict):
    for index, existing in enumerate(guardrails):
        if existing.get("agent") == check["agent"] and existing.get("name") == check["name"]:
            guardrails[index] = check
            return

    guardrails.append(check)
