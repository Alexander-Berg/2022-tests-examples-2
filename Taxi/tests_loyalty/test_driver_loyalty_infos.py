import pytest

from . import utils as test_utils

CODEGEN_HANDLER_URL = 'driver/v1/loyalty/v1/infos'


@pytest.mark.parametrize(
    'position,expected_code,expected_response,with_priority',
    [
        (
            [37.1946401739712, 55.478983901730004],
            200,
            'expected_response1.json',
            False,
        ),
        ([39.590533, 55.733863], 200, 'expected_response2.json', False),
        ([37.590533, 59.733863], 200, 'expected_response3.json', False),
        (
            [37.1946401739712, 55.478983901730004],
            200,
            'expected_response4.json',
            True,
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.pgsql('loyalty', files=['loyalty_rewards.sql'])
@pytest.mark.experiments3(filename='loyalty_ui_statuses.json')
async def test_driver_loyalty_infos(
        taxi_loyalty,
        experiments3,
        load_json,
        position,
        expected_code,
        expected_response,
        with_priority,
        unique_drivers,
        mock_fleet_parks_list,
):
    experiments3.add_experiment(
        **test_utils.make_priority_experiment3(with_priority),
    )
    unique_drivers.set_unique_driver('driver_db_id1', 'driver_uuid1', '')
    response = await taxi_loyalty.post(
        CODEGEN_HANDLER_URL,
        json={'position': position, 'timezone': 'Europe/Moscow'},
        headers=test_utils.get_auth_headers(
            'driver_db_id1', 'driver_uuid1', 'Taximeter 8.80 (562)',
        ),
    )

    assert response.status_code == expected_code
    assert response.json() == load_json('response/' + expected_response)


@pytest.mark.parametrize(
    'position, expected_response, exp_clause_zone, add_exp_clause',
    [
        (
            [37.1946401739712, 55.478983901730004],
            'expected_response1.json',
            '',
            False,
        ),
        (
            [37.1946401739712, 55.478983901730004],
            'expected_response1.json',
            'kazan',
            False,
        ),
        (
            [37.1946401739712, 55.478983901730004],
            'expected_response4.json',
            'moscow',
            True,
        ),
        (
            [37.1946401739712, 55.478983901730004],
            'expected_response4.json',
            'br_tsentralnyj_fo',
            True,
        ),
        (
            [37.1946401739712, 55.478983901730004],
            'expected_response4.json',
            'br_russia',
            True,
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.pgsql('loyalty', files=['loyalty_rewards.sql'])
@pytest.mark.experiments3(filename='loyalty_ui_statuses.json')
async def test_driver_loyalty_infos_with_zones_kwarg(
        taxi_loyalty,
        experiments3,
        load_json,
        position,
        expected_response,
        unique_drivers,
        exp_clause_zone,
        add_exp_clause,
        mock_fleet_parks_list,
):
    clauses = None
    if add_exp_clause:
        clauses = [
            test_utils.get_priority_exp_zones_clause(exp_clause_zone, 90),
        ]

    experiments3.add_experiment(
        **test_utils.make_priority_exp3_wo_default(clauses),
    )
    unique_drivers.set_unique_driver('driver_db_id1', 'driver_uuid1', '')
    response = await taxi_loyalty.post(
        CODEGEN_HANDLER_URL,
        json={'position': position, 'timezone': 'Europe/Moscow'},
        headers=test_utils.get_auth_headers(
            'driver_db_id1', 'driver_uuid1', 'Taximeter 8.80 (562)',
        ),
    )

    assert response.status_code == 200
    assert response.json() == load_json('response/' + expected_response)
