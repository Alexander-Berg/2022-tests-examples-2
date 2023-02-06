import pytest

from sandbox.projects.yabs.qa.tasks.YabsServerShmResourceGC import hamster


@pytest.mark.parametrize(("endpoint", "active_endpoint_resources", "expected"), [
    ({'resource_id': 1}, [1], True),
    ({'resource_id': 1}, [1, 2], True),
    ({'resource_id': 1}, [], False),
    ({'resource_id': 2}, [1], False),
])
def test_is_active_endpoint(endpoint, active_endpoint_resources, expected):
    assert hamster._is_active_endpoint(endpoint, active_endpoint_resources) == expected
