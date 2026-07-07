import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INVENTORY_FILE = BASE_DIR / "inventory.json"


def get_all_products():
    with open(INVENTORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def search_products(query: str):
    products = get_all_products()
    query = query.lower()

    matched = [
        product for product in products
        if query in product["name"].lower()
        or query in product["sku"].lower()
        or query in product["category"].lower()
    ]

    return {
        "tool": "Inventory MCP",
        "query": query,
        "results": matched,
        "count": len(matched),
    }


def check_stock(sku: str, quantity: int):
    products = get_all_products()

    for product in products:
        if product["sku"] == sku:
            return {
                "tool": "Inventory MCP",
                "sku": sku,
                "requested_quantity": quantity,
                "available_stock": product["stock"],
                "available": product["stock"] >= quantity,
                "product": product,
            }

    return {
        "tool": "Inventory MCP",
        "sku": sku,
        "available": False,
        "error": "Product not found",
    }