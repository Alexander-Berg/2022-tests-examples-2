import json

import pytest

from tests_driver_work_modes import utils


ENDPOINT_URL = 'v1/parks/driver-profiles/hiring-type-restriction'

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
                'restricted': True,
                'available_hiring_type': 'commercial',
                'driver_info': {
                    'name': 'Иван П.',
                    'hiring_date': '2019-11-27T13:41:36+00:00',
                },
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
                'restricted': True,
                'available_hiring_type': 'commercial_with_rent',
                'driver_info': {
                    'name': 'Иван П.',
                    'hiring_date': '2019-11-27T13:41:36+00:00',
                },
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
            {'restricted': False},
        ),
        (
            {'parks_driver_hirings': []},
            make_hiring_candidates_response(is_rent=False),
            404,
            {
                'code': 'parks_driver_hirings_not_found',
                'message': 'Park driver hirings not found',
            },
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
            {'restricted': False},
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
            {'restricted': False},
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
            {'restricted': False},
        ),
    ],
)
async def test_hiring_type_restrictions(
        taxi_driver_work_modes,
        mockserver,
        parks_driver_hirings_list_response,
        hiring_candidates_response,
        expected_code,
        expected_response,
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

    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={'driver_license': DRIVER_LICENSE, 'park_id': 'any_park_id'},
    )

    assert response.status_code == expected_code, response.text
    if response.status_code == 200:
        assert _mock_parks_driver_hirings_list.times_called == 1

    assert response.json() == expected_response


async def test_hiring_candidates_bad_response(
        taxi_driver_work_modes, mockserver,
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

    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={'driver_license': DRIVER_LICENSE, 'park_id': 'any_park_id'},
    )

    assert response.status_code == 200
    assert mock_hiring_candidates.times_called == 1
    assert mock_parks_driver_hirings_list.times_called == 1

    assert response.json() == {'restricted': False}


async def test_hiring_candidates_unavailable(
        taxi_driver_work_modes, mockserver,
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
            response='service unavailable', status=500,
        )

    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={'driver_license': DRIVER_LICENSE, 'park_id': 'any_park_id'},
    )

    assert response.status_code == 200
    assert mock_hiring_candidates.times_called == 3
    assert mock_parks_driver_hirings_list.times_called == 1

    assert response.json() == {'restricted': False}
