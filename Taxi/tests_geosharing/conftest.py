# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=C5521
from geosharing_plugins import *  # noqa: F403 F401
import pytest

from tests_geosharing.mock_user_tracker import UserTrackerFixture


@pytest.fixture
def user_tracker(mockserver):
    fixture = UserTrackerFixture(mockserver)
    yield fixture
    fixture.finalize()


@pytest.fixture(autouse=True)
def _yagr(mockserver):
    @mockserver.handler('/yagr/pipeline/go-users/position/store')
    def _(request):
        return mockserver.make_response('Ok', 200)
