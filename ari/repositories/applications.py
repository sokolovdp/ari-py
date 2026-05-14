from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import httpx

from ari.exceptions import raise_for_status

if TYPE_CHECKING:
    from ari.client import ARIClient


class ApplicationRepository:
    def __init__(self, http: httpx.AsyncClient, client: ARIClient | None) -> None:
        self._http = http
        self._client = client

    async def list(self) -> list[dict[str, Any]]:
        r = await self._http.get("/applications")
        raise_for_status(r, self._client)
        return cast(list[dict[str, Any]], r.json())

    async def get(self, app_name: str) -> dict[str, Any]:
        r = await self._http.get(f"/applications/{app_name}")
        raise_for_status(r, self._client)
        return cast(dict[str, Any], r.json())

    async def subscribe(self, app_name: str, event_source: str) -> dict[str, Any]:
        r = await self._http.post(
            f"/applications/{app_name}/subscription",
            params={"eventSource": event_source},
        )
        raise_for_status(r, self._client)
        return cast(dict[str, Any], r.json())

    async def unsubscribe(self, app_name: str, event_source: str) -> dict[str, Any]:
        r = await self._http.delete(
            f"/applications/{app_name}/subscription",
            params={"eventSource": event_source},
        )
        raise_for_status(r, self._client)
        return cast(dict[str, Any], r.json())
