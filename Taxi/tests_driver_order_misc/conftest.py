# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=wrong-import-order
from driver_order_misc_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(name='protocol', autouse=True)
def _protocol(mockserver):
    class ProtocolContext:
        def __init__(self):
            self.voiceforwarding = None

        def set_voiceforwarding(self, voiceforwarding):
            self.voiceforwarding = voiceforwarding

    context = ProtocolContext()

    def mock_protocol_voiceforwarding(context, request):
        return context.voiceforwarding

    @mockserver.json_handler('/protocol/1.x/voiceforwarding')
    def _mock_protocol(request):
        arg_dict = {key: request.args[key] for key in request.args}
        assert arg_dict == {
            'apikey': 'ba4a40f6e11f46f6b20ee7fa6000565d',
            'clid': '100500',
            'for': 'driver',
            'orderid': '383e1b2cfeb03093accea972389eb8f4',
            'type': 'main',
        }
        return mock_protocol_voiceforwarding(context, request)

    return context


@pytest.fixture(name='parks', autouse=True)
def _parks(mockserver):
    class ProtocolContext:
        def __init__(self):
            self.data = None

        def set_driver_profiles_list(self, data):
            self.data = data

    context = ProtocolContext()

    def mock_parks_driver_profiles_list(context, request):
        return context.data

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        return mock_parks_driver_profiles_list(context, request)

    return context


@pytest.fixture(name='dit_efp')
def _dit_efp(mockserver):
    class MockContext:
        def __init__(self):
            self.token = None

            self.ticket_info = None

        def set_token(self, data):
            self.token = data

        def set_ticket_info(self, data):
            self.ticket_info = data

    context = MockContext()

    @mockserver.json_handler('/dit-efp/token')
    def _token(request):
        return context.token

    @mockserver.json_handler(
        '/dit-efp/api/pass-check-taxi/1.0/check-ticket-by-taxi',
    )
    def _check_ticket(request):
        return context.ticket_info

    return context


@pytest.fixture(name='dit_mo')
def _dit_mo(mockserver):
    class MockContext:
        def __init__(self):
            self.tokens = None
            self.ticket_info = None

        def set_tokens(self, data):
            self.tokens = data

        def set_ticket_info(self, data):
            self.ticket_info = data

    context = MockContext()

    @mockserver.json_handler('/dit-mo/api/v2/account/login')
    def _login(request):
        return context.tokens

    @mockserver.json_handler('/dit-mo/api/v2/account/refreshToken')
    def _refresh_tokens(request):
        return context.tokens

    @mockserver.json_handler('/dit-mo/api/v2/token/permits')
    def _permits(request):
        return context.ticket_info

    return context


@pytest.fixture(name='driver_trackstory')
def _driver_trackstory(mockserver):
    @mockserver.json_handler('/driver-trackstory/position')
    def _token(request):
        return {
            'position': {'lon': 37.634555, 'lat': 55.751516, 'timestamp': 3},
            'type': 'raw',
        }


@pytest.fixture(autouse=True, name='driver_app_profiles')
def _driver_app_profile(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_get_driver_app(request):
        return {
            'profiles': [
                {'park_driver_profile_id': x, 'data': {'locale': 'en'}}
                for x in request.json['id_in_set']
            ],
        }

    return _mock_get_driver_app


@pytest.fixture(name='tags')
def _tags(mockserver):
    class MockContext:
        def __init__(self):
            self.udid = False

    context = MockContext()

    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        if context.udid:
            assert request.json['tags'] == [
                {
                    'name': 'tag_for_fun',
                    'match': {'id': 'unique_driver_id_1', 'ttl': 7200},
                },
            ]
        else:
            assert request.json['tags'] == [
                {
                    'name': 'tag_for_priority',
                    'match': {'id': 'park_id_1_driver_id_1', 'ttl': 10800},
                },
            ]
        return {'status': 'ok'}

    return context


@pytest.fixture(name='unique_drivers', autouse=True)
def _uniques(mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _unique_profiles(request):
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'dbid_uuid',
                    'data': {'unique_driver_id': 'unique_driver_id_1'},
                },
            ],
        }


@pytest.fixture(name='yamaps', autouse=True)
def mock_yamaps_default(load_json, yamaps):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        return load_json('yamaps_response.json')
