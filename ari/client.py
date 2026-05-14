from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from typing import Any, Callable

import httpx
import websockets

from ari.events import EventUnsubscriber
from ari.models import (
    Bridge,
    Channel,
    DeviceState,
    Endpoint,
    LiveRecording,
    Playback,
    Sound,
    StoredRecording,
)
from ari.repositories import (
    ApplicationRepository,
    AsteriskRepository,
    BridgeRepository,
    ChannelRepository,
    DeviceStateRepository,
    EndpointRepository,
    MailboxRepository,
    PlaybackRepository,
    RecordingRepository,
    SoundRepository,
)

log = logging.getLogger(__name__)

_EVENT_MODEL_MAP: dict[str, dict[str, str]] = {
    "PlaybackStarted": {"playback": "Playback"},
    "PlaybackFinished": {"playback": "Playback"},
    "RecordingStarted": {"recording": "LiveRecording"},
    "RecordingFinished": {"recording": "LiveRecording"},
    "RecordingFailed": {"recording": "LiveRecording"},
    "BridgeCreated": {"bridge": "Bridge"},
    "BridgeDestroyed": {"bridge": "Bridge"},
    "BridgeMerged": {"bridge": "Bridge", "bridge_from": "Bridge"},
    "ChannelCreated": {"channel": "Channel"},
    "ChannelDestroyed": {"channel": "Channel"},
    "ChannelEnteredBridge": {"bridge": "Bridge", "channel": "Channel"},
    "ChannelLeftBridge": {"bridge": "Bridge", "channel": "Channel"},
    "ChannelStateChange": {"channel": "Channel"},
    "ChannelDtmfReceived": {"channel": "Channel"},
    "ChannelDialplan": {"channel": "Channel"},
    "ChannelCallerId": {"channel": "Channel"},
    "ChannelUserevent": {"channel": "Channel"},
    "ChannelHangupRequest": {"channel": "Channel"},
    "ChannelVarset": {"channel": "Channel"},
    "EndpointStateChange": {"endpoint": "Endpoint"},
    "StasisEnd": {"channel": "Channel"},
    "StasisStart": {"channel": "Channel"},
}

_MODEL_CLASS_MAP: dict[str, type[Any]] = {
    "Channel": Channel,
    "Bridge": Bridge,
    "Playback": Playback,
    "LiveRecording": LiveRecording,
    "StoredRecording": StoredRecording,
    "Endpoint": Endpoint,
    "DeviceState": DeviceState,
    "Sound": Sound,
}


class ARIClient:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._http = httpx.AsyncClient(
            base_url=f"{self._base_url}/ari",
            auth=(username, password),
            headers={"Content-Type": "application/json"},
        )
        self.channels = ChannelRepository(self._http, self)
        self.bridges = BridgeRepository(self._http, self)
        self.playbacks = PlaybackRepository(self._http, self)
        self.recordings = RecordingRepository(self._http, self)
        self.endpoints = EndpointRepository(self._http, self)
        self.device_states = DeviceStateRepository(self._http, self)
        self.sounds = SoundRepository(self._http, self)
        self.mailboxes = MailboxRepository(self._http, self)
        self.applications = ApplicationRepository(self._http, self)
        self.asterisk = AsteriskRepository(self._http, self)

        self._listeners: dict[str, list[tuple[Any, ...]]] = {}
        self._app_registered_callbacks: defaultdict[str, list[tuple[Any, ...]]] = (
            defaultdict(list)
        )
        self._app_deregistered_callbacks: defaultdict[str, list[tuple[Any, ...]]] = (
            defaultdict(list)
        )
        self.exception_handler: Callable[[Exception], None] = lambda ex: log.exception(
            "Event listener threw exception"
        )
        self._ws: websockets.ClientConnection | None = None

    async def close(self) -> None:
        if self._ws is not None:
            await self._ws.close()
        await self._http.aclose()

    async def __aenter__(self) -> ARIClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    def on_event(
        self,
        event_type: str,
        event_cb: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> EventUnsubscriber:
        listeners = self._listeners.setdefault(event_type, [])
        for cb in listeners:
            if event_cb is cb[0]:
                listeners.remove(cb)
                break
        callback_obj: tuple[Any, ...] = (event_cb, args, kwargs)
        listeners.append(callback_obj)
        return EventUnsubscriber(listeners, callback_obj)

    async def _dispatch(self, event: dict[str, Any]) -> None:
        event_type = event.get("type")
        if not event_type:
            log.error("Event missing 'type': %s", event)
            return
        for callback, args, kwargs in list(self._listeners.get(event_type, [])):
            try:
                result = callback(event, *args, **kwargs)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                self.exception_handler(e)

    def on_object_event(
        self,
        event_type: str,
        event_cb: Callable[..., Any],
        factory_fn: Callable[..., Any],
        model_id: str,
        *args: Any,
        **kwargs: Any,
    ) -> EventUnsubscriber:
        event_model = _EVENT_MODEL_MAP.get(event_type)
        if not event_model:
            raise ValueError(f"Cannot find event model '{event_type}'")
        obj_fields = [k for k, v in event_model.items() if v == model_id]
        if not obj_fields:
            raise ValueError(
                f"Event model '{event_type}' has no fields of type {model_id}"
            )

        def extract_objects(event: dict[str, Any], *args: Any, **kwargs: Any) -> None:
            obj: Any = {
                field: factory_fn(self, event[field])
                for field in obj_fields
                if event.get(field)
            }
            if len(obj_fields) == 1:
                obj = list(obj.values())[0] if obj else None
            event_cb(obj, event, *args, **kwargs)

        return self.on_event(event_type, extract_objects, *args, **kwargs)

    def on_channel_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> EventUnsubscriber:
        return self.on_object_event(
            event_type,
            fn,
            lambda client, d: Channel._with_client(d, client),
            "Channel",
            *args,
            **kwargs,
        )

    def on_bridge_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> EventUnsubscriber:
        return self.on_object_event(
            event_type,
            fn,
            lambda client, d: Bridge._with_client(d, client),
            "Bridge",
            *args,
            **kwargs,
        )

    def on_playback_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> EventUnsubscriber:
        return self.on_object_event(
            event_type,
            fn,
            lambda client, d: Playback._with_client(d, client),
            "Playback",
            *args,
            **kwargs,
        )

    def on_live_recording_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> EventUnsubscriber:
        return self.on_object_event(
            event_type,
            fn,
            lambda client, d: LiveRecording._with_client(d, client),
            "LiveRecording",
            *args,
            **kwargs,
        )

    def on_stored_recording_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> EventUnsubscriber:
        return self.on_object_event(
            event_type,
            fn,
            lambda client, d: StoredRecording._with_client(d, client),
            "StoredRecording",
            *args,
            **kwargs,
        )

    def on_endpoint_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> EventUnsubscriber:
        return self.on_object_event(
            event_type,
            fn,
            lambda client, d: Endpoint._with_client(d, client),
            "Endpoint",
            *args,
            **kwargs,
        )

    def on_device_state_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> EventUnsubscriber:
        return self.on_object_event(
            event_type,
            fn,
            lambda client, d: DeviceState._with_client(d, client),
            "DeviceState",
            *args,
            **kwargs,
        )

    def on_sound_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> EventUnsubscriber:
        return self.on_object_event(
            event_type,
            fn,
            lambda client, d: Sound._with_client(d, client),
            "Sound",
            *args,
            **kwargs,
        )

    def on_application_registered(
        self,
        application_name: str,
        fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._app_registered_callbacks[application_name].append((fn, args, kwargs))

    def on_application_deregistered(
        self,
        application_name: str,
        fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._app_deregistered_callbacks[application_name].append((fn, args, kwargs))

    def _execute_app_registered_callbacks(self, apps: str) -> None:
        self._execute_app_callbacks(apps, self._app_registered_callbacks)

    def _execute_app_deregistered_callbacks(self, apps: str) -> None:
        self._execute_app_callbacks(apps, self._app_deregistered_callbacks)

    def _execute_app_callbacks(
        self, apps: str, callback_map: dict[str, list[tuple[Any, ...]]]
    ) -> None:
        for app in apps.split(","):
            for fn, args, kwargs in callback_map[app]:
                try:
                    fn(*args, **kwargs)
                except Exception as e:
                    self.exception_handler(e)

    async def run(self, apps: str | list[str]) -> None:
        if isinstance(apps, list):
            apps = ",".join(apps)
        url = (
            f"{self._base_url}/ari/events"
            f"?app={apps}&api_key={self._username}:{self._password}"
        )
        async with websockets.connect(url) as ws:
            self._ws = ws
            self._execute_app_registered_callbacks(apps)
            try:
                async for raw in ws:
                    if not raw:
                        continue
                    try:
                        event = json.loads(raw)
                    except json.JSONDecodeError:
                        log.error("Failed to parse event JSON: %s", raw)
                        continue
                    await self._dispatch(event)
            finally:
                self._execute_app_deregistered_callbacks(apps)
                self._ws = None
