export default function EmailPanel({ email }) {
  return (
    <div className="panel">
      <h3>Incoming Email</h3>

      {!email && <p>No email processed yet.</p>}

      {email && (
        <>
          <p><b>From:</b> {email.from}</p>
          <p><b>To:</b> {email.to}</p>
          <p><b>Subject:</b> {email.subject}</p>
          <textarea className="email-body" value={email.body} readOnly />
        </>
      )}
    </div>
  );
}
