from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Self

from pydantic import BaseModel, ConfigDict, PrivateAttr

if TYPE_CHECKING:
    from ari.client import ARIClient


class _ARIBase(BaseModel):
    """Base class that allows injecting ``_client`` via ``_with_client``."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    _client: ARIClient | None = PrivateAttr(default=None)

    @classmethod
    def _with_client(cls, data: dict[str, Any], client: ARIClient | None) -> Self:
        obj = cls.model_validate(data)
        object.__setattr__(obj, "_client", client)
        return obj

    @property
    def _c(self) -> ARIClient:
        assert self._client is not None
        return self._client


class Channel(_ARIBase):
    id: str
    name: str | None = None
    state: str | None = None
    caller: dict[str, Any] | None = None
    connected: dict[str, Any] | None = None
    accountcode: str | None = None
    dialplan: dict[str, Any] | None = None
    creationtime: str | None = None

    async def hangup(self, *, reason: str | None = None) -> None:
        await self._c.channels.hangup(self.id, reason=reason)

    async def answer(self) -> None:
        await self._c.channels.answer(self.id)

    async def ring(self) -> None:
        await self._c.channels.ring(self.id)

    async def ring_stop(self) -> None:
        await self._c.channels.ring_stop(self.id)

    async def send_dtmf(self, dtmf: str, **kwargs: Any) -> None:
        await self._c.channels.send_dtmf(self.id, dtmf, **kwargs)

    async def mute(self, *, direction: str = "both") -> None:
        await self._c.channels.mute(self.id, direction=direction)

    async def unmute(self, *, direction: str = "both") -> None:
        await self._c.channels.unmute(self.id, direction=direction)

    async def hold(self) -> None:
        await self._c.channels.hold(self.id)

    async def unhold(self) -> None:
        await self._c.channels.unhold(self.id)

    async def start_moh(self, *, moh_class: str | None = None) -> None:
        await self._c.channels.start_moh(self.id, moh_class=moh_class)

    async def stop_moh(self) -> None:
        await self._c.channels.stop_moh(self.id)

    async def play(self, media: str, **kwargs: Any) -> Playback:
        return await self._c.channels.play(self.id, media, **kwargs)

    async def record(self, name: str, format: str, **kwargs: Any) -> LiveRecording:
        return await self._c.channels.record(self.id, name, format, **kwargs)

    async def get_var(self, variable: str) -> str:
        return await self._c.channels.get_channel_var(self.id, variable)

    async def set_var(self, variable: str, value: str = "") -> None:
        await self._c.channels.set_channel_var(self.id, variable, value)

    async def continue_in_dialplan(self, **kwargs: Any) -> None:
        await self._c.channels.continue_in_dialplan(self.id, **kwargs)

    def on_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        channel_id = self.id

        def fn_filter(
            objects: Channel | dict[str, Any] | None,
            event: dict[str, Any],
            *args: Any,
            **kwargs: Any,
        ) -> None:
            if isinstance(objects, dict):
                if channel_id in [c.id for c in objects.values()]:
                    fn(objects, event, *args, **kwargs)
            elif objects is not None and objects.id == channel_id:
                fn(objects, event, *args, **kwargs)

        return self._c.on_channel_event(event_type, fn_filter, *args, **kwargs)


class Bridge(_ARIBase):
    id: str
    technology: str | None = None
    bridge_type: str | None = None
    bridge_class: str | None = None
    channels: list[str] = []

    async def destroy(self) -> None:
        await self._c.bridges.destroy(self.id)

    async def add_channel(self, channel: str, *, role: str | None = None) -> None:
        await self._c.bridges.add_channel(self.id, channel, role=role)

    async def remove_channel(self, channel: str) -> None:
        await self._c.bridges.remove_channel(self.id, channel)

    async def play(self, media: str, **kwargs: Any) -> Playback:
        return await self._c.bridges.play(self.id, media, **kwargs)

    async def record(self, name: str, format: str, **kwargs: Any) -> LiveRecording:
        return await self._c.bridges.record(self.id, name, format, **kwargs)

    async def start_moh(self, *, moh_class: str | None = None) -> None:
        await self._c.bridges.start_moh(self.id, moh_class=moh_class)

    async def stop_moh(self) -> None:
        await self._c.bridges.stop_moh(self.id)

    def on_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        bridge_id = self.id

        def fn_filter(
            objects: Bridge | dict[str, Any] | None,
            event: dict[str, Any],
            *args: Any,
            **kwargs: Any,
        ) -> None:
            if isinstance(objects, dict):
                if bridge_id in [b.id for b in objects.values()]:
                    fn(objects, event, *args, **kwargs)
            elif objects is not None and objects.id == bridge_id:
                fn(objects, event, *args, **kwargs)

        return self._c.on_bridge_event(event_type, fn_filter, *args, **kwargs)


class Playback(_ARIBase):
    id: str
    media_uri: str | None = None
    target_uri: str | None = None
    language: str | None = None
    state: str | None = None

    async def stop(self) -> None:
        await self._c.playbacks.stop(self.id)

    async def control(self, operation: str) -> None:
        await self._c.playbacks.control(self.id, operation)

    def on_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        playback_id = self.id

        def fn_filter(
            objects: Playback | dict[str, Any] | None,
            event: dict[str, Any],
            *args: Any,
            **kwargs: Any,
        ) -> None:
            if isinstance(objects, dict):
                if playback_id in [p.id for p in objects.values()]:
                    fn(objects, event, *args, **kwargs)
            elif objects is not None and objects.id == playback_id:
                fn(objects, event, *args, **kwargs)

        return self._c.on_playback_event(event_type, fn_filter, *args, **kwargs)


class LiveRecording(_ARIBase):
    name: str
    format: str | None = None
    state: str | None = None

    async def cancel(self) -> None:
        await self._c.recordings.cancel(self.name)

    async def stop(self) -> None:
        await self._c.recordings.stop(self.name)

    async def pause(self) -> None:
        await self._c.recordings.pause(self.name)

    async def unpause(self) -> None:
        await self._c.recordings.unpause(self.name)

    async def mute(self) -> None:
        await self._c.recordings.mute(self.name)

    async def unmute(self) -> None:
        await self._c.recordings.unmute(self.name)

    def on_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        return self._c.on_live_recording_event(event_type, fn, *args, **kwargs)


class StoredRecording(_ARIBase):
    name: str
    format: str | None = None

    async def get(self) -> StoredRecording:
        return await self._c.recordings.get_stored(self.name)

    async def delete(self) -> None:
        await self._c.recordings.delete_stored(self.name)

    def on_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        return self._c.on_stored_recording_event(event_type, fn, *args, **kwargs)


class Endpoint(_ARIBase):
    technology: str
    resource: str
    state: str | None = None
    channel_ids: list[str] = []

    async def get(self) -> Endpoint:
        return await self._c.endpoints.get(self.technology, self.resource)

    def on_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        return self._c.on_endpoint_event(event_type, fn, *args, **kwargs)


class DeviceState(_ARIBase):
    name: str
    state: str | None = None

    async def update(self, device_state: str) -> DeviceState:
        return await self._c.device_states.update(self.name, device_state)

    async def delete(self) -> None:
        await self._c.device_states.delete(self.name)

    def on_event(
        self, event_type: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        return self._c.on_device_state_event(event_type, fn, *args, **kwargs)


class Sound(_ARIBase):
    id: str
    text: str | None = None
    formats: list[dict[str, Any]] = []


class Mailbox(_ARIBase):
    name: str
    old_messages: str | int | None = None
    new_messages: str | int | None = None

    async def update(self, old_messages: int, new_messages: int) -> None:
        await self._c.mailboxes.update(self.name, old_messages, new_messages)

    async def delete(self) -> None:
        await self._c.mailboxes.delete(self.name)
