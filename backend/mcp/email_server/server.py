from mcp.server.fastmcp import FastMCP
from mcp.email_server.tools import (
    read_inbox_tool,
    send_email_tool,
    send_approval_email_tool,
)

mcp = FastMCP("Email MCP Server")


@mcp.tool()
def read_unread_emails(limit: int = 5):
    return read_inbox_tool(limit)


@mcp.tool()
def send_email(
    to_email: str,
    subject: str,
    body: str,
    attachment_path: str | None = None,
):
    return send_email_tool(
        to_email=to_email,
        subject=subject,
        body=body,
        attachment_path=attachment_path,
    )


@mcp.tool()
def send_approval_email(
    manager_email: str,
    invoice_id: str,
    amount: float,
):
    return send_approval_email_tool(
        manager_email=manager_email,
        invoice_id=invoice_id,
        amount=amount,
    )


if __name__ == "__main__":
    mcp.run()