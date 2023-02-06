import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils

HANDLER = '/scooters-ops/old-flow/v1/validation/point-visited'

TIME_NOW = '2022-02-14T12:00:00+0500'
TS_NOW = 1644822000


@common.TRANSLATIONS
@pytest.mark.config(
    SCOOTERS_OPS_BATTERY_CHANGE_VALIDATION={
        'validate_battery_level': {
            'max_sensor_delay_seconds': 60,
            'min_battery_charge': 75,
            'enabled': True,
        },
    },
)
@pytest.mark.parametrize(
    ['sensor', 'expected_response', 'expected_statuses', 'expected_history'],
    [
        pytest.param(
            None,
            {},
            {'point': 'visited', 'job': 'completed'},
            [{'type': 'job_completed'}, {'type': 'point_completed'}],
            id='no sensor',
        ),
        pytest.param(
            {'id': 2217, 'name': 'hood_open', 'value': None},
            {},
            {'point': 'visited', 'job': 'completed'},
            [{'type': 'job_completed'}, {'type': 'point_completed'}],
            id='no fuel_level sensor info',
        ),
        pytest.param(
            {
                'id': 2107,
                'name': 'fuel_level',
                'since': TS_NOW,
                'updated': TS_NOW,
                'value': 80,
            },
            {},
            {'point': 'visited', 'job': 'completed'},
            [{'type': 'job_completed'}, {'type': 'point_completed'}],
            id='battery level ok',
        ),
        pytest.param(
            {
                'id': 2107,
                'name': 'fuel_level',
                'since': TS_NOW,
                'updated': TS_NOW,
                'value': 48,
            },
            {
                'code': '400',
                'message': (
                    'Уровень заряда в замененном аккумуляторе 48%. '
                    'Вы точно заменили аккумулятор?'
                ),
            },
            {'point': 'arrived', 'job': 'performing'},
            [],
            id='sensor not actual',
        ),
        pytest.param(
            {
                'id': 2107,
                'name': 'fuel_level',
                'since': TS_NOW - 100,
                'updated': TS_NOW - 100,
                'value': 10,
            },
            {
                'code': '400',
                'message': (
                    'Информация о замененном аккумуляторе обновляется. '
                    'Пожалуйста, подождите'
                ),
            },
            {'point': 'arrived', 'job': 'performing'},
            [],
            id='sensor updated recently but value updated long time ago',
        ),
    ],
)
@pytest.mark.now(TIME_NOW)
async def test_validate_battery_level(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        stq,
        sensor,
        expected_response,
        expected_statuses,
        expected_history,
):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id_1',
            'status': 'performing',
            'points': [
                {
                    'point_id': 'point_id_1',
                    'type': 'scooter',
                    'status': 'arrived',
                    'cargo_point_id': 'cargo_point_id_scooter_1',
                    'typed_extra': {'scooter': {'id': 'vehicle_id_1'}},
                    'jobs': [
                        {
                            'job_id': 'job_id_1',
                            'status': 'performing',
                            'type': 'battery_exchange',
                            'typed_extra': {'vehicle_id': 'vehicle_id_1'},
                        },
                    ],
                },
            ],
        },
    )

    @mockserver.json_handler('/scooter-backend/api/taxi/car/telematics/state')
    def telematics_state_mock(request):
        return {'sensors': [sensor] if sensor else []}

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={
            'locale': 'ru-ru',
            'mission_id': 'mission_id_1',
            'cargo_point_id': 'cargo_point_id_scooter_1',
        },
    )
    job_status = db_utils.get_jobs(pgsql, ids=['job_id_1'], fields=['status'])[
        0
    ]['status']
    point_status = db_utils.get_points(
        pgsql, ids=['point_id_1'], fields=['status'],
    )[0]['status']

    assert telematics_state_mock.times_called == 1
    assert resp.json() == expected_response

    assert point_status == expected_statuses['point']
    assert job_status == expected_statuses['job']

    history = db_utils.get_history(pgsql, fields=['type'])
    assert history == expected_history


@pytest.mark.config(
    SCOOTERS_OPS_BATTERY_CHANGE_VALIDATION={
        'validate_battery_level': {
            'max_sensor_delay_seconds': 60,
            'min_battery_charge': 75,
            'enabled': True,
        },
    },
)
@pytest.mark.now(TIME_NOW)
async def test_idempotency(taxi_scooters_ops, pgsql, mockserver, stq):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id_1',
            'status': 'performing',
            'points': [
                {
                    'point_id': 'point_id_1',
                    'type': 'scooter',
                    'status': 'arrived',
                    'cargo_point_id': 'cargo_point_id_scooter_1',
                    'typed_extra': {'scooter': {'id': 'vehicle_id_1'}},
                    'jobs': [
                        {
                            'job_id': 'job_id_1',
                            'status': 'performing',
                            'type': 'battery_exchange',
                            'typed_extra': {'vehicle_id': 'vehicle_id_1'},
                        },
                    ],
                },
            ],
        },
    )

    @mockserver.json_handler('/scooter-backend/api/taxi/car/telematics/state')
    def telematics_state_mock(request):
        return {
            'sensors': [
                {
                    'id': 2107,
                    'name': 'fuel_level',
                    'since': TS_NOW,
                    'updated': TS_NOW,
                    'value': 80,
                },
            ],
        }

    resp1 = await taxi_scooters_ops.post(
        HANDLER,
        params={
            'locale': 'ru-ru',
            'mission_id': 'mission_id_1',
            'cargo_point_id': 'cargo_point_id_scooter_1',
        },
    )

    resp2 = await taxi_scooters_ops.post(
        HANDLER,
        params={
            'locale': 'ru-ru',
            'mission_id': 'mission_id_1',
            'cargo_point_id': 'cargo_point_id_scooter_1',
        },
    )

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert telematics_state_mock.times_called == 1

    history = db_utils.get_history(pgsql, fields=['type'])
    assert history == [{'type': 'job_completed'}, {'type': 'point_completed'}]
