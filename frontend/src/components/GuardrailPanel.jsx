export default function GuardrailPanel({ checks }) {
  return (
    <div className="panel">
      <h3>Guardrails</h3>

      {checks.length === 0 && <p>No guardrails executed yet.</p>}

      {checks.map((check, index) => (
        <div
          key={index}
          className={`guardrail-item ${check.passed ? "pass" : "fail"}`}
        >
          {check.passed ? "PASS" : "FAIL"} {check.name}
        </div>
      ))}
    </div>
  );
}
