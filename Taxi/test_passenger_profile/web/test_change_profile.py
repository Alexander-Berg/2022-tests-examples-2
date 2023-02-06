import aiohttp
from aiohttp import test_utils
import pytest

from passenger_profile.api import change_profile

DEFAULT_RATING = '4.87'


async def test_change_name(web_app_client: test_utils.TestClient):
    headers = {
        'X-Yandex-Uid': '10002',
        'X-Request-Application': (
            'app_ver3=34174,app_name=uber_android,'
            'app_build=release,platform_ver2=4,'
            'app_ver2=95,platform_ver1=12,app_ver1=4'
        ),
        'X-YaTaxi-Pass-Flags': 'phonish',
    }
    body = {'first_name': 'Лёша'}

    response = await web_app_client.patch(
        '/4.0/passenger-profile/v1/profile', json=body, headers=headers,
    )

    assert response.status == 200

    response_data = await response.json()

    assert response_data['first_name'] == 'Лёша'
    assert response_data['rating'] == '4.10'


@pytest.mark.config(PASSENGER_PROFILE_DEFAULT_RATING=DEFAULT_RATING)
async def test_change_name_profile_does_not_exist(
        web_app_client: test_utils.TestClient,
):
    """
    If a profile does not exist yet, we should insert it with the default
    rating value
    """

    headers = {
        'X-Yandex-Uid': '10002',
        'X-Request-Application': (
            'app_ver3=34174,app_name=yango_iphone,'
            'app_build=release,platform_ver2=4,'
            'app_ver2=95,platform_ver1=12,app_ver1=4'
        ),
        'X-YaTaxi-Pass-Flags': 'phonish',
    }

    body = {'first_name': 'Алекс'}

    response = await web_app_client.patch(
        '/4.0/passenger-profile/v1/profile', json=body, headers=headers,
    )
    assert response.status == 200

    response_data = await response.json()

    assert response_data['first_name'] == 'Алекс'
    assert response_data['rating'] == DEFAULT_RATING


async def test_remove_name(web_app_client: test_utils.TestClient):
    headers = {
        'X-Yandex-Uid': '10002',
        'X-Request-Application': (
            'app_ver3=34174,app_name=uber_android,'
            'app_build=release,platform_ver2=4,'
            'app_ver2=95,platform_ver1=12,app_ver1=4'
        ),
        'X-YaTaxi-Pass-Flags': 'phonish',
    }
    body = {'first_name': ''}
    response = await web_app_client.patch(
        '/4.0/passenger-profile/v1/profile', json=body, headers=headers,
    )

    assert response.status == 200

    response_data = await response.json()

    assert 'first_name' not in response_data
    assert response_data['rating'] == '4.10'


async def test_change_name_too_long(web_app_client: test_utils.TestClient):
    headers = {
        'X-Yandex-Uid': '10002',
        'X-Request-Application': (
            'app_ver3=34174,app_name=uber_android,'
            'app_build=release,platform_ver2=4,'
            'app_ver2=95,platform_ver1=12,app_ver1=4'
        ),
        'X-YaTaxi-Pass-Flags': 'phonish',
    }
    body = {'first_name': 'a' * 121}  # limit is 120
    response = await web_app_client.patch(
        '/4.0/passenger-profile/v1/profile', json=body, headers=headers,
    )

    assert response.status == 400

    response_data = await response.json()

    assert response_data['code'] == 'REQUEST_VALIDATION_ERROR'


@pytest.mark.parametrize(
    'body',
    [
        {},  # first name is required
        {'first_name': 'a' * 101},  # the length limit is 100 characters
        {'first_name': None},  # null is not permitted
    ],
)
async def test_change_name_validation_error(
        web_app_client: test_utils.TestClient, body,
):

    headers = {
        'X-Yandex-Uid': '10002',
        'X-Request-Application': (
            'app_ver3=34174,app_name=uber_android,'
            'app_build=release,platform_ver2=4,'
            'app_ver2=95,platform_ver1=12,app_ver1=4'
        ),
        'X-YaTaxi-Pass-Flags': 'phonish',
    }
    response = await web_app_client.patch(
        '/4.0/passenger-profile/v1/profile', json=body, headers=headers,
    )

    assert response.status == 400

    response_data = await response.json()

    assert response_data['code'] == 'REQUEST_VALIDATION_ERROR'


async def _request_internal_profile(
        web_app_client: test_utils.TestClient,
        add_passenger_profile_experiment,
        application: str,
        uid: str,
) -> aiohttp.ClientResponse:
    add_passenger_profile_experiment(yandex_uid=uid)
    query = {'yandex_uid': uid, 'application': application}
    response = await web_app_client.get(
        '/passenger-profile/v1/profile', params=query,
    )
    assert response.status == 200

    return response


@pytest.mark.config(PASSENGER_PROFILE_DEFAULT_RATING=DEFAULT_RATING)
@pytest.mark.pgsql(
    'passenger_profile', files=['pg_passenger_profile_bound_uids.sql'],
)
async def test_set_name_with_bound_uids(
        web_app_client: test_utils.TestClient,
        add_passenger_profile_experiment,
):
    """
    If a passenger sets a name in a portal account, we should update
    all bound accounts that don't have a name yet
    """
    bound_uids_with_empty_names = {'2', '3', '4'}
    bound_uids_with_names = {'5', '6'}
    bound_uids_with_no_profiles = {'7', '8'}

    bound_uids = {
        *bound_uids_with_names,
        *bound_uids_with_empty_names,
        *bound_uids_with_no_profiles,
    }

    headers = {
        'X-Yandex-Uid': '1',
        'X-Request-Application': (
            'app_ver3=34174,app_name=android,'
            'app_build=release,platform_ver2=4,'
            'app_ver2=95,platform_ver1=12,app_ver1=4'
        ),
        'X-YaTaxi-Pass-Flags': 'portal,ya-plus',
        'X-YaTaxi-Bound-Uids': ','.join(bound_uids),
    }
    new_name = 'Мишаня'
    body = {'first_name': new_name}

    response = await web_app_client.patch(
        '/4.0/passenger-profile/v1/profile', json=body, headers=headers,
    )

    assert response.status == 200
    response_data = await response.json()

    assert response_data['first_name'] == new_name

    # check that bound profiles were updated
    for bound_uid in bound_uids_with_empty_names:
        profile_response = await _request_internal_profile(
            web_app_client,
            add_passenger_profile_experiment,
            application='iphone',
            uid=bound_uid,
        )
        profile_response_data = await profile_response.json()
        assert profile_response_data['first_name'] == new_name

    # check that bound profile for other apps were left intact
    # and that
    for bound_uid in bound_uids:
        profile_response = await _request_internal_profile(
            web_app_client,
            add_passenger_profile_experiment,
            application='uber_android',
            uid=bound_uid,
        )
        profile_response_data = await profile_response.json()

        if bound_uid in bound_uids_with_no_profiles:
            assert 'first_name' not in profile_response_data
            assert profile_response_data['rating'] == DEFAULT_RATING
        else:
            assert profile_response_data['first_name'] != new_name

    # check that bound profiles with already set names were not updated
    for bound_uid in bound_uids_with_names:
        profile_response = await _request_internal_profile(
            web_app_client,
            add_passenger_profile_experiment,
            application='iphone',
            uid=bound_uid,
        )
        profile_response_data = await profile_response.json()

        assert profile_response_data['first_name'] != new_name

    # check that bound uids with no profiles were inserted with default rating
    for bound_uid in bound_uids_with_no_profiles:
        profile_response = await _request_internal_profile(
            web_app_client,
            add_passenger_profile_experiment,
            application='android',
            uid=bound_uid,
        )
        profile_response_data = await profile_response.json()
        assert profile_response_data['first_name'] == new_name
        assert profile_response_data['rating'] == DEFAULT_RATING

    # check that other profiles were left intact
    for uid in ['9', '10']:  # other person
        profile_response = await _request_internal_profile(
            web_app_client, add_passenger_profile_experiment, 'iphone', uid,
        )
        profile_response_data = await profile_response.json()

        assert profile_response_data['first_name'] != new_name


@pytest.mark.parametrize(
    ['raw', 'expected'],
    [
        (
            'app_ver3=34174,app_name=uber_android,'
            'app_build=release,platform_ver2=4,'
            'app_ver2=95,platform_ver1=12,app_ver1=4',
            'uber_android',
        ),
        (
            'app_ver3=34174,app_name=iphone,'
            'app_build=release,platform_ver2=4,'
            'app_ver2=95,platform_ver1=132,app_ver1=4',
            'iphone',
        ),
        ('app_name=mobileweb', 'mobileweb'),
        ('app_ver3=34174', None),
        ('=======', None),
        (',,,=', None),
        ('', None),
    ],
)
def test_parse_request_application(raw, expected):
    assert change_profile.parse_request_application(raw) == expected
