from mcp.email_server.imap_reader import read_unread_emails
from mcp.email_server.smtp_sender import send_smtp_email
from config import settings


def read_inbox_tool(limit=5):
    return {
        "tool": "Email MCP",
        "action": "read_unread_emails",
        "emails": read_unread_emails(limit),
    }


def send_email_tool(to_email, subject, body, attachment_path=None, html_body=None):
    return send_smtp_email(
        to_email=to_email,
        subject=subject,
        body=body,
        attachment_path=attachment_path,
        html_body=html_body,
    )


def send_approval_email_tool(manager_email, invoice_id, amount):
    subject = f"Approval Required: Invoice {invoice_id}"
    approve_url = f"{settings.BACKEND_PUBLIC_URL}/api/approval/approve/{invoice_id}"
    reject_url = f"{settings.BACKEND_PUBLIC_URL}/api/approval/reject/{invoice_id}"

    body = f"""
Hello,

A new invoice approval is required.

Invoice ID: {invoice_id}
Amount: Rs. {amount}

Approve or reject directly from this email, or use the MCP dashboard.

Direct links:
Approve + Send: {approve_url}
Reject: {reject_url}

Regards,
MCP Workflow System
"""

    html_body = f"""
<!doctype html>
<html>
  <body style="margin:0;padding:24px;background:#f8fafc;font-family:Arial,sans-serif;color:#111827;">
    <div style="max-width:620px;margin:auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;padding:24px;">
      <h2 style="margin:0 0 12px;color:#0f172a;">Invoice Approval Required</h2>
      <p>A new invoice is waiting for approval.</p>
      <table style="width:100%;border-collapse:collapse;margin:18px 0;">
        <tr>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;"><b>Invoice ID</b></td>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;">{invoice_id}</td>
        </tr>
        <tr>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;"><b>Amount</b></td>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;">Rs. {amount}</td>
        </tr>
      </table>
      <div style="margin:22px 0;">
        <a href="{approve_url}" style="display:inline-block;background:#047857;color:#ffffff;text-decoration:none;font-weight:700;padding:12px 18px;border-radius:10px;margin-right:10px;">
          Approve + Send Invoice
        </a>
        <a href="{reject_url}" style="display:inline-block;background:#b91c1c;color:#ffffff;text-decoration:none;font-weight:700;padding:12px 18px;border-radius:10px;">
          Reject
        </a>
      </div>
      <p style="font-size:13px;color:#64748b;">If buttons do not work, use these links:</p>
      <p style="font-size:13px;word-break:break-all;">Approve: {approve_url}</p>
      <p style="font-size:13px;word-break:break-all;">Reject: {reject_url}</p>
    </div>
  </body>
</html>
"""

    return send_email_tool(
        to_email=manager_email,
        subject=subject,
        body=body,
        html_body=html_body,
    )


def send_invoice_email_tool(client_email, invoice, attachment_path=None):
    subject = f"Invoice {invoice['invoice_id']} from Anvenssa"

    body = f"""
Hello,

Your invoice has been approved and is attached.

Invoice ID: {invoice['invoice_id']}
Product: {invoice['product']}
Quantity: {invoice['quantity']}
Total: Rs. {invoice['total']}

Regards,
Anvenssa Workflow System
"""

    return send_email_tool(
        to_email=client_email,
        subject=subject,
        body=body,
        attachment_path=attachment_path or invoice.get("pdf_path"),
    )


def send_text_quotation_email_tool(client_email, quote):
    subject = f"Text quotation for {quote['product']} from Anvenssa"

    body = f"""
Hello,

As requested, here is your quotation in text format.

Quotation ID: {quote['invoice_id']}
Product: {quote['product']}
SKU: {quote['sku']}
Quantity: {quote['quantity']}
Unit Price: Rs. {quote['unit_price']}
Subtotal: Rs. {quote['subtotal']}
GST (18%): Rs. {quote['gst']}
Total Amount: Rs. {quote['total']}

Terms & Conditions:
- Prices are subject to final confirmation at order placement.
- Standard GST is included in the total above.
- Delivery timeline will be confirmed after purchase order approval.

Thank you for contacting Anvenssa.

Regards,
Anvenssa Workflow System
"""

    return send_email_tool(
        to_email=client_email,
        subject=subject,
        body=body,
    )


def send_stock_unavailable_email_tool(client_email, product_name, requested_quantity, available_stock):
    subject = f"Stock unavailable: {product_name}"

    body = f"""
Hello,

We received your invoice request for {requested_quantity} {product_name}.

At the moment, only {available_stock} units are available, so we cannot generate the invoice for the requested quantity.

Please reply with a revised quantity or contact the sales team for availability.

Regards,
Anvenssa Workflow System
"""

    return send_email_tool(
        to_email=client_email,
        subject=subject,
        body=body,
    )
