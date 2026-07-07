 Backend Architecture
                           FastAPI
                               │
               ┌───────────────┴───────────────┐
               │                               │
          REST APIs                     WebSockets
               │                               │
               └───────────────┬───────────────┘
                               │
                       Supervisor Agent
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   Email Agent          Inventory Agent        Invoice Agent
        │                      │                      │
        ▼                      ▼                      ▼
   Email MCP             Inventory MCP         Invoice MCP
        │                      │                      │
        ▼                      ▼                      ▼
 SMTP / IMAP           Demo JSON → Odoo          PDF Generator
                               │
                               ▼
                      Approval Agent
                               │
                               ▼
                        Approval MCP
                               │
                               ▼
                     Manager Approval Email
                               │
                               ▼
                          Audit MCP
                               │
                               ▼
                            SQLite

MCP SERVER

                             CUSTOMER

                               │
                               │
                     Sends Email Request
                               │
                               ▼
                    web@anvenssa.com (Inbox)
                               │
                               ▼
                  ┌─────────────────────────┐
                  │     Email MCP Server    │
                  │-------------------------│
                  │ Read Inbox (IMAP)       │
                  │ Parse Email             │
                  │ Extract Customer        │
                  │ Extract Products        │
                  └───────────┬─────────────┘
                              │
                              ▼
                     📧 Email Agent
                              │
                              ▼
                   🧠 Supervisor Agent
                              │
      ┌───────────────────────┼────────────────────────┐
      │                       │                        │
      ▼                       ▼                        ▼
📦 Inventory Agent      📄 Invoice Agent        ✅ Approval Agent
      │                       │                        │
      ▼                       ▼                        ▼
┌───────────────┐     ┌────────────────┐     ┌────────────────┐
│Inventory MCP  │     │ Invoice MCP    │     │ Approval MCP   │
├───────────────┤     ├────────────────┤     ├────────────────┤
│Search Product │     │Generate PDF    │     │Create Request  │
│Check Stock    │     │GST Calculation │     │Manager Status  │
│Price Lookup   │     │Invoice Number  │     │Approve/Reject  │
│Warehouse Info │     │Store Invoice   │     │                │
└───────┬───────┘     └────────┬───────┘     └────────┬───────┘
        │                      │                      │
        ▼                      ▼                      ▼
 Inventory JSON          Invoice PDF          sharvari@anvenssa.com
   (Later Odoo)                                     │
                                                    │
                                              Approves Invoice
                                                    │
                                                    ▼
                                           Approval MCP updates
                                                    │
                                                    ▼
                    ┌───────────────────────────────┐
                    │       Audit MCP Server        │
                    ├───────────────────────────────┤
                    │ Agent Logs                    │
                    │ MCP Tool Calls                │
                    │ Workflow History              │
                    │ Invoice History               │
                    │ Approval Logs                 │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                          📧 Email Agent
                                    │
                                    ▼
                          Email MCP Server
                                    │
                           SMTP Send Invoice
                                    │
                                    ▼
                               CUSTOMER

                               
## License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

## Commands


bash
# 1. Install backend requirements
pip install -r backend/requirements.txt

# 2. Install frontend dependenciesy
cd frontend && npm install

# 3. Start backend
cd backend && uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# 4. Start frontend
cd frontend && npm run dev

# 5. Start backend and frontend with Docker
docker compose up --build

