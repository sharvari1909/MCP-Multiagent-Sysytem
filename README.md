git clone https://github.com/sharvari1909/MCP-Multiagent-Sysytem.git
cd MCP-Multiagent-Sysytem

**Backend Commands:**
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000

**Frontend commands**
cd frontend
npm install
npm run dev

**Backend:  http://localhost:8000
Frontend: http://localhost:5174**
