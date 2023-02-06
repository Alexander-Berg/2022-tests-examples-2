import json

import pytest

from tests_contractor_profiles_manager import utils

PARK_ID = 'some_par'

PARK_ID2 = 'any_park_id'

AUTH_HEADERS = {
    'X-Yandex-UID': '1000',
    'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Park-Id': PARK_ID,
}

AUTH_HEADERS2 = {
    'X-Yandex-UID': '1000',
    'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Park-Id': PARK_ID2,
}

AUTH_HEADERS_TEAM = {
    'X-Yandex-UID': '1000',
    'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Park-Id': PARK_ID,
}

ENDPOINT = '/v1/hiring-type-restriction/retrieve'
AUTH_ENDPOINT = (
    '/fleet/contractor-profiles/v1/hiring-type-restriction/retrieve'
)


@pytest.mark.parametrize('endpoint', [ENDPOINT, AUTH_ENDPOINT])
@pytest.mark.parametrize(
    'in_dl,real_dl,current_status, expected_response',
    [
        (
            'dl1',
            'DL1',
            {
                'hiring_date': '2000-08-21T00:00:00.000',
                'hiring_type': 'commercial',
            },
            {
                'is_restricted': True,
                'available_hiring_type': 'commercial',
                'hiring_date': '2000-08-21T00:00:00+00:00',
                'is_warning_expected': False,
            },
        ),
        (
            'dl1',
            'DL1',
            {
                'hiring_date': '2000-08-21T00:00:00.000',
                'hiring_type': 'commercial_with_rent',
            },
            {
                'is_restricted': True,
                'available_hiring_type': 'commercial_with_rent',
                'hiring_date': '2000-08-21T00:00:00+00:00',
                'is_warning_expected': False,
            },
        ),
        (
            'dl1',
            'DL1',
            {'hiring_date': '2000-08-21T00:00:00.000'},
            {
                'is_restricted': False,
                'hiring_date': '2000-08-21T00:00:00+00:00',
                'is_warning_expected': False,
            },
        ),
        (
            # Cyrillic license
            'ОаКвЕр4Н',
            'OAKBEP4H',
            {'hiring_date': '2000-08-21T00:00:00.000'},
            {
                'is_restricted': False,
                'hiring_date': '2000-08-21T00:00:00+00:00',
                'is_warning_expected': False,
            },
        ),
    ],
)
async def test_same_license(
        taxi_contractor_profiles_manager,
        mockserver,
        in_dl,
        real_dl,
        current_status,
        expected_response,
        endpoint,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _driver_profiles_retrieve(request):
        assert request.json == {
            'id_in_set': ['some_par_some_did'],
            'projection': ['data.license', 'data.hiring_details'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'some_par_some_did',
                    'data': {
                        'full_name': {
                            'first_name': 'Кирилл',
                            'middle_name': 'Юрьевич',
                            'last_name': 'Зюганов',
                        },
                        'license': {'pd_id': 'license_pd_id'},
                        'hiring_details': current_status,
                        'created_date': '2000-08-21T00:00:00.000',
                    },
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    async def _licenses_retrieve(request):
        assert request.json == {
            'id': 'license_pd_id',
            'primary_replica': False,
        }
        return {'id': 'license_pd_id', 'value': real_dl}

    response = await taxi_contractor_profiles_manager.post(
        endpoint,
        headers=AUTH_HEADERS,
        params={'driver_profile_id': 'some_did'},
        json={'driver_license': in_dl},
    )
    assert response.status == 200, response.text
    assert response.json() == expected_response


@pytest.mark.parametrize('endpoint', [ENDPOINT, AUTH_ENDPOINT])
@pytest.mark.parametrize(
    'is_driver_rent,commercial_hiring,'
    'commercial_hiring_with_car,already_commercial,expected_response',
    [
        (
            False,
            False,
            False,
            False,
            {'is_restricted': False, 'is_warning_expected': False},
        ),
        (
            False,
            False,
            True,
            True,
            {
                'is_restricted': True,
                'available_hiring_type': 'commercial',
                'hiring_date': '2000-08-21T00:00:00+00:00',
                'is_warning_expected': False,
            },
        ),
        (
            False,
            True,
            False,
            True,
            {
                'is_restricted': True,
                'available_hiring_type': 'commercial',
                'hiring_date': '2000-08-21T00:00:00+00:00',
                'is_warning_expected': True,
                'name': 'Кирилл З.',
            },
        ),
        (
            True,
            True,
            False,
            False,
            {'is_restricted': False, 'is_warning_expected': False},
        ),
        (
            True,
            False,
            False,
            False,
            {'is_restricted': False, 'is_warning_expected': False},
        ),
        (
            True,
            False,
            True,
            True,
            {
                'is_restricted': True,
                'available_hiring_type': 'commercial_with_rent',
                'hiring_date': '2000-08-21T00:00:00+00:00',
                'is_warning_expected': True,
                'name': 'Кирилл З.',
            },
        ),
    ],
)
async def test_different_license(
        taxi_contractor_profiles_manager,
        mockserver,
        is_driver_rent,
        commercial_hiring,
        commercial_hiring_with_car,
        expected_response,
        already_commercial,
        endpoint,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _driver_profiles_retrieve(request):
        assert request.json == {
            'id_in_set': ['some_par_some_did'],
            'projection': ['data.license', 'data.hiring_details'],
        }
        if already_commercial:
            return {
                'profiles': [
                    {
                        'park_driver_profile_id': 'some_par_some_did',
                        'data': {
                            'license': {'pd_id': 'license_pd_id'},
                            'hiring_details': {
                                'hiring_date': '2000-08-21T00:00:00.000',
                                'hiring_type': 'commercial',
                            },
                        },
                    },
                ],
            }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'some_par_some_did',
                    'data': {'license': {'pd_id': 'license_pd_id'}},
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    async def _licenses_retrieve(request):
        assert request.json == {
            'id': 'license_pd_id',
            'primary_replica': False,
        }
        return {'id': 'license_pd_id', 'value': 'DL1'}

    @mockserver.json_handler('/fleet-parks/v1/parks/driver-hirings/list')
    async def _driver_hirings_list(request):
        assert request.json == {'query': {'park': {'ids': [PARK_ID]}}}
        return {
            'parks_driver_hirings': [
                {
                    'park_id': 'any_park_id',
                    'commercial_hiring': commercial_hiring,
                    'commercial_hiring_with_car': commercial_hiring_with_car,
                },
            ],
        }

    @mockserver.json_handler('/hiring-candidates/v1/driver-for-city')
    async def _driver_for_city(request):
        assert request.query == {'driver_license': 'DL2'}
        return {
            'driver_license': 'DL2',
            'phone': '79102923008',
            'name': 'Зюганов Кирилл Юрьевич',
            'car_number': 'Т228ТТ799',
            'is_rent': is_driver_rent,
            'created_dttm': '2000-08-21T00:00:00+00:00',
        }

    response = await taxi_contractor_profiles_manager.post(
        endpoint,
        headers=AUTH_HEADERS,
        params={'driver_profile_id': 'some_did'},
        json={'driver_license': 'dl2'},
    )
    assert response.status == 200, response.text
    assert response.json() == expected_response


@pytest.mark.parametrize('endpoint', [ENDPOINT, AUTH_ENDPOINT])
@pytest.mark.parametrize(
    'hiring_details,expected_response',
    [
        (
            {'hiring_type': 'commercial'},
            {
                'is_restricted': True,
                'available_hiring_type': 'commercial',
                'is_warning_expected': False,
            },
        ),
        (
            {'hiring_date': '2002-08-21T00:00:00+00:00'},
            {
                'is_restricted': False,
                'hiring_date': '2002-08-21T00:00:00+00:00',
                'is_warning_expected': False,
            },
        ),
        (
            {
                'hiring_date': '2002-08-21T00:00:00+00:00',
                'hiring_type': 'commercial',
            },
            {
                'is_restricted': True,
                'available_hiring_type': 'commercial',
                'hiring_date': '2002-08-21T00:00:00+00:00',
                'is_warning_expected': False,
            },
        ),
        (None, {'is_restricted': False, 'is_warning_expected': False}),
        (None, {'is_restricted': False, 'is_warning_expected': False}),
    ],
)
async def test_incomplete_driver_profiles(
        taxi_contractor_profiles_manager,
        mockserver,
        hiring_details,
        expected_response,
        endpoint,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _driver_profiles_retrieve(request):
        assert request.json == {
            'id_in_set': ['some_par_some_did'],
            'projection': ['data.license', 'data.hiring_details'],
        }
        profile = {
            'park_driver_profile_id': 'some_par_some_did',
            'data': {'license': {'pd_id': 'license_pd_id'}},
        }
        if hiring_details is not None:
            profile['data']['hiring_details'] = hiring_details
        return {'profiles': [profile]}

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    async def _licenses_retrieve(request):
        assert request.json == {
            'id': 'license_pd_id',
            'primary_replica': False,
        }
        return {'id': 'license_pd_id', 'value': 'DL1'}

    response = await taxi_contractor_profiles_manager.post(
        endpoint,
        headers=AUTH_HEADERS,
        params={'driver_profile_id': 'some_did'},
        json={'driver_license': 'dl1'},
    )
    assert response.status == 200, response.text
    assert response.json() == expected_response


@pytest.mark.parametrize('endpoint', [ENDPOINT, AUTH_ENDPOINT])
async def test_no_license(
        taxi_contractor_profiles_manager, mockserver, endpoint,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _driver_profiles_retrieve(request):
        assert request.json == {
            'id_in_set': ['some_par_some_did'],
            'projection': ['data.license', 'data.hiring_details'],
        }
        profile = {
            'park_driver_profile_id': 'some_par_some_did',
            'data': {'created_date': '2001-08-21T15:32:23.234'},
        }
        return {'profiles': [profile]}

    @mockserver.json_handler('/fleet-parks/v1/parks/driver-hirings/list')
    async def _driver_hirings_list(request):
        assert request.json == {'query': {'park': {'ids': [PARK_ID]}}}
        return {
            'parks_driver_hirings': [
                {
                    'park_id': 'any_park_id',
                    'commercial_hiring': True,
                    'commercial_hiring_with_car': False,
                },
            ],
        }

    @mockserver.json_handler('/hiring-candidates/v1/driver-for-city')
    async def _driver_for_city(request):
        assert request.query == {'driver_license': 'DL1'}
        return {
            'driver_license': 'DL1',
            'phone': '79102923008',
            'name': 'Зюганов Кирилл Юрьевич',
            'car_number': 'Т228ТТ799',
            'is_rent': False,
            'created_dttm': '2000-08-21T00:00:00+00:00',
        }

    response = await taxi_contractor_profiles_manager.post(
        endpoint,
        headers=AUTH_HEADERS,
        params={'driver_profile_id': 'some_did'},
        json={'driver_license': 'dl1'},
    )
    assert response.status == 200, response.text
    assert response.json() == {
        'is_restricted': True,
        'available_hiring_type': 'commercial',
        'hiring_date': '2000-08-21T00:00:00+00:00',
        'is_warning_expected': True,
        'name': 'Кирилл З.',
    }


@pytest.mark.parametrize(
    'is_driver_rent,commercial_hiring,'
    'commercial_hiring_with_car,expected_response',
    [
        (
            True,
            False,
            True,
            {
                'is_restricted': True,
                'available_hiring_type': 'commercial',
                'hiring_date': '2000-08-21T00:00:00+00:00',
                'is_warning_expected': False,
            },
        ),
    ],
)
async def test_by_yandex_team(
        taxi_contractor_profiles_manager,
        mockserver,
        is_driver_rent,
        commercial_hiring,
        commercial_hiring_with_car,
        expected_response,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _driver_profiles_retrieve(request):
        assert request.json == {
            'id_in_set': ['some_par_some_did'],
            'projection': ['data.license', 'data.hiring_details'],
        }
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'some_par_some_did',
                    'data': {
                        'license': {'pd_id': 'license_pd_id'},
                        'hiring_details': {
                            'hiring_date': '2000-08-21T00:00:00.000',
                            'hiring_type': 'commercial',
                        },
                    },
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    async def _licenses_retrieve(request):
        assert request.json == {
            'id': 'license_pd_id',
            'primary_replica': False,
        }
        return {'id': 'license_pd_id', 'value': 'DL1'}

    @mockserver.json_handler('/fleet-parks/v1/parks/driver-hirings/list')
    async def _driver_hirings_list(request):
        assert request.json == {'query': {'park': {'ids': [PARK_ID]}}}
        return {
            'parks_driver_hirings': [
                {
                    'park_id': 'any_park_id',
                    'commercial_hiring': commercial_hiring,
                    'commercial_hiring_with_car': commercial_hiring_with_car,
                },
            ],
        }

    @mockserver.json_handler('/hiring-candidates/v1/driver-for-city')
    async def _driver_for_city(request):
        assert request.query == {'driver_license': 'DL2'}
        return {
            'driver_license': 'DL2',
            'phone': '79102923008',
            'name': 'Зюганов Кирилл Юрьевич',
            'car_number': 'Т228ТТ799',
            'is_rent': is_driver_rent,
            'created_dttm': '2000-08-21T00:00:00+00:00',
        }

    response = await taxi_contractor_profiles_manager.post(
        AUTH_ENDPOINT,
        headers=AUTH_HEADERS_TEAM,
        params={'driver_profile_id': 'some_did'},
        json={'driver_license': 'dl2'},
    )
    assert response.status == 200, response.text
    assert response.json() == expected_response


DRIVER_LICENSE = '64СС070313'


def make_hiring_candidates_response(is_rent: bool):
    return {
        'driver_license': DRIVER_LICENSE,
        'phone': '79102923008',
        'name': 'Петров Иван Аркадьевич',
        'car_number': 'Т228ТТ799',
        'is_rent': is_rent,
        'created_dttm': '2019-11-27T13:41:36+00:00',
    }


@pytest.mark.parametrize('endpoint', [ENDPOINT, AUTH_ENDPOINT])
@pytest.mark.parametrize(
    [
        'parks_driver_hirings_list_response',
        'hiring_candidates_response',
        'expected_code',
        'expected_response',
    ],
    [
        (
            {
                'parks_driver_hirings': [
                    {
                        'park_id': 'any_park_id',
                        'commercial_hiring': True,
                        'commercial_hiring_with_car': False,
                    },
                ],
            },
            make_hiring_candidates_response(is_rent=False),
            200,
            {
                'is_restricted': True,
                'available_hiring_type': 'commercial',
                'name': 'Иван П.',
                'hiring_date': '2019-11-27T13:41:36+00:00',
                'is_warning_expected': True,
            },
        ),
        (
            {
                'parks_driver_hirings': [
                    {
                        'park_id': 'any_park_id',
                        'commercial_hiring': False,
                        'commercial_hiring_with_car': True,
                    },
                ],
            },
            make_hiring_candidates_response(is_rent=True),
            200,
            {
                'is_restricted': True,
                'available_hiring_type': 'commercial_with_rent',
                'name': 'Иван П.',
                'hiring_date': '2019-11-27T13:41:36+00:00',
                'is_warning_expected': True,
            },
        ),
        (
            {
                'parks_driver_hirings': [
                    {
                        'park_id': 'any_park_id',
                        'commercial_hiring': False,
                        'commercial_hiring_with_car': False,
                    },
                ],
            },
            make_hiring_candidates_response(is_rent=True),
            200,
            {'is_restricted': False, 'is_warning_expected': False},
        ),
        (
            {'parks_driver_hirings': []},
            make_hiring_candidates_response(is_rent=False),
            200,
            {'is_restricted': False, 'is_warning_expected': False},
        ),
        (
            {
                'parks_driver_hirings': [
                    {
                        'park_id': 'any_park_id',
                        'commercial_hiring': True,
                        'commercial_hiring_with_car': False,
                    },
                ],
            },
            make_hiring_candidates_response(is_rent=True),
            200,
            {'is_restricted': False, 'is_warning_expected': False},
        ),
        (
            {
                'parks_driver_hirings': [
                    {
                        'park_id': 'any_park_id',
                        'commercial_hiring': False,
                        'commercial_hiring_with_car': True,
                    },
                ],
            },
            make_hiring_candidates_response(is_rent=False),
            200,
            {'is_restricted': False, 'is_warning_expected': False},
        ),
        (
            {
                'parks_driver_hirings': [
                    {
                        'park_id': 'any_park_id',
                        'commercial_hiring': False,
                        'commercial_hiring_with_car': True,
                    },
                ],
            },
            make_hiring_candidates_response(is_rent=False),
            200,
            {'is_restricted': False, 'is_warning_expected': False},
        ),
    ],
)
async def test_hiring_type_restrictions_no_driver_id(
        taxi_contractor_profiles_manager,
        mockserver,
        parks_driver_hirings_list_response,
        hiring_candidates_response,
        expected_code,
        expected_response,
        endpoint,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/driver-hirings/list')
    def _mock_parks_driver_hirings_list(request):
        return parks_driver_hirings_list_response

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        return {'parks': [utils.NICE_PARK]}

    @mockserver.json_handler('/hiring-candidates/v1/driver-for-city')
    def _mock_hiring_candidates(request):
        return hiring_candidates_response

    response = await taxi_contractor_profiles_manager.post(
        endpoint,
        headers=AUTH_HEADERS,
        json={'driver_license': DRIVER_LICENSE},
    )

    assert response.status_code == expected_code, response.text
    if response.status_code == 200:
        assert _mock_parks_driver_hirings_list.times_called == 1

    assert response.json() == expected_response


@pytest.mark.parametrize('endpoint', [ENDPOINT, AUTH_ENDPOINT])
async def test_hiring_candidates_bad_response(
        taxi_contractor_profiles_manager, mockserver, endpoint,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/driver-hirings/list')
    def mock_parks_driver_hirings_list(request):
        return {
            'parks_driver_hirings': [
                {
                    'park_id': 'any_park_id',
                    'commercial_hiring': False,
                    'commercial_hiring_with_car': True,
                },
            ],
        }

    @mockserver.json_handler('/hiring-candidates/v1/driver-for-city')
    def mock_hiring_candidates(request):
        return mockserver.make_response(
            response=json.dumps(
                {
                    'message': (
                        'No driver license in this city in active period'
                    ),
                    'code': 'DRIVER_LICENSE_IN_CITY_NOT_FOUND',
                    'details': {'occurred_at': '2019-12-27T23:00:00+0000'},
                },
            ),
            status=404,
        )

    response = await taxi_contractor_profiles_manager.post(
        endpoint,
        headers=AUTH_HEADERS2,
        json={'driver_license': DRIVER_LICENSE},
    )

    assert response.status_code == 200
    assert mock_hiring_candidates.times_called == 1
    assert mock_parks_driver_hirings_list.times_called == 1

    assert response.json() == {
        'is_restricted': False,
        'is_warning_expected': False,
    }
