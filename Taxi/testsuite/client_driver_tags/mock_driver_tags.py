import json
from typing import Any
from typing import Dict
from typing import Optional

import pytest

import client_driver_tags.match_fbs as match_fbs

_SERVICE = '/driver-tags'
_V1_MATCH_PROFILE_URL = '/v1/drivers/match/profile'
_V2_MATCH_PROFILE_URL = '/v2/drivers/match/profile'
_V1_RETRIEVE_PROFILE_URL = '/v1/drivers/retrieve/profile'
_V1_MATCH_PROFILES_URL = '/v1/drivers/match/profiles'
_V1_MATCH_PROFILES_FBS_URL = '/v1/drivers/match/profiles_fbs'

_MATCH_MARKER = 'driver_tags_match'
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
#            udid='udid',
#        )

_ERROR_MARKER = 'driver_tags_error'
# Usage: @pytest.mark.driver_tags_error(
#            handler='/v1/drivers/match/profile',
#            error_code=500,
#            error_message={'message': 'Server error', 'code': '500'},
#        )


class DriverTagsContext:
    def __init__(self):
        self.tags_info = {}
        self.udids = {}
        self.errors = {}
        self.calls = {}

        self.v1_match_profile = None
        self.v1_match_profiles = None
        self.v2_match_profile = None

    def reset(self):
        self.tags_info = {}
        self.udids = {}
        self.errors = {}
        self.calls = {}

    def set_error(self, handler, error_code, error_message=None):
        self.errors[handler] = {
            'code': error_code,
            'message': error_message or {
                'message': 'Server error',
                'code': str(error_code),
            },
        }

    # TODO: method should be renamed, but there dependencies for many services
    def set_tags_info(self, dbid, uuid, tags=None, tags_info=None, udid=None):
        tags_info = tags_info or {}
        if tags:
            tags_info.update({tag: {} for tag in tags})
        self.tags_info[(dbid, uuid)] = tags_info
        self.udids[(dbid, uuid)] = udid

    def get_tags_info(self, dbid, uuid, topics=None):
        tags_info = self.tags_info.get((dbid, uuid), {})
        if topics is not None:
            tags_info = {
                tag: info
                for tag, info in tags_info.items()
                if ('topics' in info) and (set(info['topics']) & set(topics))
            }
        return tags_info

    def get_tags(self, dbid, uuid, topics=None):
        tags_info = self.get_tags_info(dbid, uuid, topics)
        return set(tags_info.keys())

    def get_udid(self, dbid, uuid):
        return self.udids.get((dbid, uuid))

    def add_calls(self, handler, calls=1):
        self.calls[handler] = self.calls.get(handler, 0) + calls

    def count_calls(self, handler: Optional[str] = None):
        if handler is None:
            return sum(self.calls.values())
        return self.calls.get(handler, 0)

    def has_calls(self, handler=None):
        return bool(self.count_calls(handler))


def pytest_configure(config):
    config.addinivalue_line('markers', f'{_MATCH_MARKER}: driver tags match')
    config.addinivalue_line('markers', f'{_ERROR_MARKER}: driver tags error')


@pytest.fixture(name='driver_tags_mocks')
def _driver_tags_mocks(mockserver):
    driver_tags_context = DriverTagsContext()

    @mockserver.json_handler(_SERVICE + _V1_MATCH_PROFILE_URL)
    def _mock_v1_match_profile(request):
        driver_tags_context.add_calls(_V1_MATCH_PROFILE_URL)
        if _V1_MATCH_PROFILE_URL in driver_tags_context.errors:
            error = driver_tags_context.errors[_V1_MATCH_PROFILE_URL]
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        request_json = json.loads(request.get_data())
        dbid = request_json['dbid']
        uuid = request_json['uuid']
        topics = request_json.get('topics')
        response_tags = driver_tags_context.get_tags(dbid, uuid, topics)

        return {'tags': list(response_tags)}

    @mockserver.json_handler(_SERVICE + _V2_MATCH_PROFILE_URL)
    def _mock_v2_match_profile(request):
        driver_tags_context.add_calls(_V2_MATCH_PROFILE_URL)
        if _V2_MATCH_PROFILE_URL in driver_tags_context.errors:
            error = driver_tags_context.errors[_V2_MATCH_PROFILE_URL]
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        request_json = json.loads(request.get_data())
        dbid = request_json['dbid']
        uuid = request_json['uuid']
        topics = request_json.get('topics')
        reveal_ttl = request_json.get('reveal_ttl', True)
        reveal_topics = request_json.get('reveal_topics', True)
        reveal_udid = request_json.get('reveal_udid', False)
        tags_info = driver_tags_context.get_tags_info(dbid, uuid, topics)

        response_tags = {}
        for tag, info in tags_info.items():
            tag_info = {}
            if 'ttl' in info and reveal_ttl:
                tag_info['ttl'] = info['ttl']
            if 'topics' in info and reveal_topics:
                tag_info['topics'] = info['topics']
            response_tags[tag] = tag_info
        response = {'tags': response_tags}
        if reveal_udid:
            udid = driver_tags_context.get_udid(dbid, uuid)
            if udid is not None:
                response['udid'] = udid
        return response

    def _match_profiles(
            tags_context: DriverTagsContext,
            request_json: Dict[str, Any],
            required_udid: bool,
    ) -> Dict[str, Any]:
        topics = request_json.get('topics')
        response_drivers = []
        for driver in request_json['drivers']:
            dbid = driver['dbid']
            uuid = driver['uuid']
            tags = tags_context.get_tags(dbid, uuid, topics)

            item = {'dbid': dbid, 'uuid': uuid, 'tags': list(tags)}
            if required_udid:
                udid = tags_context.get_udid(dbid, uuid)
                if udid is not None:
                    item['udid'] = udid
            response_drivers.append(item)

        return {'drivers': response_drivers}

    @mockserver.json_handler(_SERVICE + _V1_MATCH_PROFILES_URL)
    def _mock_v1_match_profiles(request):
        driver_tags_context.add_calls(_V1_MATCH_PROFILES_URL)
        if _V1_MATCH_PROFILES_URL in driver_tags_context.errors:
            error = driver_tags_context.errors[_V1_MATCH_PROFILES_URL]
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )
        request_json = json.loads(request.get_data())
        return _match_profiles(
            driver_tags_context, request_json, required_udid=False,
        )

    @mockserver.json_handler(_SERVICE + _V1_RETRIEVE_PROFILE_URL)
    def _mock_v1_retrieve_profile(request):
        driver_tags_context.add_calls(_V1_RETRIEVE_PROFILE_URL)
        if _V1_RETRIEVE_PROFILE_URL in driver_tags_context.errors:
            error = driver_tags_context.errors[_V1_RETRIEVE_PROFILE_URL]
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )
        request_json = json.loads(request.get_data())
        dbid = request_json['park_id']
        uuid = request_json['driver_profile_id']
        topics = request_json.get('topics')
        response_tags = driver_tags_context.get_tags(dbid, uuid, topics)
        return {'tags': list(response_tags)}

    @mockserver.json_handler(_SERVICE + _V1_MATCH_PROFILES_FBS_URL)
    def _mock_v1_match_profiles_fbs(request):
        driver_tags_context.add_calls(_V1_MATCH_PROFILES_FBS_URL)
        if _V1_MATCH_PROFILES_FBS_URL in driver_tags_context.errors:
            error = driver_tags_context.errors[_V1_MATCH_PROFILES_FBS_URL]
            # todo: consider correct fbs error code
            return mockserver.make_response(
                json=error['message'], status=error['code'],
            )

        request_json = match_fbs.unpack_profiles_fbs_request(
            request.get_data(),
        )
        response_json = _match_profiles(
            driver_tags_context, request_json, required_udid=True,
        )

        return mockserver.make_response(
            match_fbs.pack_profiles_fbs_response(response_json),
            content_type='application/x-flatbuffers',
            charset='utf-8',
        )

    driver_tags_context.v1_match_profile = _mock_v1_match_profile
    driver_tags_context.v1_match_profiles = _mock_v1_match_profiles
    driver_tags_context.v2_match_profile = _mock_v2_match_profile
    return driver_tags_context


@pytest.fixture(name='driver_tags_fixture', autouse=True)
def _driver_tags_fixture(driver_tags_mocks, request):
    driver_tags_mocks.reset()

    # If not set, driver profile will have no tags specified
    for marker in request.node.iter_markers(_MATCH_MARKER):
        if marker.kwargs:
            driver_tags_mocks.set_tags_info(**marker.kwargs)

    # If not set, driver profile will have no tags specified
    for marker in request.node.iter_markers(_ERROR_MARKER):
        if marker.kwargs:
            driver_tags_mocks.set_error(**marker.kwargs)

    yield driver_tags_mocks

    driver_tags_mocks.reset()
