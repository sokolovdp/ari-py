from __future__ import annotations

from collections import defaultdict

import httpx
import pytest

from ari.client import ARIClient
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

BASE_URL = "http://ari.py"


@pytest.fixture
async def ari_client():
    http = httpx.AsyncClient(base_url=f"{BASE_URL}/ari", auth=("test", "test"))
    client = ARIClient.__new__(ARIClient)
    client._http = http
    client._base_url = BASE_URL
    client._username = "test"
    client._password = "test"
    client._listeners = {}
    client._app_registered_callbacks = defaultdict(list)
    client._app_deregistered_callbacks = defaultdict(list)
    client._ws = None

    def reraise(ex: Exception) -> None:
        raise ex

    client.exception_handler = reraise

    client.channels = ChannelRepository(http, client)
    client.bridges = BridgeRepository(http, client)
    client.playbacks = PlaybackRepository(http, client)
    client.recordings = RecordingRepository(http, client)
    client.endpoints = EndpointRepository(http, client)
    client.device_states = DeviceStateRepository(http, client)
    client.sounds = SoundRepository(http, client)
    client.mailboxes = MailboxRepository(http, client)
    client.applications = ApplicationRepository(http, client)
    client.asterisk = AsteriskRepository(http, client)

    yield client

    await http.aclose()
