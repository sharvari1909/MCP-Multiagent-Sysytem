export default function MetricsPanel({ agents, mcpCalls, email, stock, invoice, approval }) {
  const agentList = Object.values(agents);
  const totalTokens = agentList.reduce((sum, agent) => sum + (agent.tokens || 0), 0);
  const completed = agentList.filter((agent) => agent.status === "completed").length;
  const activeAgent = agentList.find((agent) => agent.status === "running");
  const failedAgent = agentList.find((agent) => agent.status === "failed");

  const workflowStatus =
    approval?.status === "failed"
      ? "Needs attention"
      : approval?.status === "approved"
        ? "Approved"
        : approval?.status === "pending"
          ? "Pending approval"
          : email
            ? "Processing"
            : "Waiting";

  return (
    <div className="panel metrics-panel">
      <h3>Live Workflow Metrics</h3>

      <div className="metric-grid">
        <div className="metric-tile accent-blue">
          <span>Status</span>
          <strong>{workflowStatus}</strong>
        </div>
        <div className="metric-tile accent-green">
          <span>Tokens</span>
          <strong>{totalTokens}</strong>
        </div>
        <div className="metric-tile accent-orange">
          <span>MCP Calls</span>
          <strong>{mcpCalls.length}</strong>
        </div>
        <div className="metric-tile accent-pink">
          <span>Agents Done</span>
          <strong>{completed}/5</strong>
        </div>
      </div>

      <div className="timeline-item highlight-item">
        <b>Current Agent:</b>{" "}
        {failedAgent?.title || activeAgent?.title || "No agent running"}
      </div>

      {email && (
        <div className="timeline-item">
          <b>Mail:</b> {email.subject}
          <span>{email.from}</span>
        </div>
      )}

      {stock && (
        <div className={`timeline-item ${stock.available ? "ok-item" : "warn-item"}`}>
          <b>Inventory:</b> {stock.product?.name || stock.sku}
          <span>
            requested {stock.requested_quantity}, available {stock.available_stock}
          </span>
        </div>
      )}

      {invoice && (
        <div className="timeline-item ok-item">
          <b>Invoice:</b> {invoice.invoice_id}
          <span>Rs. {invoice.total}</span>
        </div>
      )}
    </div>
  );
}
