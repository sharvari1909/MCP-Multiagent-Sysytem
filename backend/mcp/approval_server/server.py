from mcp.approval_server.tools import (
    create_approval_request,
    approve_invoice,
    reject_invoice,
    get_approval_status,
)


class ApprovalMCPServer:
    def create(self, invoice_id: str, manager_email: str, amount: float):
        return create_approval_request(invoice_id, manager_email, amount)

    def approve(self, invoice_id: str):
        return approve_invoice(invoice_id)

    def reject(self, invoice_id: str):
        return reject_invoice(invoice_id)

    def status(self, invoice_id: str):
        return get_approval_status(invoice_id)