# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from achievements_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(name='unique_drivers', autouse=True)
def _unique_drivers(mockserver):
    class UniqueDriversContext:
        def __init__(self):
            self.unique_driver_ids = {}

        def set_unique_driver(self, db_id, uuid, unique_driver_id):
            self.unique_driver_ids[
                'UniqueDriver:' + db_id + '_' + uuid
            ] = unique_driver_id

    context = UniqueDriversContext()
    context.set_unique_driver('test_db', 'test_uuid', 'test_unique_driver_id')

    def mock_retrieve_by_profiles(context, request):
        token = request.headers.get('X-Ya-Service-Ticket')
        if token is None:
            return mockserver.make_response('{"message": "unauthorized"}', 401)
        profile_id_in_set = request.json.get('profile_id_in_set')
        response_uniques = []
        for profile_id in profile_id_in_set:
            record = {'park_driver_profile_id': profile_id}
            key = 'UniqueDriver:' + profile_id
            if key in context.unique_driver_ids:
                record['data'] = {
                    'unique_driver_id': context.unique_driver_ids[key],
                }
            response_uniques.append(record)
        return {'uniques': response_uniques}

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _mock_retrieve_by_profiles(request):
        return mock_retrieve_by_profiles(context, request)

    return context


@pytest.fixture()
def driver_ui_profile_mock(mockserver):
    class Context:
        def __init__(self):
            self.v1_mode_get = None
            self.error_code = 404
            self.response = None

        def set_response(self, response):
            self.response = response
            self.error_code = None

        def set_error(self, code):
            self.error_code = code
            self.response = None

    context = Context()

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _wrapper(request):
        if context.error_code:
            return mockserver.make_response(status=context.error_code)
        return context.response

    context.v1_mode_get = _wrapper

    return context
