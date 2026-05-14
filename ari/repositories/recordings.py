from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from ari.exceptions import raise_for_status
from ari.models import LiveRecording, StoredRecording

if TYPE_CHECKING:
    from ari.client import ARIClient


class RecordingRepository:
    def __init__(self, http: httpx.AsyncClient, client: ARIClient | None) -> None:
        self._http = http
        self._client = client

    async def get_live(self, recording_name: str) -> LiveRecording:
        r = await self._http.get(f"/recordings/live/{recording_name}")
        raise_for_status(r, self._client)
        return LiveRecording._with_client(r.json(), self._client)

    async def cancel(self, recording_name: str) -> None:
        r = await self._http.delete(f"/recordings/live/{recording_name}")
        raise_for_status(r, self._client)

    async def stop(self, recording_name: str) -> None:
        r = await self._http.post(f"/recordings/live/{recording_name}/stop")
        raise_for_status(r, self._client)

    async def pause(self, recording_name: str) -> None:
        r = await self._http.post(f"/recordings/live/{recording_name}/pause")
        raise_for_status(r, self._client)

    async def unpause(self, recording_name: str) -> None:
        r = await self._http.delete(f"/recordings/live/{recording_name}/pause")
        raise_for_status(r, self._client)

    async def mute(self, recording_name: str) -> None:
        r = await self._http.post(f"/recordings/live/{recording_name}/mute")
        raise_for_status(r, self._client)

    async def unmute(self, recording_name: str) -> None:
        r = await self._http.delete(f"/recordings/live/{recording_name}/mute")
        raise_for_status(r, self._client)

    async def list_stored(self) -> list[StoredRecording]:
        r = await self._http.get("/recordings/stored")
        raise_for_status(r, self._client)
        return [StoredRecording._with_client(rec, self._client) for rec in r.json()]

    async def get_stored(self, recording_name: str) -> StoredRecording:
        r = await self._http.get(f"/recordings/stored/{recording_name}")
        raise_for_status(r, self._client)
        return StoredRecording._with_client(r.json(), self._client)

    async def delete_stored(self, recording_name: str) -> None:
        r = await self._http.delete(f"/recordings/stored/{recording_name}")
        raise_for_status(r, self._client)
