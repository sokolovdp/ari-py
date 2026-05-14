from ari.events import EventUnsubscriber


def test_close_removes_callback():
    listeners: list = []
    cb = ("fn", (), {})
    listeners.append(cb)
    unsub = EventUnsubscriber(listeners, cb)

    unsub.close()

    assert cb not in listeners


def test_close_idempotent():
    listeners: list = []
    cb = ("fn", (), {})
    listeners.append(cb)
    unsub = EventUnsubscriber(listeners, cb)

    unsub.close()
    unsub.close()  # second call must not raise

    assert listeners == []


def test_close_only_removes_target():
    listeners: list = []
    cb1 = ("fn1", (), {})
    cb2 = ("fn2", (), {})
    listeners.extend([cb1, cb2])
    unsub = EventUnsubscriber(listeners, cb1)

    unsub.close()

    assert cb1 not in listeners
    assert cb2 in listeners
