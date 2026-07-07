import AgentCard from "./AgentCard";

export default function WorkflowCanvas({ agents, mcpCalls, guardrails }) {
  const order = [
    "email",
    "supervisor",
    "inventory",
    "invoice",
    "approval",
  ];

  return (
    <div className="workflow-canvas">
      {order.map((key, index) => (
        <div key={key}>
          <AgentCard
            {...agents[key]}
            toolCalls={mcpCalls.filter((call) => call.agent === agents[key]?.title)}
            guardrails={guardrails.filter((check) => check.agent === agents[key]?.title)}
          />
          {index < order.length - 1 && <div className="connector" />}
        </div>
      ))}
    </div>
  );
}
