# pylint: disable=redefined-outer-name
import dataclasses
from typing import Callable

import pytest

import taxi_loyalty_py3.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
pytest_plugins = ['taxi_loyalty_py3.generated.service.pytest_plugins']

DRIVER_RATINGS_URL = '/driver-ratings/v1/driver/ratings/retrieve'


@pytest.fixture(name='mock_driver_ratings')
def mock_driver_ratings_factory(mockserver):
    @dataclasses.dataclass
    class StatefulHandler:
        handler_mock: Callable
        _rating: float = 5.0
        _status_code: int = 200

        @property
        def rating(self):
            return self._rating

        @rating.setter
        def rating(self, rating):
            self._rating = rating

        @property
        def status_code(self):
            return self._status_code

        @status_code.setter
        def status_code(self, status_code):
            self._status_code = status_code

    @mockserver.json_handler(DRIVER_RATINGS_URL)
    def handler_mock(request):
        return mockserver.make_response(
            status=handler.status_code,
            json={
                'ratings': [
                    {'unique_driver_id': x, 'data': {'rating': handler.rating}}
                    for x in request.json['id_in_set']
                ],
            },
        )

    handler = StatefulHandler(handler_mock)
    return handler
