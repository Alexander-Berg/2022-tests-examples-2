import json

import pytest

from tests_superapp_misc.test_availability import consts
from tests_superapp_misc.test_availability import helpers


@pytest.mark.experiments3(
    filename='exp3_superapp_masstransit_availability.json',
)
@pytest.mark.parametrize(
    ['is_available', 'expected_result'],
    [
        (False, helpers.masstransit_ok_response(is_available=False)),
        (True, helpers.masstransit_ok_response(is_available=True)),
    ],
)
async def test_masstransit_availability(
        taxi_superapp_misc, mockserver, is_available, expected_result,
):
    @mockserver.json_handler('/masstransit/masstransit/v1/availability')
    def _availability(request):
        assert request.headers['X-YaTaxi-UserId'] == 'user_id'
        assert json.loads(request.get_data()) == {
            'position': [37.590533, 55.733863],
        }
        return {'available': is_available}

    response = await taxi_superapp_misc.post(
        consts.URL,
        helpers.build_payload(),
        headers={'X-YaTaxi-UserId': 'user_id'},
    )
    assert response.status_code == 200
    assert response.json() == expected_result


@pytest.mark.experiments3(
    filename='exp3_superapp_masstransit_availability.json',
)
@pytest.mark.parametrize('err_class', ['TimeoutError', 'NetworkError'])
async def test_masstransit_availability_errors(
        taxi_superapp_misc, mockserver, err_class,
):
    @mockserver.json_handler('/masstransit/masstransit/v1/availability')
    def _availability(request):
        raise getattr(mockserver, err_class)

    response = await taxi_superapp_misc.post(
        consts.URL,
        helpers.build_payload(),
        headers={'X-YaTaxi-UserId': 'user_id'},
    )
    assert response.status_code == 200
    assert response.json() == helpers.ok_response(True, True)


@pytest.mark.experiments3(
    filename='exp3_superapp_masstransit_availability.json',
)
@pytest.mark.parametrize(
    ['exp_multipoint', 'expected_result'],
    [
        pytest.param(
            False,
            helpers.masstransit_ok_response(is_available=False),
            id='Available only on waypoints, exp: false, expected: false',
        ),
        pytest.param(
            True,
            helpers.masstransit_ok_response(is_available=True),
            id='Available only on waypoints, exp: true, expected: true',
        ),
    ],
)
async def test_masstransit_multipoint_availability(
        taxi_superapp_misc,
        mockserver,
        experiments3,
        exp_multipoint,
        expected_result,
):
    @mockserver.json_handler('/masstransit/masstransit/v1/availability')
    def _availability(request):
        assert request.headers['X-YaTaxi-UserId'] == 'user_id'
        is_available = (
            json.loads(request.get_data())['position']
            == consts.ADDITIONAL_POSITION
        )
        return {'available': is_available}

    helpers.add_exp_multipoint(experiments3, exp_multipoint)

    response = await taxi_superapp_misc.post(
        consts.URL,
        helpers.build_payload(state=helpers.build_state()),
        headers={'X-YaTaxi-UserId': 'user_id'},
    )
    assert response.status_code == 200
    assert response.json() == expected_result
