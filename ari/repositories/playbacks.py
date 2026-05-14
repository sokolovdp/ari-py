from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from ari.exceptions import raise_for_status
from ari.models import Playback

if TYPE_CHECKING:
    from ari.client import ARIClient


class PlaybackRepository:
    def __init__(self, http: httpx.AsyncClient, client: ARIClient | None) -> None:
        self._http = http
        self._client = client

    async def get(self, playback_id: str) -> Playback:
        r = await self._http.get(f"/playbacks/{playback_id}")
        raise_for_status(r, self._client)
        return Playback._with_client(r.json(), self._client)

    async def stop(self, playback_id: str) -> None:
        r = await self._http.delete(f"/playbacks/{playback_id}")
        raise_for_status(r, self._client)

    async def control(self, playback_id: str, operation: str) -> None:
        r = await self._http.post(
            f"/playbacks/{playback_id}/control",
            params={"operation": operation},
        )
        raise_for_status(r, self._client)
