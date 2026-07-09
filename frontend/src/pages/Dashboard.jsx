import { useEffect, useState } from "react";

import api from "../services/api";
import ws from "../services/websocket";

import WorkflowCanvas from "../components/WorkflowCanvas";
import EmailPanel from "../components/EmailPanel";
import MetricsPanel from "../components/MetricsPanel";
import MCPTimeline from "../components/MCPTimeline";
import GuardrailPanel from "../components/GuardrailPanel";
import LogPanel from "../components/LogPanel";
import InventoryTable from "../components/InventoryTable";
import ApprovalPanel from "../components/ApprovalPanel";

const initialAgents = {
  email: {
    title: "Email Agent",
    status: "idle",
    tokens: 0,
    latency: 0,
    context: "Waiting for customer email from web@anvenssa.com",
  },
  supervisor: {
    title: "Supervisor Agent",
    status: "idle",
    tokens: 0,
    latency: 0,
    context: "Waiting to classify task and delegate agents",
  },
  inventory: {
    title: "Inventory Agent",
    status: "idle",
    tokens: 0,
    latency: 0,
    context: "Waiting to call Inventory MCP",
  },
  invoice: {
    title: "Invoice Agent",
    status: "idle",
    tokens: 0,
    latency: 0,
    context: "Waiting to generate invoice PDF",
  },
  approval: {
    title: "Approval Agent",
    status: "idle",
    tokens: 0,
    latency: 0,
    context: "Waiting to send approval request",
  },
};

export default function Dashboard() {
  const [agents, setAgents] = useState(initialAgents);
  const [email, setEmail] = useState(null);
  const [mcpCalls, setMcpCalls] = useState([]);
  const [guardrails, setGuardrails] = useState([]);
  const [logs, setLogs] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [invoice, setInvoice] = useState(null);
  const [approval, setApproval] = useState(null);
  const [approvalEmail, setApprovalEmail] = useState(null);
  const [stock, setStock] = useState(null);

  useEffect(() => {
    loadInventory();
    loadLatestWorkflow();

    ws.connect((data) => {
      handleSocketEvent(data);
    });

    const workflowRefresh = window.setInterval(loadLatestWorkflow, 5000);
    return () => window.clearInterval(workflowRefresh);
  }, []);

  const loadInventory = async () => {
    try {
      const res = await api.get("/inventory/");
      setInventory(res.data || []);
    } catch (error) {
      console.error("Failed to load inventory:", error);
    }
  };

  const loadLatestWorkflow = async () => {
    try {
      const res = await api.get("/invoice/workflows");
      const workflows = res.data || [];
      const latest = workflows[workflows.length - 1];

      if (!latest) return;

      setEmail(latest.email || null);
      setStock(latest.stock || null);
      setInvoice(latest.invoice || null);
      setApproval(latest.approval || null);
      setApprovalEmail(latest.approval_email || null);
      setAgents({
        ...initialAgents,
        ...(latest.agents || {}),
      });
      setMcpCalls(latest.mcp_calls || []);
      setGuardrails(latest.guardrails || []);
      setLogs(latest.logs || []);
    } catch (error) {
      console.error("Failed to load latest workflow:", error);
    }
  };

  const handleSocketEvent = (data) => {
    if (data.type === "agent_status") {
      const p = data.payload;

      const keyMap = {
        "Email Agent": "email",
        "Supervisor Agent": "supervisor",
        "Inventory Agent": "inventory",
        "Invoice Agent": "invoice",
        "Approval Agent": "approval",
      };

      const key = keyMap[p.agent];

      if (key) {
        setAgents((prev) => ({
          ...prev,
          [key]: {
            ...prev[key],
            status: p.status,
            tokens: p.tokens ?? prev[key].tokens,
            latency: p.latency_ms ?? prev[key].latency,
            context: p.context_window ?? prev[key].context,
          },
        }));
      }
    }

    if (data.type === "mcp_call") {
      setMcpCalls((prev) => [...prev, data.payload]);
    }

    if (data.type === "guardrails") {
      setGuardrails((prev) => [...prev, ...data.payload.checks]);
    }

    if (data.type === "workflow_complete") {
      const p = data.payload;
      setEmail(p.email);
      setStock(p.stock || null);
      setInvoice(p.invoice);
      setApproval(p.approval);
      setApprovalEmail(p.approval_email || null);
      setLogs(p.logs || []);
      setMcpCalls(p.mcp_calls || []);
      setGuardrails(p.guardrails || []);
      if (p.agents) {
        setAgents({
          ...initialAgents,
          ...p.agents,
        });
      }
    }
  };

  const processInbox = async () => {
    setAgents(initialAgents);
    setEmail(null);
    setMcpCalls([]);
    setGuardrails([]);
    setLogs([]);
    setInvoice(null);
    setApproval(null);
    setApprovalEmail(null);
    setStock(null);

    try {
      const res = await api.post("/invoice/process-inbox");
      if (res.data?.status === "failed") {
        alert(res.data.error || "Failed to process inbox.");
        await loadLatestWorkflow();
        return;
      }
      const latest = res.data?.results?.[res.data.results.length - 1];

      if (latest) {
        setEmail(latest.email || null);
        setStock(latest.stock || null);
        setInvoice(latest.invoice || null);
        setApproval(latest.approval || null);
        setApprovalEmail(latest.approval_email || null);
        setAgents({
          ...initialAgents,
          ...(latest.agents || {}),
        });
        setMcpCalls(latest.mcp_calls || []);
        setGuardrails(latest.guardrails || []);
        setLogs(latest.logs || []);
      } else {
        await loadLatestWorkflow();
      }
    } catch (error) {
      console.error("Failed to process inbox:", error);
      alert("Failed to process inbox. Check if backend is running or configured correctly.");
      await loadLatestWorkflow();
    }
  };


  return (
    <div className="app-shell">
      <div className="topbar">
        <div className="brand">
          <h1>MCP Multi-Agent Mission Control</h1>
        </div>
      </div>

      <div className="main-grid">
        <div>
          <EmailPanel email={email} />
          <br />
          <InventoryTable inventory={inventory} />
        </div>

        <div className="panel workflow-area">
          <button className="run-btn" onClick={processInbox}>
            Process Inbox
          </button>

          <WorkflowCanvas
            agents={agents}
            mcpCalls={mcpCalls}
            guardrails={guardrails}
          />
        </div>

        <div>
          <MetricsPanel
            agents={agents}
            mcpCalls={mcpCalls}
            email={email}
            stock={stock}
            invoice={invoice}
            approval={approval}
          />
          <br />
          <MCPTimeline events={mcpCalls} />
          <br />
          <GuardrailPanel checks={guardrails} />
          <br />
          <ApprovalPanel
            approval={approval}
            approvalEmail={approvalEmail}
            invoice={invoice}
            onApprovalChange={setApproval}
          />
          <br />
          <LogPanel logs={logs} />
        </div>
      </div>
    </div>
  );
}
