from mcp.server.fastmcp import FastMCP
from mcp.invoice_server.tools import generate_invoice_tool

mcp = FastMCP("Invoice MCP Server")


@mcp.tool()
def generate_invoice(product: dict, quantity: int, customer_email: str):
    return generate_invoice_tool(
        product=product,
        quantity=quantity,
        customer_email=customer_email,
    )


if __name__ == "__main__":
    mcp.run()