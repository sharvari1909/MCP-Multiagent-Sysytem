import asyncio
import contextlib

from config import settings
from agents.supervisor import process_unread_invoice_emails


class EmailPoller:
    def __init__(self):
        self._task = None

    def start(self):
        if not settings.EMAIL_POLLING_ENABLED:
            return

        if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
            return

        if self._task and not self._task.done():
            return

        self._task = asyncio.create_task(self._run())

    async def stop(self):
        if not self._task:
            return

        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task

    async def _run(self):
        while True:
            try:
                await process_unread_invoice_emails(limit=5)
            except Exception as exc:
                print(f"Email poller error: {exc}")

            await asyncio.sleep(settings.EMAIL_POLL_INTERVAL_SECONDS)


email_poller = EmailPoller()
