from fastapi import APIRouter
from agents.supervisor import process_unread_invoice_emails, run_demo_workflow
from agents.workflow_store import workflow_store

router = APIRouter()


@router.post("/run-demo")
async def run_demo():
    result = await run_demo_workflow()
    return result


@router.post("/process-inbox")
async def process_inbox(limit: int = 5):
    result = await process_unread_invoice_emails(limit=limit)
    return result


@router.get("/workflows")
def workflows():
    return list(workflow_store.values())
