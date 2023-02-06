from typing import TypeVar  # noqa: IS001

import testsuite.utils.callinfo as callinfo


class MockedHandlerContext:
    TResponse = TypeVar('TResponse')

    def __init__(
            self, handler: callinfo.AsyncCallQueue, response: TResponse = None,
    ):
        self.response = response
        self.handler: callinfo.AsyncCallQueue = handler
        self.image = 'short_payment_id.png'
