import json
from typing import Optional

import pytest


_SERVICE = '/driver-ratings'
_V2_DRIVER_RATING_URL = '/v2/driver/rating'
_V2_DRIVER_RATING_BATCH_RETRIEVE_URL = '/v2/driver/rating/batch-retrieve'

_RATINGS_MARKER = 'driver_ratings'
# Usage: @pytest.mark.driver_ratings(
#            ratings=[
#                {'unique_driver_id': 'udid1', 'rating': 4.912},
#                ...
#            ],
#            default_rating=5.0,
#        )

_DEFAULT_RATING = 5.0


class DriverRatingsContext:
    def __init__(self):
        self.ratings = {}
        self.default_rating = _DEFAULT_RATING
        self.calls = {}
        self.v2_driver_rating = None
        self.v2_driver_rating_batch_retrieve = None

    def reset(self):
        self.ratings = {}
        self.default_rating = _DEFAULT_RATING
        self.calls = {}
        self.v2_driver_rating = None
        self.v2_driver_rating_batch_retrieve = None

    def set_ratings(self, ratings, default_rating=None):
        for row in ratings:
            udid = row['unique_driver_id']
            rating = row['rating']
            self.ratings[udid] = rating
        if default_rating is not None:
            self.default_rating = default_rating

    def get_rating(self, udid):
        return (
            self.ratings.get(udid) if udid in self.ratings else _DEFAULT_RATING
        )

    def add_calls(self, handler, calls=1):
        self.calls[handler] = self.calls.get(handler, 0) + calls

    def count_calls(self, handler: Optional[str] = None):
        if handler is None:
            return sum(self.calls.values())
        return self.calls.get(handler, 0)

    def has_calls(self, handler=None):
        return bool(self.count_calls(handler))


def pytest_configure(config):
    config.addinivalue_line('markers', f'{_RATINGS_MARKER}: driver ratings')


@pytest.fixture(name='driver_ratings_mocks')
def _driver_ratings_mocks(mockserver):
    driver_ratings_context = DriverRatingsContext()

    @mockserver.json_handler(_SERVICE + _V2_DRIVER_RATING_URL)
    def _mock_v2_driver_rating(request):
        driver_ratings_context.add_calls(_V2_DRIVER_RATING_URL)

        udid = request.query.get('unique_driver_id')
        rating = driver_ratings_context.get_rating(udid)

        return {'unique_driver_id': udid, 'rating': str(rating)}

    @mockserver.json_handler(_SERVICE + _V2_DRIVER_RATING_BATCH_RETRIEVE_URL)
    def _mock_v2_driver_rating_batch_retrieve(request):
        driver_ratings_context.add_calls(_V2_DRIVER_RATING_BATCH_RETRIEVE_URL)

        request_json = json.loads(request.get_data())
        udids = request_json['unique_driver_ids']
        udids.sort()

        if len(udids) != len(set(udids)):
            return mockserver.make_response(
                json={
                    'code': 400,
                    'message': 'All items in unique_driver_ids must be unique',
                },
                status=400,
            )

        ratings = []
        for udid in udids:
            rating = driver_ratings_context.get_rating(udid)
            ratings.append({'unique_driver_id': udid, 'rating': str(rating)})

        return {'ratings': ratings}

    driver_ratings_context.v2_driver_rating = _mock_v2_driver_rating
    driver_ratings_context.v2_driver_rating_batch_retrieve = (
        _mock_v2_driver_rating_batch_retrieve
    )
    return driver_ratings_context


@pytest.fixture(name='driver_ratings_fixture', autouse=True)
def _driver_ratings_fixture(driver_ratings_mocks, request):
    driver_ratings_mocks.reset()

    # If not set, unique driver will have default rating
    for marker in request.node.iter_markers(_RATINGS_MARKER):
        if marker.kwargs:
            driver_ratings_mocks.set_ratings(**marker.kwargs)

    yield driver_ratings_mocks

    driver_ratings_mocks.reset()
