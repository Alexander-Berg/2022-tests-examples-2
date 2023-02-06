import pytest

CORRECT_RULE_ID = 'af31c824-066d-46df-0001-000000000001'
INCORRECT_RULE_ID = 'af31c824-066d-46df-9999-404404404404'


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas.sql',
    ],
)
@pytest.mark.parametrize(
    'request_dict, response_code, polygon',
    [
        (
            {
                'workshift_rule_id': CORRECT_RULE_ID,
                'workshift_rule_version': 1,
                'geoarea_id': {
                    'geoarea_type': 'logistic_supply',
                    'name': 'second',
                },
            },
            200,
            {
                'coordinates': [
                    [
                        {'lat': 80.0, 'lon': 10.0},
                        {'lat': 80.0, 'lon': 80.0},
                        {'lat': 10.0, 'lon': 80.0},
                        {'lat': 10.0, 'lon': 10.0},
                        {'lat': 80.0, 'lon': 10.0},
                    ],
                ],
            },
        ),
        (
            {
                'workshift_rule_id': INCORRECT_RULE_ID,
                'workshift_rule_version': 1,
                'geoarea_id': {
                    'geoarea_type': 'logistic_supply',
                    'name': 'second',
                },
            },
            404,
            {
                'code': 'not_found',
                'message': (
                    'polygon with given workshift_rule_id, '
                    'version and geoarea_id not found'
                ),
            },
        ),
    ],
)
async def test_polygon_info(
        taxi_logistic_supply_conductor,
        pgsql,
        request_dict,
        response_code,
        polygon,
):
    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/polygon/info', json=request_dict,
    )

    response_dict = response.json()
    assert response.status_code == response_code

    assert response_dict == polygon

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/remove',
        json={
            'workshift_rule_id': CORRECT_RULE_ID,
            'version': 1,
            'revision': 1,
        },
    )

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/version/polygon/info', json=request_dict,
    )
    assert response.status_code == 404
