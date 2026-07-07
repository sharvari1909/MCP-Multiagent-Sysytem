import { useState } from "react";

import api from "../services/api";

export default function ApprovalPanel({ approval, invoice, onApprovalChange }) {
  const [delivery, setDelivery] = useState(null);
  const [busy, setBusy] = useState(false);
  const textQuoteSent = invoice?.quote_format === "text" || approval?.status === "not_required";

  const approveInvoice = async () => {
    if (!invoice) return;

    setBusy(true);
    try {
      const res = await api.post(`/approval/approve/${invoice.invoice_id}`);
      onApprovalChange?.(res.data);
      setDelivery(res.data.client_delivery);
    } finally {
      setBusy(false);
    }
  };

  const rejectInvoice = async () => {
    if (!invoice) return;

    setBusy(true);
    try {
      const res = await api.post(`/approval/reject/${invoice.invoice_id}`);
      onApprovalChange?.(res.data);
      setDelivery(null);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="panel">
      <h3>Approval + Invoice</h3>

      {!invoice && approval?.status !== "failed" && <p>No invoice generated yet.</p>}

      {!invoice && approval?.status === "failed" && (
        <div className="invoice-card">
          <p><b>Status:</b> Failed</p>
          <p><b>Reason:</b> {approval.reason}</p>
        </div>
      )}

      {invoice && (
        <div className="invoice-card">
          <p><b>{textQuoteSent ? "Quotation" : "Invoice"}:</b> {invoice.invoice_id}</p>
          <p><b>Customer:</b> {invoice.customer_email}</p>
          <p><b>Product:</b> {invoice.product}</p>
          <p><b>Quantity:</b> {invoice.quantity}</p>
          {textQuoteSent && <p><b>Format:</b> Text email, no PDF attachment</p>}
          <p className="amount">Rs. {invoice.total}</p>
        </div>
      )}

      <br />

      <p><b>Approval Status:</b> {approval?.status || "Waiting"}</p>
      <p><b>Manager:</b> {approval?.manager_email || "sharvari@anvenssa.com"}</p>
      {approval?.reason && <p><b>Reason:</b> {approval.reason}</p>}

      {invoice && !textQuoteSent && approval?.status !== "approved" && approval?.status !== "rejected" && (
        <div className="approval-actions">
          <button className="approve-btn" onClick={approveInvoice} disabled={busy}>
            Approve + Send
          </button>
          <button className="reject-btn" onClick={rejectInvoice} disabled={busy}>
            Reject
          </button>
        </div>
      )}

      {delivery && (
        <p><b>Client Email:</b> {delivery.status} to {delivery.to}</p>
      )}
    </div>
  );
}
