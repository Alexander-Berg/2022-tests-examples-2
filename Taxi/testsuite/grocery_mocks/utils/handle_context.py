from typing import Any
from typing import Dict
from typing import Optional

from . import helpers


class HandleContext:
    def __init__(self):
        self._check_body: Optional[Dict] = None
        self._check_headers: Optional[Dict] = None
        self.response: Optional[Any] = None
        self.status_code: int = 200
        self.times_called: int = 0

    @property
    def is_ok(self) -> bool:
        return self.status_code == 200

    def response_with(self, default: Dict) -> Dict:
        return {**default, **(self.response or {})}

    def check(self, headers=None, **kwargs):
        self.check_body(kwargs)
        self.check_headers(headers)

    def check_body(self, data):
        self._check_body = data

    def check_headers(self, data):
        self._check_headers = data

    def process(self, request_body, request_headers=None):
        self.times_called = self.times_called + 1

        if request_body is not None and self._check_body is not None:
            helpers.assert_dict_contains(request_body, self._check_body)

        if request_headers is not None and self._check_headers is not None:
            helpers.assert_dict_contains(request_headers, self._check_headers)

    def __call__(self, request):
        self.process(request.json, request.headers)

    def mock_response(self, **kwargs):
        self.response = kwargs
