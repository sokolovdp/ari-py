from __future__ import annotations

from typing import TYPE_CHECKING, List

import httpx

from ari.exceptions import raise_for_status
from ari.models import Endpoint

if TYPE_CHECKING:
    from ari.client import ARIClient


class EndpointRepository:
    def __init__(self, http: httpx.AsyncClient, client: ARIClient | None) -> None:
        self._http = http
        self._client = client

    async def list(self) -> List[Endpoint]:
        r = await self._http.get("/endpoints")
        raise_for_status(r, self._client)
        return [Endpoint._with_client(ep, self._client) for ep in r.json()]

    async def list_by_tech(self, tech: str) -> List[Endpoint]:
        r = await self._http.get(f"/endpoints/{tech}")
        raise_for_status(r, self._client)
        return [Endpoint._with_client(ep, self._client) for ep in r.json()]

    async def get(self, tech: str, resource: str) -> Endpoint:
        r = await self._http.get(f"/endpoints/{tech}/{resource}")
        raise_for_status(r, self._client)
        return Endpoint._with_client(r.json(), self._client)
