from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from ari.exceptions import raise_for_status
from ari.models import Mailbox

if TYPE_CHECKING:
    from ari.client import ARIClient


class MailboxRepository:
    def __init__(self, http: httpx.AsyncClient, client: ARIClient | None) -> None:
        self._http = http
        self._client = client

    async def list(self) -> list[Mailbox]:
        r = await self._http.get("/mailboxes")
        raise_for_status(r, self._client)
        return [Mailbox._with_client(mb, self._client) for mb in r.json()]

    async def get(self, mailbox_name: str) -> Mailbox:
        r = await self._http.get(f"/mailboxes/{mailbox_name}")
        raise_for_status(r, self._client)
        return Mailbox._with_client(r.json(), self._client)

    async def update(
        self, mailbox_name: str, old_messages: int, new_messages: int
    ) -> Mailbox:
        r = await self._http.put(
            f"/mailboxes/{mailbox_name}",
            params={"oldMessages": old_messages, "newMessages": new_messages},
        )
        raise_for_status(r, self._client)
        return Mailbox._with_client(r.json(), self._client)

    async def delete(self, mailbox_name: str) -> None:
        r = await self._http.delete(f"/mailboxes/{mailbox_name}")
        raise_for_status(r, self._client)
