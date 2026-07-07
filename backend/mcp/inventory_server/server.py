from mcp.inventory_server.tools import get_all_products, search_products, check_stock


class InventoryMCPServer:
    def list_products(self):
        return get_all_products()

    def search(self, query: str):
        return search_products(query)

    def stock(self, sku: str, quantity: int):
        return check_stock(sku, quantity)