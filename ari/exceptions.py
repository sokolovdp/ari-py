from __future__ import annotations

from typing import TYPE_CHECKING, cast

import httpx

if TYPE_CHECKING:
    from ari.client import ARIClient

_HTTP_ERRORS: dict[int, type[ARIHTTPError]]


class ARIException(Exception):
    def __init__(self, client: ARIClient | None, response: httpx.Response) -> None:
        self.client = client
        self.response = response
        self.message = self._extract_message(response)
        super().__init__(self.message or str(response.status_code))

    @staticmethod
    def _extract_message(response: httpx.Response) -> str | None:
        try:
            return cast(str | None, response.json().get("message"))
        except Exception:
            return None


class ARIHTTPError(ARIException):
    pass


class ARINotFound(ARIHTTPError):
    pass


class ARINotInStasis(ARIHTTPError):
    pass


class ARIUnprocessable(ARIHTTPError):
    pass


class ARIServerError(ARIHTTPError):
    pass


class ARIServerUnavailable(ARIHTTPError):
    pass


_HTTP_ERRORS = {
    404: ARINotFound,
    409: ARINotInStasis,
    422: ARIUnprocessable,
    500: ARIServerError,
    503: ARIServerUnavailable,
}


def raise_for_status(response: httpx.Response, client: ARIClient | None) -> None:
    if response.is_error:
        exc_class = _HTTP_ERRORS.get(response.status_code, ARIException)
        raise exc_class(client, response)
