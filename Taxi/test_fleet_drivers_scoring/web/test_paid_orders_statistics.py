import pytest

from test_fleet_drivers_scoring import utils as global_utils
from test_fleet_drivers_scoring.web import defaults
from test_fleet_drivers_scoring.web import utils

ENDPOINT = 'v1/paid/drivers/scoring/orders-statistics/retrieve'


@pytest.mark.config(**defaults.SCORING_ENABLED_CONFIG1)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_ok.sql'])
@pytest.mark.parametrize(
    'check_id, expected_response',
    [
        (
            'req_done',
            {
                'response': {
                    'data': {
                        'first_and_last_order': {
                            'first_order_at': (
                                '2014-06-30T18:47:47.052000+04:00'
                            ),
                            'last_order_at': (
                                '2019-06-30T17:47:47.052000+03:00'
                            ),
                        },
                        'total_statistics': {
                            'begin_at': '2019-01-01T03:00:00+03:00',
                            'successful_orders_count': 10,
                            'driver_rejected_orders_count': 5,
                        },
                        'statistics_by_interval': [
                            {
                                'begin_at': '2020-02-01T03:00:00+03:00',
                                'end_at': '2020-03-01T03:00:00+03:00',
                                'tariffs_statistics': [
                                    {
                                        'tariff': 'econom',
                                        'successful_orders_count': 83,
                                        'driver_rejected_orders_count': 1,
                                    },
                                    {
                                        'tariff': 'comfort',
                                        'successful_orders_count': 1,
                                        'driver_rejected_orders_count': 1,
                                    },
                                ],
                            },
                        ],
                    },
                    'version': '1',
                },
            },
        ),
        ('req_no_orders_statistics', {}),
    ],
)
async def test_ok(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        check_id,
        expected_response,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}],
    )

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={'request_id': check_id},
        params={'park_id': 'park1'},
    )

    assert response.status == 200, response.text
    response_json = await response.json()
    assert global_utils.date_parsed(response_json) == global_utils.date_parsed(
        expected_response,
    )


@pytest.mark.config(**defaults.SCORING_ENABLED_CONFIG1)
@pytest.mark.parametrize(
    'db_state, status_code, expected_response',
    [
        (
            'test_pending.sql',
            409,
            {
                'code': '409',
                'message': 'Scoring request is not done. status=pending',
            },
        ),
        (None, 400, {'code': '400', 'message': 'Scoring request not found'}),
    ],
)
async def test_no_data(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        pgsql,
        load,
        db_state,
        status_code,
        expected_response,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}],
    )

    if db_state:
        global_utils.execute_file(pgsql, load, db_state)
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={'request_id': 'req1'},
        params={'park_id': 'park1'},
    )

    assert response.status == status_code, response.text
    response_json = await response.json()
    assert response_json == expected_response


@pytest.mark.parametrize(
    'config, park_id, response_fleet_parks, fleet_parks_call_number,'
    'expected_response',
    [
        (
            defaults.SCORING_ENABLED_CONFIG3,
            'park2',
            {'parks': [defaults.RESPONSE_FLEET_PARKS2]},
            0,
            {'code': '400', 'message': 'Scoring is disabled'},
        ),
        (
            defaults.SCORING_ENABLED_CONFIG2,
            'park4',
            {'parks': [defaults.RESPONSE_FLEET_PARKS3]},
            1,
            {'code': '400', 'message': 'Park park4 was not found'},
        ),
        (
            defaults.SCORING_ENABLED_CONFIG2,
            'park3',
            {'parks': [defaults.RESPONSE_FLEET_PARKS2]},
            0,
            {'code': '400', 'message': 'Scoring is disabled for park park3'},
        ),
    ],
)
async def test_scoring_disabled(
        taxi_fleet_drivers_scoring_web,
        taxi_config,
        _mock_fleet_parks,
        config,
        park_id,
        response_fleet_parks,
        fleet_parks_call_number,
        expected_response,
):
    taxi_config.set_values(config)
    _mock_fleet_parks.set_parks_list_responses([response_fleet_parks])

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={'request_id': 'req1'},
        params={'park_id': park_id},
    )

    assert _mock_fleet_parks.parks_list.times_called == fleet_parks_call_number

    assert response.status == 400, response.text
    response_json = await response.json()
    assert response_json == expected_response
