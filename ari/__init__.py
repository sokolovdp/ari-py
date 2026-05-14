from ari.client import ARIClient
from ari import exceptions
from ari.models import (
    Bridge,
    Channel,
    DeviceState,
    Endpoint,
    LiveRecording,
    Mailbox,
    Playback,
    Sound,
    StoredRecording,
)


def connect(base_url: str, username: str, password: str) -> ARIClient:
    return ARIClient(base_url, username, password)


__all__ = [
    "ARIClient",
    "connect",
    "exceptions",
    "Bridge",
    "Channel",
    "DeviceState",
    "Endpoint",
    "LiveRecording",
    "Mailbox",
    "Playback",
    "Sound",
    "StoredRecording",
]
