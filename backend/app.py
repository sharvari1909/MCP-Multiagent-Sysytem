from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as main_router
from agents.email_poller import email_poller
from websocket import router as websocket_router

app = FastAPI(
    title="MCP Multiagent System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router, prefix="/api")
app.include_router(websocket_router)


@app.on_event("startup")
async def start_email_poller():
    email_poller.start()


@app.on_event("shutdown")
async def stop_email_poller():
    await email_poller.stop()


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "MCP Multiagent System",
        "message": "MCP multi-agent backend is active",
    }
