import json

import pytest


_MATCH_MARKER = 'driver_tags_match'
_SERVICE = '/driver_tags'
_V1_MATCH_PROFILE_URL = '/v1/drivers/match/profile'
_V2_MATCH_PROFILE_URL = '/v2/drivers/match/profile'
_V1_MATCH_PROFILES_URL = '/v1/drivers/match/profiles'

# Usage: @pytest.mark.driver_tags_match(
#            dbid='dbid',
#            uuid='uuid',
#            tags=['tag', ...],
#            tags_info={
#                'tag': {
#                    'ttl': '2019-07-15T13:57:07.000+0000',
#                    'topics': ['topic'],
#                },
#            },
#        )


class DriverTagsContext:
    def __init__(self):
        self.tags_info = {}

    def reset(self):
        self.tags_info = {}

    def set_tags_info(self, dbid, uuid, tags=None, tags_info=None):
        tags_info = tags_info or {}
        if tags:
            tags_info.update({tag: {} for tag in tags})
        self.tags_info[(dbid, uuid)] = tags_info

    def get_tags_info(self, dbid, uuid, topics=None):
        tags_info = self.tags_info.get((dbid, uuid), {})
        if topics is not None:
            tags_info = {
                tag: info
                for tag, info in tags_info.items()
                if ('topics' in info) and (set(info['topics']) & topics)
            }
        return tags_info

    def get_tags(self, dbid, uuid, topics=None):
        tags_info = self.get_tags_info(dbid, uuid, topics)
        return set(tags_info.keys())


@pytest.fixture
def driver_tags_mocks(mockserver):
    driver_tags_context = DriverTagsContext()

    @mockserver.json_handler(_SERVICE + _V1_MATCH_PROFILE_URL)
    def mock_v1_match_profile(request):
        request_json = json.loads(request.get_data())
        dbid = request_json['dbid']
        uuid = request_json['uuid']
        topics = request_json.get('topics')
        response_tags = driver_tags_context.get_tags(dbid, uuid, topics)

        return {'tags': list(response_tags)}

    @mockserver.json_handler(_SERVICE + _V2_MATCH_PROFILE_URL)
    def mock_v2_match_profile(request):
        request_json = json.loads(request.get_data())
        dbid = request_json['dbid']
        uuid = request_json['uuid']
        topics = request_json.get('topics')
        tags_info = driver_tags_context.get_tags_info(dbid, uuid, topics)

        response_tags = {}
        for tag, info in tags_info.items():
            response_tags[tag] = {}
            if 'ttl' in info:
                response_tags[tag]['ttl'] = info['ttl']

        return {'tags': response_tags}

    @mockserver.json_handler(_SERVICE + _V1_MATCH_PROFILES_URL)
    def mock_v1_match_profiles(request):
        request_json = json.loads(request.get_data())
        topics = request_json.get('topics')
        response_drivers = []
        for driver in request_json['drivers']:
            dbid = driver['dbid']
            uuid = driver['uuid']
            tags = driver_tags_context.get_tags(dbid, uuid, topics)
            response_drivers.append(
                {'dbid': dbid, 'uuid': uuid, 'tags': list(tags)},
            )

        return {'drivers': response_drivers}

    return driver_tags_context


@pytest.fixture(autouse=True)
def driver_tags_fixture(driver_tags_mocks, request):
    driver_tags_mocks.reset()

    if request.node.get_marker(_MATCH_MARKER):
        # If not set, driver profile will have no tags specified
        for req in request.node.get_marker(_MATCH_MARKER):
            if req.kwargs:
                driver_tags_mocks.set_tags_info(**req.kwargs)

    yield driver_tags_mocks

    driver_tags_mocks.reset()
