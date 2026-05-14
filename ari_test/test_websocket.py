import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ari.models import Channel


async def test_on_event_basic(ari_client):
    received = []
    ari_client.on_event("StasisStart", lambda e: received.append(e))
    await ari_client._dispatch({"type": "StasisStart", "data": 1})
    assert received == [{"type": "StasisStart", "data": 1}]


async def test_on_event_filters_type(ari_client):
    received = []
    ari_client.on_event("StasisStart", lambda e: received.append(e))
    await ari_client._dispatch({"type": "StasisEnd", "data": 2})
    assert received == []


async def test_on_event_multiple_callbacks(ari_client):
    a, b = [], []
    ari_client.on_event("ev", lambda e: a.append(e))
    ari_client.on_event("ev", lambda e: b.append(e))
    await ari_client._dispatch({"type": "ev"})
    assert len(a) == 1
    assert len(b) == 1


async def test_unsubscribe(ari_client):
    received = []
    unsub = ari_client.on_event("ev", lambda e: received.append(e))
    unsub.close()
    await ari_client._dispatch({"type": "ev"})
    assert received == []


async def test_on_event_duplicate_callback_replaced(ari_client):
    called = []

    def cb(e):
        called.append(e)

    ari_client.on_event("ev", cb)
    ari_client.on_event("ev", cb)  # re-register same callback
    await ari_client._dispatch({"type": "ev"})
    assert len(called) == 1


async def test_async_callback(ari_client):
    received = []

    async def handler(event):
        received.append(event)

    ari_client.on_event("ev", handler)
    await ari_client._dispatch({"type": "ev", "x": 1})
    assert received == [{"type": "ev", "x": 1}]


async def test_on_channel_event(ari_client):
    received = []

    def cb(channel, event):
        received.append((channel, event))

    ari_client.on_channel_event("StasisStart", cb)
    await ari_client._dispatch({"type": "StasisStart", "channel": {"id": "ch-1"}})
    assert len(received) == 1
    channel, event = received[0]
    assert isinstance(channel, Channel)
    assert channel.id == "ch-1"


async def test_on_channel_event_no_channel_field(ari_client):
    received = []
    ari_client.on_channel_event("StasisStart", lambda ch, ev: received.append(ch))
    await ari_client._dispatch({"type": "StasisStart"})
    assert received == [None]


async def test_on_object_event_bad_event_type(ari_client):
    with pytest.raises(ValueError, match="Cannot find event model"):
        ari_client.on_object_event(
            "NonExistentEvent", lambda *a: None, lambda *a: None, "Channel"
        )


async def test_on_object_event_bad_model_type(ari_client):
    with pytest.raises(ValueError, match="no fields of type"):
        ari_client.on_object_event(
            "StasisStart", lambda *a: None, lambda *a: None, "Bridge"
        )


async def test_app_registered_callbacks(ari_client):
    called = []
    ari_client.on_application_registered("my-app", lambda: called.append(True))
    ari_client._execute_app_registered_callbacks("my-app")
    assert called == [True]


async def test_app_deregistered_callbacks(ari_client):
    called = []
    ari_client.on_application_deregistered("my-app", lambda: called.append(True))
    ari_client._execute_app_deregistered_callbacks("my-app")
    assert called == [True]


async def test_run_dispatches_messages(ari_client):
    messages = [
        json.dumps({"type": "StasisStart", "channel": {"id": "ch-1"}}),
        json.dumps({"type": "StasisEnd", "channel": {"id": "ch-1"}}),
    ]
    received_types = []
    ari_client.on_event("StasisStart", lambda e: received_types.append(e["type"]))
    ari_client.on_event("StasisEnd", lambda e: received_types.append(e["type"]))

    async def fake_ws_iter():
        for m in messages:
            yield m

    mock_ws = MagicMock()
    mock_ws.__aiter__ = lambda self: fake_ws_iter()
    mock_ws.close = AsyncMock()

    with patch("websockets.connect") as mock_connect:
        mock_connect.return_value.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.return_value.__aexit__ = AsyncMock(return_value=False)
        await ari_client.run("test-app")

    assert received_types == ["StasisStart", "StasisEnd"]


async def test_run_calls_app_callbacks(ari_client):
    registered = []
    deregistered = []
    ari_client.on_application_registered("my-app", lambda: registered.append(True))
    ari_client.on_application_deregistered("my-app", lambda: deregistered.append(True))

    async def fake_ws_iter():
        return
        yield  # make it an async generator

    mock_ws = MagicMock()
    mock_ws.__aiter__ = lambda self: fake_ws_iter()
    mock_ws.close = AsyncMock()

    with patch("websockets.connect") as mock_connect:
        mock_connect.return_value.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.return_value.__aexit__ = AsyncMock(return_value=False)
        await ari_client.run("my-app")

    assert registered == [True]
    assert deregistered == [True]
