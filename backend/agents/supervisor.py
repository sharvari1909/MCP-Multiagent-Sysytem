from config import settings
from logger import log_event
from websocket import manager

from agents.email_parser import (
    extract_email_address,
    parse_invoice_request,
    wants_text_quotation,
)
from agents.metrics import token_estimate
from agents.guardrails import (
    validate_email_request,
    validate_inventory,
    validate_invoice,
)
from agents.workflow_store import (
    save_failed_workflow,
    save_invoice_workflow,
    update_invoice_workflow,
)

from mcp.inventory_server.tools import check_stock
from mcp.invoice_server.tools import calculate_invoice, generate_invoice_tool
from mcp.approval_server.tools import create_approval_request
from mcp.email_server.tools import (
    read_inbox_tool,
    send_approval_email_tool,
    send_stock_unavailable_email_tool,
    send_text_quotation_email_tool,
)
from mcp.audit_server.tools import save_audit_event


async def emit(event_type: str, payload: dict):
    await manager.broadcast({
        "type": event_type,
        "payload": payload,
    })


async def run_invoice_workflow_from_email(email_data: dict):
    logs = []
    mcp_calls = []
    guardrails = []
    agents = _initial_agent_snapshot()

    await emit("agent_status", {
        "agent": "Email Agent",
        "status": "running",
    })
    _set_agent(agents, "email", "running")

    logs.append(log_event("Email MCP received customer request"))
    save_audit_event("email_received", email_data)

    email_guardrails = validate_email_request(email_data)
    email_guardrails = _tag_items(email_guardrails, "Email Agent")
    guardrails.extend(email_guardrails)
    await emit("guardrails", {
        "agent": "Email Agent",
        "checks": email_guardrails,
    })
    _set_agent(agents, "email", "completed")
    await emit("agent_status", {
        "agent": "Email Agent",
        "status": "completed",
        "tokens": token_estimate(email_data.get("body", "")),
        "latency_ms": 90,
        "context_window": "Customer email headers + message body",
    })

    await emit("agent_status", {
        "agent": "Supervisor Agent",
        "status": "running",
        "tokens": token_estimate(email_data.get("body", "")),
        "context_window": "Email + customer + workflow policy",
    })
    _set_agent(
        agents,
        "supervisor",
        "running",
        tokens=token_estimate(email_data.get("body", "")),
        latency=120,
        context="Email + customer + workflow policy",
    )

    request = parse_invoice_request(email_data)
    if not request:
        logs.append(log_event("No matching inventory product found in email", "error"))
        _set_agent(agents, "supervisor", "failed")
        workflow = save_failed_workflow(
            workflow_id=f"FAILED-{email_data.get('id', 'unknown')}",
            email=email_data,
            stock=None,
            message="No matching inventory product found in email",
            logs=logs,
            mcp_calls=mcp_calls,
            guardrails=guardrails,
            agents=agents,
        )
        await emit("workflow_complete", workflow)
        return {
            "status": "failed",
            "message": "No matching inventory product found in email",
            "email": email_data,
            "logs": logs,
        }

    logs.append(log_event("Supervisor classified request as invoice request"))
    _set_agent(agents, "supervisor", "completed")
    await emit("agent_status", {
        "agent": "Supervisor Agent",
        "status": "completed",
        "tokens": token_estimate(email_data.get("body", "")),
        "latency_ms": 120,
        "context_window": "Matched product + quantity from customer email",
    })

    inventory_call = {
        "tool": "Inventory MCP",
        "action": "check_stock",
        "params": f"{request['sku']} x {request['quantity']}",
        "agent": "Inventory Agent",
    }
    mcp_calls.append(inventory_call)
    await emit("mcp_call", inventory_call)

    _set_agent(
        agents,
        "inventory",
        "running",
        tokens=80,
        latency=180,
        context="Inventory JSON + requested item",
    )
    await emit("agent_status", {
        "agent": "Inventory Agent",
        "status": "running",
        "tokens": 80,
        "latency_ms": 180,
        "context_window": "Inventory JSON + requested item",
    })

    stock_result = check_stock(request["sku"], request["quantity"])

    inventory_status = "completed" if stock_result.get("available") else "failed"
    _set_agent(agents, "inventory", inventory_status)
    await emit("agent_status", {
        "agent": "Inventory Agent",
        "status": inventory_status,
        "tokens": 80,
        "latency_ms": 180,
        "context_window": "Inventory JSON + requested item",
    })

    inventory_guardrails = validate_inventory(stock_result)
    inventory_guardrails = _tag_items(inventory_guardrails, "Inventory Agent")
    guardrails.extend(inventory_guardrails)
    await emit("guardrails", {
        "agent": "Inventory Agent",
        "checks": inventory_guardrails,
    })

    if not stock_result.get("available"):
        product = stock_result.get("product", {})
        client_email = extract_email_address(email_data.get("from", ""))
        message = (
            f"Requested quantity {request['quantity']} is not available for "
            f"{product.get('name', request['sku'])}. Available stock: "
            f"{stock_result.get('available_stock', 0)}."
        )
        logs.append(log_event(message, "error"))

        try:
            stock_email = send_stock_unavailable_email_tool(
                client_email=client_email,
                product_name=product.get("name", request["sku"]),
                requested_quantity=request["quantity"],
                available_stock=stock_result.get("available_stock", 0),
            )
        except Exception as e:
            stock_email = {
                "status": "failed",
                "error": str(e),
            }

        workflow = save_failed_workflow(
            workflow_id=f"FAILED-{email_data.get('id', request['sku'])}",
            email=email_data,
            stock=stock_result,
            message=message,
            logs=logs,
            mcp_calls=mcp_calls,
            guardrails=guardrails,
            agents=agents,
        )
        workflow["client_delivery"] = stock_email
        save_audit_event("stock_unavailable", {
            "email": email_data,
            "stock": stock_result,
            "client_delivery": stock_email,
        })
        await emit("workflow_complete", workflow)

        return {
            "status": "failed",
            "message": message,
            "email": email_data,
            "stock": stock_result,
            "client_delivery": stock_email,
            "logs": logs,
        }

    client_email = extract_email_address(email_data.get("from", ""))

    if wants_text_quotation(email_data):
        quote_call = {
            "tool": "Invoice MCP",
            "action": "calculate_text_quotation",
            "params": f"{stock_result['product']['sku']} x {request['quantity']}",
            "agent": "Invoice Agent",
        }
        mcp_calls.append(quote_call)
        await emit("mcp_call", quote_call)

        _set_agent(
            agents,
            "invoice",
            "running",
            tokens=160,
            latency=190,
            context="Customer + product + GST rules + text-only request",
        )
        await emit("agent_status", {
            "agent": "Invoice Agent",
            "status": "running",
            "tokens": 160,
            "latency_ms": 190,
            "context_window": "Customer + product + GST rules + text-only request",
        })

        quote = calculate_invoice(
            product=stock_result["product"],
            quantity=request["quantity"],
            customer_email=client_email,
        )
        quote["quote_format"] = "text"
        quote["pdf_path"] = None

        invoice_guardrails = validate_invoice(quote)
        invoice_guardrails.append({
            "name": "PDF skipped only because customer requested text quotation",
            "passed": True,
        })
        invoice_guardrails = _tag_items(invoice_guardrails, "Invoice Agent")
        guardrails.extend(invoice_guardrails)
        await emit("guardrails", {
            "agent": "Invoice Agent",
            "checks": invoice_guardrails,
        })

        _set_agent(
            agents,
            "invoice",
            "completed",
            tokens=160,
            latency=190,
            context="Text quotation calculated; PDF generation skipped",
        )
        await emit("agent_status", {
            "agent": "Invoice Agent",
            "status": "completed",
            "tokens": 160,
            "latency_ms": 190,
            "context_window": "Text quotation calculated; PDF generation skipped",
        })

        email_call = {
            "tool": "Email MCP",
            "action": "send_text_quotation_email",
            "params": client_email,
            "agent": "Email Agent",
        }
        mcp_calls.append(email_call)
        await emit("mcp_call", email_call)

        try:
            text_delivery = send_text_quotation_email_tool(
                client_email=client_email,
                quote=quote,
            )
        except Exception as e:
            text_delivery = {
                "status": "failed",
                "error": str(e),
                "note": "Check SMTP credentials in .env",
            }

        approval = {
            "status": "not_required",
            "reason": "Customer explicitly requested a text quotation.",
            "manager_email": settings.MANAGER_EMAIL,
        }
        approval_guardrails = _tag_items([
            {
                "name": "Manager approval bypass allowed for text-only quotation",
                "passed": True,
            }
        ], "Approval Agent")
        guardrails.extend(approval_guardrails)
        await emit("guardrails", {
            "agent": "Approval Agent",
            "checks": approval_guardrails,
        })
        _set_agent(
            agents,
            "approval",
            "completed",
            tokens=15,
            latency=60,
            context="No approval required because no PDF invoice is issued",
        )
        await emit("agent_status", {
            "agent": "Approval Agent",
            "status": "completed",
            "tokens": 15,
            "latency_ms": 60,
            "context_window": "No approval required because no PDF invoice is issued",
        })

        logs.append(log_event("Text quotation sent to customer without PDF attachment"))
        save_audit_event("text_quotation_sent", {
            "email": email_data,
            "quote": quote,
            "client_delivery": text_delivery,
        })

        workflow = save_invoice_workflow(
            invoice_id=quote["invoice_id"],
            email=email_data,
            stock=stock_result,
            invoice=quote,
            approval=approval,
            logs=logs,
            mcp_calls=mcp_calls,
            guardrails=guardrails,
            agents=agents,
        )
        workflow["client_delivery"] = text_delivery

        await emit("workflow_complete", workflow)

        return {
            "status": "text_quotation_sent",
            "message": "Text quotation sent to customer without PDF attachment",
            **workflow,
        }

    invoice_call = {
        "tool": "Invoice MCP",
        "action": "generate_invoice",
        "params": f"{stock_result['product']['sku']} x {request['quantity']}",
        "agent": "Invoice Agent",
    }
    mcp_calls.append(invoice_call)
    await emit("mcp_call", invoice_call)
    _set_agent(
        agents,
        "invoice",
        "running",
        tokens=210,
        latency=240,
        context="Customer + product + GST rules",
    )
    await emit("agent_status", {
        "agent": "Invoice Agent",
        "status": "running",
        "tokens": 210,
        "latency_ms": 240,
        "context_window": "Customer + product + GST rules",
    })

    invoice_result = generate_invoice_tool(
        product=stock_result["product"],
        quantity=request["quantity"],
        customer_email=client_email,
    )

    invoice = invoice_result["invoice"]

    _set_agent(agents, "invoice", "completed")
    await emit("agent_status", {
        "agent": "Invoice Agent",
        "status": "completed",
        "tokens": 210,
        "latency_ms": 240,
        "context_window": "Customer + product + GST rules",
    })

    invoice_guardrails = validate_invoice(invoice)
    invoice_guardrails = _tag_items(invoice_guardrails, "Invoice Agent")
    guardrails.extend(invoice_guardrails)
    await emit("guardrails", {
        "agent": "Invoice Agent",
        "checks": invoice_guardrails,
    })

    save_audit_event("invoice_generated", invoice)

    approval_call = {
        "tool": "Approval MCP",
        "action": "create_approval_request",
        "params": invoice["invoice_id"],
        "agent": "Approval Agent",
    }
    mcp_calls.append(approval_call)
    await emit("mcp_call", approval_call)

    approval = create_approval_request(
        invoice_id=invoice["invoice_id"],
        manager_email=settings.MANAGER_EMAIL,
        amount=invoice["total"],
    )

    save_invoice_workflow(
        invoice_id=invoice["invoice_id"],
        email=email_data,
        stock=stock_result,
        invoice=invoice,
        approval=approval,
        logs=logs,
        mcp_calls=mcp_calls,
        guardrails=guardrails,
        agents=agents,
    )

    approval_email_call = {
        "tool": "Email MCP",
        "action": "send_approval_email",
        "params": settings.MANAGER_EMAIL,
        "agent": "Approval Agent",
    }
    mcp_calls.append(approval_email_call)
    await emit("mcp_call", approval_email_call)

    try:
        approval_email = send_approval_email_tool(
            manager_email=settings.MANAGER_EMAIL,
            invoice_id=invoice["invoice_id"],
            amount=invoice["total"],
        )
    except Exception as e:
        approval_email = {
            "status": "failed",
            "error": str(e),
            "note": "Check SMTP credentials in .env",
        }

    _set_agent(
        agents,
        "approval",
        "pending",
        tokens=20,
        latency=150,
        context="Invoice summary + manager approval rules",
    )
    await emit("agent_status", {
        "agent": "Approval Agent",
        "status": "pending",
        "tokens": 20,
        "context_window": "Invoice summary + manager approval rules",
    })

    approval_email_status = approval_email.get("status")
    if approval_email_status == "sent":
        logs.append(log_event(f"Approval request sent to manager via {approval_email.get('provider', 'email')}"))
    else:
        attempted_ports = _format_smtp_attempts(approval_email)
        provider_attempts = _format_provider_attempts(approval_email)
        logs.append(log_event(
            f"Approval email {approval_email_status}: {approval_email.get('error') or approval_email.get('note', 'unknown email issue')}{attempted_ports}{provider_attempts}",
            "error",
        ))

    guardrails.append({
        "name": "Dashboard approval active",
        "passed": True,
        "agent": "Approval Agent",
    })
    guardrails.append({
        "name": "Approval email sent to manager",
        "passed": approval_email_status == "sent",
        "agent": "Approval Agent",
    })

    save_audit_event("approval_requested", approval)
    update_invoice_workflow(
        invoice["invoice_id"],
        approval_email=approval_email,
        logs=logs,
        mcp_calls=mcp_calls,
        guardrails=guardrails,
        agents=agents,
    )

    payload = {
        "email": email_data,
        "stock": stock_result,
        "invoice": invoice,
        "approval": approval,
        "approval_email": approval_email,
        "logs": logs,
        "mcp_calls": mcp_calls,
        "guardrails": guardrails,
        "agents": agents,
    }

    await emit("workflow_complete", payload)

    return {
        "status": "pending_approval",
        "message": "Invoice generated and sent to manager for approval",
        **payload,
    }


async def run_demo_workflow():
    demo_email = {
        "from": "customer@example.com",
        "to": "web@anvenssa.com",
        "subject": "Need invoice for Industrial Pump",
        "body": "Hello, please send invoice for 2 Industrial Pumps.",
    }

    return await run_invoice_workflow_from_email(demo_email)


async def process_unread_invoice_emails(limit=5):
    inbox = read_inbox_tool(limit=limit)
    results = []

    for email_data in inbox.get("emails", []):
        if _should_skip_email(email_data):
            continue

        result = await run_invoice_workflow_from_email(email_data)
        results.append(result)

    return {
        "status": "processed",
        "count": len(results),
        "results": results,
    }


def _should_skip_email(email_data: dict):
    sender = email_data.get("from", "").lower()
    subject = email_data.get("subject", "").lower()
    body = email_data.get("body", "").lower()
    combined = f"{subject} {body}"

    if "mailer-daemon" in sender or "undelivered mail" in subject:
        return True

    invoice_words = ["invoice", "quotation", "quote", "bill"]
    return not any(word in combined for word in invoice_words)


def _initial_agent_snapshot():
    return {
        "email": {
            "title": "Email Agent",
            "status": "idle",
            "tokens": 0,
            "latency": 0,
            "context": "Waiting for customer email from web@anvenssa.com",
        },
        "supervisor": {
            "title": "Supervisor Agent",
            "status": "idle",
            "tokens": 0,
            "latency": 0,
            "context": "Waiting to classify task and delegate agents",
        },
        "inventory": {
            "title": "Inventory Agent",
            "status": "idle",
            "tokens": 0,
            "latency": 0,
            "context": "Waiting to call Inventory MCP",
        },
        "invoice": {
            "title": "Invoice Agent",
            "status": "idle",
            "tokens": 0,
            "latency": 0,
            "context": "Waiting to generate invoice PDF",
        },
        "approval": {
            "title": "Approval Agent",
            "status": "idle",
            "tokens": 0,
            "latency": 0,
            "context": "Waiting to send approval request",
        },
    }


def _set_agent(agents, key, status, tokens=None, latency=None, context=None):
    agents[key]["status"] = status

    if tokens is not None:
        agents[key]["tokens"] = tokens

    if latency is not None:
        agents[key]["latency"] = latency

    if context is not None:
        agents[key]["context"] = context


def _tag_items(items, agent):
    return [{**item, "agent": agent} for item in items]


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
