from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from ari.exceptions import raise_for_status
from ari.models import Sound

if TYPE_CHECKING:
    from ari.client import ARIClient


class SoundRepository:
    def __init__(self, http: httpx.AsyncClient, client: ARIClient | None) -> None:
        self._http = http
        self._client = client

    async def list(
        self,
        *,
        lang: str | None = None,
        format: str | None = None,
    ) -> list[Sound]:
        params: dict[str, Any] = {}
        if lang is not None:
            params["lang"] = lang
        if format is not None:
            params["format"] = format
        r = await self._http.get("/sounds", params=params)
        raise_for_status(r, self._client)
        return [Sound._with_client(s, self._client) for s in r.json()]

    async def get(self, sound_id: str) -> Sound:
        r = await self._http.get(f"/sounds/{sound_id}")
        raise_for_status(r, self._client)
        return Sound._with_client(r.json(), self._client)
