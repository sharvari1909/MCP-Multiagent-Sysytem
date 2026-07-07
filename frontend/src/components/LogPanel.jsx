export default function LogPanel({ logs }) {
  return (
    <div className="panel">
      <h3>Execution Logs</h3>

      {logs.length === 0 && <p>No logs yet.</p>}

      {logs.map((log, index) => (
        <div className="log-item" key={index}>
          <strong>{log.timestamp}</strong>
          <span> [{log.level}] {log.message}</span>
        </div>
      ))}
    </div>
  );
}
