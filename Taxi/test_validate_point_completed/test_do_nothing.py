import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils

HANDLER = '/scooters-ops/old-flow/v1/validation/point-visited'


OK_RESPONSE = {'code': 200, 'json': {}}
BAD_REQUEST_RESPONSE = {
    'code': 400,
    'json': {'code': '400', 'message': 'Какая-то ужасная ошибка'},
}


@common.TRANSLATIONS
@pytest.mark.parametrize(
    ['job_status', 'expected_response'],
    [
        pytest.param('performing', OK_RESPONSE),
        *[
            pytest.param(status, OK_RESPONSE)
            for status in ['completed', 'cancelled', 'failed']
        ],
        *[
            pytest.param(status, BAD_REQUEST_RESPONSE)
            for status in ['created', 'preparing', 'prepared', 'planned']
        ],
    ],
)
async def test_job_statuses(
        taxi_scooters_ops, pgsql, job_status, expected_response,
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
                            'status': job_status,
                            'type': 'do_nothing',
                            'typed_extra': {},
                        },
                    ],
                },
            ],
        },
    )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={
            'locale': 'ru-ru',
            'mission_id': 'mission_id_1',
            'cargo_point_id': 'cargo_point_id_scooter_1',
        },
    )

    assert resp.status_code == expected_response['code']
    assert resp.json() == expected_response['json']


@common.TRANSLATIONS
@pytest.mark.parametrize(
    ['point_status', 'expected_response'],
    [
        pytest.param('arrived', OK_RESPONSE),
        *[
            pytest.param(status, OK_RESPONSE)
            for status in ['visited', 'skipped', 'cancelled']
        ],
        *[
            pytest.param(status, BAD_REQUEST_RESPONSE)
            for status in ['created', 'preparing', 'prepared', 'planned']
        ],
    ],
)
async def test_point_statuses(
        taxi_scooters_ops, pgsql, point_status, expected_response,
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
                    'status': point_status,
                    'cargo_point_id': 'cargo_point_id_scooter_1',
                    'typed_extra': {'scooter': {'id': 'vehicle_id_1'}},
                    'jobs': [
                        {
                            'job_id': 'job_id_1',
                            'status': 'performing',
                            'type': 'do_nothing',
                            'typed_extra': {},
                        },
                    ],
                },
            ],
        },
    )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={
            'locale': 'ru-ru',
            'mission_id': 'mission_id_1',
            'cargo_point_id': 'cargo_point_id_scooter_1',
        },
    )

    assert resp.status_code == expected_response['code']
    assert resp.json() == expected_response['json']
