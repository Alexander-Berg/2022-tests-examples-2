import pytest

from . import performer


def default_tags():
    return ['test_tag_1']


@pytest.fixture(name='mock_driver_tags')
def _mock_driver_tags(mockserver):
    def handler(dbid_uuid=None, tags=None):
        dbid_uuid = (
            performer.default_dbid_uuid() if dbid_uuid is None else dbid_uuid
        )
        tags = default_tags() if tags is None else tags

        @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
        def _mock(request):
            assert request.json == dbid_uuid
            return {'tags': tags}

    return handler
