from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from ari.exceptions import raise_for_status
from ari.models import Channel, LiveRecording, Playback

if TYPE_CHECKING:
    from ari.client import ARIClient


class ChannelRepository:
    def __init__(self, http: httpx.AsyncClient, client: ARIClient | None) -> None:
        self._http = http
        self._client = client

    async def list(self) -> list[Channel]:
        r = await self._http.get("/channels")
        raise_for_status(r, self._client)
        return [Channel._with_client(ch, self._client) for ch in r.json()]

    async def originate(
        self,
        endpoint: str,
        *,
        app: str | None = None,
        app_args: str | None = None,
        caller_id: str | None = None,
        timeout: int | None = None,
        channel_id: str | None = None,
        other_channel_id: str | None = None,
        originator: str | None = None,
        formats: str | None = None,
        variables: dict[str, Any] | None = None,
    ) -> Channel:
        body: dict[str, Any] = {"endpoint": endpoint}
        if app is not None:
            body["app"] = app
        if app_args is not None:
            body["appArgs"] = app_args
        if caller_id is not None:
            body["callerId"] = caller_id
        if timeout is not None:
            body["timeout"] = timeout
        if channel_id is not None:
            body["channelId"] = channel_id
        if other_channel_id is not None:
            body["otherChannelId"] = other_channel_id
        if originator is not None:
            body["originator"] = originator
        if formats is not None:
            body["formats"] = formats
        if variables is not None:
            body["variables"] = variables
        r = await self._http.post("/channels", json=body)
        raise_for_status(r, self._client)
        return Channel._with_client(r.json(), self._client)

    async def get(self, channel_id: str) -> Channel:
        r = await self._http.get(f"/channels/{channel_id}")
        raise_for_status(r, self._client)
        return Channel._with_client(r.json(), self._client)

    async def hangup(self, channel_id: str, *, reason: str | None = None) -> None:
        params: dict[str, str] = {}
        if reason is not None:
            params["reason"] = reason
        r = await self._http.delete(f"/channels/{channel_id}", params=params)
        raise_for_status(r, self._client)

    async def continue_in_dialplan(
        self,
        channel_id: str,
        *,
        context: str | None = None,
        extension: str | None = None,
        priority: int | None = None,
        label: str | None = None,
    ) -> None:
        params: dict[str, Any] = {}
        if context is not None:
            params["context"] = context
        if extension is not None:
            params["extension"] = extension
        if priority is not None:
            params["priority"] = priority
        if label is not None:
            params["label"] = label
        r = await self._http.post(f"/channels/{channel_id}/continue", params=params)
        raise_for_status(r, self._client)

    async def answer(self, channel_id: str) -> None:
        r = await self._http.post(f"/channels/{channel_id}/answer")
        raise_for_status(r, self._client)

    async def ring(self, channel_id: str) -> None:
        r = await self._http.post(f"/channels/{channel_id}/ring")
        raise_for_status(r, self._client)

    async def ring_stop(self, channel_id: str) -> None:
        r = await self._http.delete(f"/channels/{channel_id}/ring")
        raise_for_status(r, self._client)

    async def send_dtmf(
        self,
        channel_id: str,
        dtmf: str,
        *,
        before: int | None = None,
        between: int | None = None,
        duration: int | None = None,
        after: int | None = None,
    ) -> None:
        params: dict[str, Any] = {"dtmf": dtmf}
        if before is not None:
            params["before"] = before
        if between is not None:
            params["between"] = between
        if duration is not None:
            params["duration"] = duration
        if after is not None:
            params["after"] = after
        r = await self._http.post(f"/channels/{channel_id}/dtmf", params=params)
        raise_for_status(r, self._client)

    async def mute(self, channel_id: str, *, direction: str = "both") -> None:
        r = await self._http.post(
            f"/channels/{channel_id}/mute", params={"direction": direction}
        )
        raise_for_status(r, self._client)

    async def unmute(self, channel_id: str, *, direction: str = "both") -> None:
        r = await self._http.delete(
            f"/channels/{channel_id}/mute", params={"direction": direction}
        )
        raise_for_status(r, self._client)

    async def hold(self, channel_id: str) -> None:
        r = await self._http.post(f"/channels/{channel_id}/hold")
        raise_for_status(r, self._client)

    async def unhold(self, channel_id: str) -> None:
        r = await self._http.delete(f"/channels/{channel_id}/hold")
        raise_for_status(r, self._client)

    async def start_moh(self, channel_id: str, *, moh_class: str | None = None) -> None:
        params: dict[str, str] = {}
        if moh_class is not None:
            params["mohClass"] = moh_class
        r = await self._http.post(f"/channels/{channel_id}/moh", params=params)
        raise_for_status(r, self._client)

    async def stop_moh(self, channel_id: str) -> None:
        r = await self._http.delete(f"/channels/{channel_id}/moh")
        raise_for_status(r, self._client)

    async def play(
        self,
        channel_id: str,
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
        r = await self._http.post(f"/channels/{channel_id}/play", params=params)
        raise_for_status(r, self._client)
        return Playback._with_client(r.json(), self._client)

    async def record(
        self,
        channel_id: str,
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
        r = await self._http.post(f"/channels/{channel_id}/record", params=params)
        raise_for_status(r, self._client)
        return LiveRecording._with_client(r.json(), self._client)

    async def get_channel_var(self, channel_id: str, variable: str) -> str:
        r = await self._http.get(
            f"/channels/{channel_id}/variable", params={"variable": variable}
        )
        raise_for_status(r, self._client)
        return str(r.json()["value"])

    async def set_channel_var(
        self, channel_id: str, variable: str, value: str = ""
    ) -> None:
        r = await self._http.post(
            f"/channels/{channel_id}/variable",
            params={"variable": variable, "value": value},
        )
        raise_for_status(r, self._client)
