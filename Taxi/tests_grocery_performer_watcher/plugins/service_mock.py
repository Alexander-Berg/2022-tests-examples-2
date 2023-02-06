# pylint: disable=import-only-modules, unsubscriptable-object, invalid-name
# flake8: noqa IS001
from dataclasses import dataclass, fields
from typing import Optional, Dict, List

from testsuite.utils.callinfo import AsyncCallQueue
from testsuite.utils.http import make_response


@dataclass
class ErrorResponse:
    status: int
    code: str
    message: str


@dataclass
class EndpointContext:
    mock: AsyncCallQueue
    response: Optional[Dict] = None
    error: Optional[ErrorResponse] = None
    service_context: Optional['ServiceContext'] = None

    def raise_error(
            self,
            status: int,
            code: str = 'error_code',
            message: str = 'error_message',
    ):
        self.error = ErrorResponse(status, code, message)

    def raise_only_error(
            self,
            status: int,
            code: str = 'error_code',
            message: str = 'error_message',
    ):
        if self.service_context:
            self.service_context.clear_errors()
        self.raise_error(status, code, message)

    def clear_error(self):
        self.error = None

    def make_error_response(self):
        return make_response(
            json={'code': self.error.code, 'message': self.error.message},
            status=self.error.status,
        )

    def __getattr__(self, item):
        """Go to service context if not found in endpoint."""
        if self.service_context:
            return getattr(self.service_context, item)
        raise AttributeError


@dataclass
class ServiceContext:
    def views(self) -> List[EndpointContext]:
        views = []
        for field in fields(self):
            if issubclass(field.type, EndpointContext):
                views.append(getattr(self, field.name))
        return views

    def __post_init__(self):
        for view in self.views():
            view.service_context = self

    def clear_errors(self):
        for view in self.views():
            view.clear_error()
