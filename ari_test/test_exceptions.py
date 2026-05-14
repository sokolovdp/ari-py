import importlib.util
import httpx
import pytest

# Import exceptions directly to avoid importing the rest of the ari module
# which still has old dependencies. This is a temporary measure until the
# entire codebase is migrated to httpx.
spec = importlib.util.spec_from_file_location(
    "ari_exceptions",
    "/Users/dp.sokolov/PycharmProjects/ari-py/ari/exceptions.py",
)
ari_exceptions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ari_exceptions)

ARIException = ari_exceptions.ARIException
ARINotFound = ari_exceptions.ARINotFound
ARINotInStasis = ari_exceptions.ARINotInStasis
ARIUnprocessable = ari_exceptions.ARIUnprocessable
ARIServerError = ari_exceptions.ARIServerError
ARIServerUnavailable = ari_exceptions.ARIServerUnavailable
raise_for_status = ari_exceptions.raise_for_status


def make_response(status_code: int, body: dict | None = None) -> httpx.Response:
    return httpx.Response(status_code, json=body or {})


def test_raise_for_status_404():
    with pytest.raises(ARINotFound):
        raise_for_status(make_response(404, {"message": "not found"}), client=None)


def test_raise_for_status_409():
    with pytest.raises(ARINotInStasis):
        raise_for_status(make_response(409), client=None)


def test_raise_for_status_422():
    with pytest.raises(ARIUnprocessable):
        raise_for_status(make_response(422), client=None)


def test_raise_for_status_500():
    with pytest.raises(ARIServerError):
        raise_for_status(make_response(500, {"message": "oops"}), client=None)


def test_raise_for_status_503():
    with pytest.raises(ARIServerUnavailable):
        raise_for_status(make_response(503), client=None)


def test_raise_for_status_unknown_error():
    with pytest.raises(ARIException):
        raise_for_status(make_response(418), client=None)


def test_raise_for_status_success():
    raise_for_status(make_response(200), client=None)


def test_raise_for_status_no_content():
    raise_for_status(make_response(204), client=None)


def test_exception_extracts_message():
    response = make_response(500, {"message": "internal error"})
    exc = ARIServerError(client=None, response=response)
    assert exc.message == "internal error"


def test_exception_handles_missing_message():
    response = make_response(500, {})
    exc = ARIServerError(client=None, response=response)
    assert exc.message is None
