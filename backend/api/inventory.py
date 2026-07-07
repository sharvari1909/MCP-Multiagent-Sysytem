from fastapi import APIRouter
from mcp.inventory_server.tools import get_all_products, search_products

router = APIRouter()


@router.get("/")
def inventory():
    return get_all_products()


@router.get("/search")
def search(q: str):
    return search_products(q)