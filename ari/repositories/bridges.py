from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from ari.exceptions import raise_for_status
from ari.models import Bridge, LiveRecording, Playback

if TYPE_CHECKING:
    from ari.client import ARIClient


class BridgeRepository:
    def __init__(self, http: httpx.AsyncClient, client: ARIClient | None) -> None:
        self._http = http
        self._client = client

    async def list(self) -> list[Bridge]:
        r = await self._http.get("/bridges")
        raise_for_status(r, self._client)
        return [Bridge._with_client(b, self._client) for b in r.json()]

    async def create(
        self,
        *,
        type: str | None = None,
        bridge_id: str | None = None,
        name: str | None = None,
    ) -> Bridge:
        params: dict[str, str] = {}
        if type is not None:
            params["type"] = type
        if bridge_id is not None:
            params["bridgeId"] = bridge_id
        if name is not None:
            params["name"] = name
        r = await self._http.post("/bridges", params=params)
        raise_for_status(r, self._client)
        return Bridge._with_client(r.json(), self._client)

    async def get(self, bridge_id: str) -> Bridge:
        r = await self._http.get(f"/bridges/{bridge_id}")
        raise_for_status(r, self._client)
        return Bridge._with_client(r.json(), self._client)

    async def destroy(self, bridge_id: str) -> None:
        r = await self._http.delete(f"/bridges/{bridge_id}")
        raise_for_status(r, self._client)

    async def add_channel(
        self, bridge_id: str, channel: str, *, role: str | None = None
    ) -> None:
        params: dict[str, str] = {"channel": channel}
        if role is not None:
            params["role"] = role
        r = await self._http.post(f"/bridges/{bridge_id}/addChannel", params=params)
        raise_for_status(r, self._client)

    async def remove_channel(self, bridge_id: str, channel: str) -> None:
        r = await self._http.post(
            f"/bridges/{bridge_id}/removeChannel", params={"channel": channel}
        )
        raise_for_status(r, self._client)

    async def start_moh(self, bridge_id: str, *, moh_class: str | None = None) -> None:
        params: dict[str, str] = {}
        if moh_class is not None:
            params["mohClass"] = moh_class
        r = await self._http.post(f"/bridges/{bridge_id}/moh", params=params)
        raise_for_status(r, self._client)

    async def stop_moh(self, bridge_id: str) -> None:
        r = await self._http.delete(f"/bridges/{bridge_id}/moh")
        raise_for_status(r, self._client)

    async def play(
        self,
        bridge_id: str,
        media: str,
        *,
        lang: str | None = None,
        offset_ms: int | None = None,
        skip_ms: int | None = None,
        playback_id: str | None = None,
    ) -> Playback:
        params: dict[str, Any] = {"media": media}
        if lang is not None:
            params["lang"] = lang
        if offset_ms is not None:
            params["offsetms"] = offset_ms
        if skip_ms is not None:
            params["skipms"] = skip_ms
        if playback_id is not None:
            params["playbackId"] = playback_id
        r = await self._http.post(f"/bridges/{bridge_id}/play", params=params)
        raise_for_status(r, self._client)
        return Playback._with_client(r.json(), self._client)

    async def record(
        self,
        bridge_id: str,
        name: str,
        format: str,
        *,
        max_duration_seconds: int | None = None,
        max_silence_seconds: int | None = None,
        if_exists: str | None = None,
        beep: bool | None = None,
        terminate_on: str | None = None,
    ) -> LiveRecording:
        params: dict[str, Any] = {"name": name, "format": format}
        if max_duration_seconds is not None:
            params["maxDurationSeconds"] = max_duration_seconds
        if max_silence_seconds is not None:
            params["maxSilenceSeconds"] = max_silence_seconds
        if if_exists is not None:
            params["ifExists"] = if_exists
        if beep is not None:
            params["beep"] = beep
        if terminate_on is not None:
            params["terminateOn"] = terminate_on
        r = await self._http.post(f"/bridges/{bridge_id}/record", params=params)
        raise_for_status(r, self._client)
        return LiveRecording._with_client(r.json(), self._client)
