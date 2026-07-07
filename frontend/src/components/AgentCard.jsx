export default function AgentCard({
  title,
  status,
  tokens,
  latency,
  context,
  toolCalls = [],
  guardrails = [],
}) {
  const statusLabel = status || "idle";

  return (
    <div className={`agent-card ${statusLabel}`}>
      <div className="agent-head">
        <div className="agent-title">{title}</div>
        <div className="agent-status">{statusLabel}</div>
      </div>

      <div className="metric-row">
        <div className="mini-metric">
          Tokens
          <strong>{tokens || 0}</strong>
        </div>

        <div className="mini-metric">
          Latency
          <strong>{latency || 0} ms</strong>
        </div>

        <div className="mini-metric">
          Guardrails
          <strong>{statusLabel === "completed" ? "Pass" : statusLabel === "failed" ? "Fail" : "-"}</strong>
        </div>
      </div>

      <div className="context-box">
        <b>Context Window</b>
        <br />
        {context || "Waiting for execution context..."}
      </div>

      <div className="agent-details">
        <b>MCP Tools</b>
        {toolCalls.length === 0 && <span>No MCP tool called yet.</span>}
        {toolCalls.map((call, index) => (
          <span key={`${call.tool}-${call.action}-${index}`}>
            {call.tool}: {call.action}
            {call.params ? ` (${call.params})` : ""}
          </span>
        ))}
      </div>

      <div className="agent-details guardrail-details">
        <b>Guardrails</b>
        {guardrails.length === 0 && <span>No guardrail check yet.</span>}
        {guardrails.map((check, index) => (
          <span key={`${check.name}-${index}`} className={check.passed ? "pass-text" : "fail-text"}>
            {check.passed ? "PASS" : "FAIL"}: {check.name}
          </span>
        ))}
      </div>
    </div>
  );
}
