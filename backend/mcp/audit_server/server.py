from mcp.server.fastmcp import FastMCP
from mcp.audit_server.tools import save_audit_event, get_audit_logs

mcp = FastMCP("Audit MCP Server")


@mcp.tool()
def save_event(event_type: str, payload: dict):
    return save_audit_event(event_type, payload)


@mcp.tool()
def get_logs():
    return get_audit_logs()


if __name__ == "__main__":
    mcp.run()