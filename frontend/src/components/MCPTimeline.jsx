export default function MCPTimeline({ events }) {
  return (
    <div className="panel">
      <h3>MCP Tool Calls</h3>

      {events.length === 0 && <p>No MCP calls yet.</p>}

      {events.map((event, index) => (
        <div className="timeline-item tool-call" key={`${event.tool}-${event.action}-${index}`}>
          <span className="tool-index">{index + 1}</span>
          <div>
            <strong>{event.tool}</strong>
            <span>{event.action}</span>
            {event.params && <small>{event.params}</small>}
          </div>
        </div>
      ))}
    </div>
  );
}
