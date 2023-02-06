import random

import pytest

from taxi.core import async
from taxi.internal import router


@pytest.mark.asyncenv('async')
@pytest.mark.parametrize(
    'sources',
    [
        [((35.0, 56.0), 42.0), ((35.2, 56.2), 56.0)],
        [((35.0, 56.0), 7.0), ((35.2, 56.2), 120.0), ((35.3, 56.3), 189.0)],
    ]
)
@pytest.inline_callbacks
def test_bulk_route_info_with_direction(patch, sources):
    _patch_route_request(patch)

    result = yield router.bulk_route_info_by_direction(sources, (35.1, 56.1))
    assert len(result) == len(sources)


@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_bulk_info_failed(patch):

    @patch('taxi.external.router.request')
    @async.inline_callbacks
    def get_router_response(
            points, output, jams=True, direction=None, locale='ru-RU',
            timeout=None, retries=False, log_extra=None):
        yield
        raise Exception

    sources = [((35.0, 56.0), 42.0), ((35.2, 56.2), 56.0)]
    with pytest.raises(router.RouterResponseError):
        yield router.bulk_route_info_by_direction(sources, (35.1, 56.1))


def _patch_route_request(patch):

    @patch('taxi.external.router.request')
    @async.inline_callbacks
    def get_router_response(
            points, output, jams=True, direction=None, locale='ru-RU',
            timeout=None, retries=False, log_extra=None):
        yield
        for point in points:
            assert isinstance(point, tuple)
            assert len(point) == 2
        time = random.randint(300, 1000)
        info = {'length': random.random() * 20,
                'time': time,
                'jams_time': time * 1.2}
        route = []
        async.return_value((info, route))
