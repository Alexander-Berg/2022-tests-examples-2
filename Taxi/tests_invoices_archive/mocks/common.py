from typing import Callable, Optional, TypeVar  # noqa: IS001

import testsuite.utils.callinfo as callinfo
import testsuite.utils.http as utils_http


class MockedHandlerContext:
    TResponse = TypeVar('TResponse')

    def __init__(
            self,
            handler: callinfo.AsyncCallQueue,
            response: TResponse = None,
            response_func: Optional[
                Callable[[Optional[utils_http.Request]], TResponse]
            ] = None,
            status: Optional[int] = None,
    ):
        self.response = response
        self.handler = handler
        self.response_func = response_func
        self.status = status

    def get_response(self, request: Optional[utils_http.Request] = None):
        if self.response_func:
            return self.response_func(request)
        return self.response
