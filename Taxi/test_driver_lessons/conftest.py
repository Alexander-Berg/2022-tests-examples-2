# pylint: disable=redefined-outer-name
import aiohttp.web
import pytest

from testsuite.utils import http

import driver_lessons.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['driver_lessons.generated.service.pytest_plugins']


@pytest.fixture
def make_dap_headers():
    def _make_headers(
            park_id,
            driver_id,
            additional_headers=None,
            app_version=None,
            app_platform=None,
    ):
        assert park_id and driver_id
        headers = {
            'Accept-Language': 'ru',
            'X-Request-Application-Version': app_version or '9.57',
            'X-Request-Platform': app_platform or 'android',
            'X-YaTaxi-Park-Id': park_id,
            'X-YaTaxi-Driver-Profile-Id': driver_id,
        }
        if not additional_headers:
            additional_headers = {}
        for key, value in additional_headers.items():
            headers[key] = value
        return headers

    return _make_headers


@pytest.fixture
def make_selfreg_headers():
    def _make_headers(
            additional_headers=None, app_version=None, app_platform=None,
    ):
        app_version = app_version or '9.57'
        headers = {
            'Accept-Language': 'ru',
            'User-Agent': f'Taximeter {app_version} (12345)',
        }
        if app_platform == 'ios':
            headers['User-Agent'] += ' ios'
        if not additional_headers:
            additional_headers = {}
        for key, value in additional_headers.items():
            headers[key] = value
        return headers

    return _make_headers


@pytest.fixture
def make_selfreg_params():
    def _make_params(token, additional_params=None):
        additional_params = additional_params or {}
        return {**additional_params, 'token': token}

    return _make_params


@pytest.fixture
def make_lesson_url():
    def _make_lesson_url(base_url, lesson_id, complete=False, reaction=False):
        lesson_url = f'{base_url}/{lesson_id}'
        if complete:
            return f'{lesson_url}/complete'
        if reaction:
            return f'{lesson_url}/reaction'
        return lesson_url

    return _make_lesson_url


@pytest.fixture(autouse=True)
def mock_selfreg_validate(mock_selfreg, load_json):
    @mock_selfreg('/internal/selfreg/v1/validate')
    async def _mock_selfreg_validate(request: http.Request):
        token = request.query.get('token')
        responses = load_json('selfreg_validate_responses.json')
        response = responses.get(token)
        if not response:
            return aiohttp.web.json_response(status=404)
        return response


@pytest.fixture(autouse=True)
def mock_fleet_parks_list(mockserver, load_json):
    parks_by_id = {park['id']: park for park in load_json('parks.json')}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock(request):
        park_ids = request.json['query']['park']['ids']
        return {
            'parks': [
                parks_by_id[park_id]
                for park_id in park_ids
                if park_id in parks_by_id
            ],
        }


@pytest.fixture
def mock_unique_drivers(mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    async def unique_driver_id_handler(request):
        profile_ids = request.json['profile_id_in_set']
        return {
            'uniques': [
                {
                    'data': {'unique_driver_id': profile_id},
                    'park_driver_profile_id': profile_id,
                }
                for profile_id in profile_ids
            ],
        }

    return unique_driver_id_handler
