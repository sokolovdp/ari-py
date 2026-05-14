from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import httpx

from ari.exceptions import raise_for_status

if TYPE_CHECKING:
    from ari.client import ARIClient


class AsteriskRepository:
    def __init__(self, http: httpx.AsyncClient, client: ARIClient | None) -> None:
        self._http = http
        self._client = client

    async def get_info(self, *, fields: str | None = None) -> dict[str, Any]:
        params: dict[str, str] = {}
        if fields is not None:
            params["fields"] = fields
        r = await self._http.get("/asterisk/info", params=params)
        raise_for_status(r, self._client)
        return cast(dict[str, Any], r.json())

    async def get_global_var(self, variable: str) -> str:
        r = await self._http.get("/asterisk/variable", params={"variable": variable})
        raise_for_status(r, self._client)
        return str(r.json()["value"])

    async def set_global_var(self, variable: str, value: str = "") -> None:
        r = await self._http.post(
            "/asterisk/variable",
            params={"variable": variable, "value": value},
        )
        raise_for_status(r, self._client)
