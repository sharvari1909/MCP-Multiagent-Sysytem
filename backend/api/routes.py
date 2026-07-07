from fastapi import APIRouter

from api.inventory import router as inventory_router
from api.invoice import router as invoice_router
from api.approval import router as approval_router

router = APIRouter()

router.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
router.include_router(invoice_router, prefix="/invoice", tags=["Invoice"])
router.include_router(approval_router, prefix="/approval", tags=["Approval"])


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "backend": "running",
        "mcp": "ready",
    }