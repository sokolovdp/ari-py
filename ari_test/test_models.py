from ari.models import (
    Channel,
    Bridge,
    Playback,
    LiveRecording,
    StoredRecording,
    Endpoint,
    DeviceState,
    Sound,
    Mailbox,
)


def test_channel_fields():
    ch = Channel(id="ch-1", name="PJSIP/100-001", state="Up")
    assert ch.id == "ch-1"
    assert ch.name == "PJSIP/100-001"
    assert ch.state == "Up"


def test_channel_optional_defaults():
    ch = Channel(id="ch-1")
    assert ch.name is None
    assert ch.caller is None
    assert ch._client is None


def test_channel_allows_extra_fields():
    ch = Channel(id="ch-1", unknown_future_field="value")
    assert ch.model_extra["unknown_future_field"] == "value"


def test_bridge_fields():
    br = Bridge(id="br-1", technology="simple_bridge", bridge_type="mixing")
    assert br.id == "br-1"
    assert br.channels == []


def test_playback_fields():
    pb = Playback(id="pb-1", media_uri="sound:beep", state="playing")
    assert pb.id == "pb-1"
    assert pb.state == "playing"


def test_live_recording_fields():
    rec = LiveRecording(name="my-recording", format="wav", state="recording")
    assert rec.name == "my-recording"


def test_stored_recording_fields():
    rec = StoredRecording(name="stored-1", format="wav")
    assert rec.name == "stored-1"


def test_endpoint_fields():
    ep = Endpoint(technology="PJSIP", resource="100")
    assert ep.technology == "PJSIP"
    assert ep.channel_ids == []


def test_device_state_fields():
    ds = DeviceState(name="Custom:dev1", state="NOT_INUSE")
    assert ds.name == "Custom:dev1"


def test_sound_fields():
    snd = Sound(id="beep", formats=[{"format": "wav", "language": "en"}])
    assert snd.id == "beep"
    assert len(snd.formats) == 1


def test_mailbox_fields():
    mb = Mailbox(name="1000", old_messages="1", new_messages="3")
    assert mb.name == "1000"
    assert mb.old_messages == "1"
