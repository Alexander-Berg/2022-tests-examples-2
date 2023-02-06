import dateutil.parser
import pytest

from tests_plugins import utils

from . import utils as test_utils

CODEGEN_HANDLER_URL = 'driver/v1/loyalty/v1/details'


# pylint: disable=too-many-arguments
# pylint: disable=invalid-name, too-many-arguments
@pytest.mark.parametrize(
    'position,time,wallet,ts_from,ts_to,timezone,user_agent,unique_driver_id,'
    'expected_code,expected_response,with_priority',
    [
        (
            [37.590533, 55.733863],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000001',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 8.80 (562)',
            '000000000000000000000001',
            200,
            'expected_response1.json',
            False,
        ),
        (
            [37.590533, 55.733863],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000002',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 8.80 (562)',
            '000000000000000000000001',
            200,
            'expected_response2.json',
            False,
        ),
        (
            [37.485333, 54.122222],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000001',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Europe/Moscow',
            'Taximeter 8.80 (562)',
            '000000000000000000000001',
            200,
            'expected_response3.json',
            False,
        ),
        (
            [37.590533, 55.733863],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000012',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 8.80 (562)',
            '000000000000000000000012',
            200,
            'expected_response4.json',
            False,
        ),
        (
            [37.485333, 54.122222],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000012',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Europe/Moscow',
            'Taximeter 8.80 (562)',
            '000000000000000000000012',
            200,
            'expected_response5.json',
            False,
        ),
        (
            [37.485333, 54.122222],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000012',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Europe/Kaliningrad',
            'Taximeter 8.80 (562)',
            '000000000000000000000012',
            200,
            'expected_response6.json',
            False,
        ),
        (
            [37.590533, 55.733863],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000013',
            '2019-02-28T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 8.80 (562)',
            '000000000000000000000013',
            200,
            'expected_response7.json',
            False,
        ),
        (
            [37.590533, 55.733863],
            '2019-04-01T01:10:00+0500',
            '000000000000000000000013',
            '2019-02-28T21:00:00+0000',
            '2019-03-31T20:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 8.80 (562)',
            '000000000000000000000013',
            200,
            'expected_response7.json',
            False,
        ),
        (
            [37.590533, 55.733863],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000001',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 8.79 (562)',
            '000000000000000000000001',
            200,
            'expected_response8.json',
            False,
        ),
        (
            [37.590533, 59.733863],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000001',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 8.80 (562)',
            '000000000000000000000001',
            200,
            'expected_response9.json',
            False,
        ),
        (
            [37.590533, 55.733863],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000016',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 8.80 (562)',
            '000000000000000000000016',
            200,
            'expected_response10.json',
            False,
        ),
        (
            [37.590533, 55.733863],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000017',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 8.80 (562)',
            '000000000000000000000017',
            200,
            'expected_response11.json',
            False,
        ),
        (
            [37.590533, 59.733863],
            '2019-06-01T06:10:00+0500',
            '100000000000000000000001',
            '2019-05-31T21:00:00+0000',
            '2019-06-01T01:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 9.10 (562)',
            '100000000000000000000001',
            200,
            'expected_response12.json',
            False,
        ),
        (
            [37.590533, 55.733863],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000016',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 8.80 (562)',
            '000000000000000000000016',
            200,
            'expected_response13.json',
            True,
        ),
        (
            [37.590533, 55.733863],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000017',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 8.80 (562)',
            '000000000000000000000017',
            200,
            'expected_response14.json',
            True,
        ),
        pytest.param(
            [37.590533, 55.733863],
            '2019-04-01T06:10:00+0500',
            '000000000000000000000002',
            '2019-03-31T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            'Asia/Yekaterinburg',
            'Taximeter 8.80 (562)',
            '000000000000000000000001',
            200,
            'expected_response15.json',
            False,
            marks=(pytest.mark.config(LOYALTY_CHECK_WALLET_BALANCE=False),),
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.driver_tags_match(
    dbid='driver_db_id1',
    uuid='driver_uuid1',
    tags=['bad_driver', '200_days_with_trips'],
)
@pytest.mark.pgsql(
    'loyalty',
    files=[
        'loyalty_accounts.sql',
        'loyalty_rewards.sql',
        'status_logs.sql',
        'manual_statuses.sql',
    ],
)
async def test_driver_loyalty_details(
        taxi_loyalty,
        driver_metrics_storage,
        mock_driver_ratings,
        mock_fleet_parks_list,
        unique_drivers,
        experiments3,
        load_json,
        position,
        time,
        wallet,
        ts_from,
        ts_to,
        timezone,
        user_agent,
        unique_driver_id,
        expected_code,
        expected_response,
        with_priority,
        mocked_time,
):
    experiments3.add_experiment(
        **test_utils.make_priority_experiment3(with_priority),
    )
    experiments3.add_experiments_json(
        load_json('loyalty_manual_status_settings.json'),
    )
    experiments3.add_experiments_json(load_json('loyalty_ui_statuses.json'))
    driver_metrics_storage.set_wallet_balance_value(
        wallet, ts_from, ts_to, 221,
    )
    mock_driver_ratings.set_rating(unique_driver_id, 3.9886)
    unique_drivers.set_unique_driver(
        'driver_db_id1', 'driver_uuid1', unique_driver_id,
    )
    mocked_time.set(utils.to_utc(dateutil.parser.parse(time)))
    await taxi_loyalty.invalidate_caches()

    response = await taxi_loyalty.post(
        CODEGEN_HANDLER_URL,
        json={'position': position, 'timezone': timezone},
        headers=test_utils.get_auth_headers(
            'driver_db_id1', 'driver_uuid1', user_agent,
        ),
    )

    assert response.status_code == expected_code
    assert response.json() == load_json('response/' + expected_response)


@pytest.mark.parametrize(
    'position, expected_response, exp_clause_zone, add_exp_clause',
    [
        (
            [37.1946401739712, 55.478983901730004],
            'expected_response11.json',
            '',
            False,
        ),
        (
            [37.1946401739712, 55.478983901730004],
            'expected_response11.json',
            'kazan',
            False,
        ),
        (
            [37.1946401739712, 55.478983901730004],
            'expected_response14.json',
            'moscow',
            True,
        ),
        (
            [37.1946401739712, 55.478983901730004],
            'expected_response14.json',
            'br_tsentralnyj_fo',
            True,
        ),
        (
            [37.1946401739712, 55.478983901730004],
            'expected_response14.json',
            'br_russia',
            True,
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.driver_tags_match(
    dbid='driver_db_id1',
    uuid='driver_uuid1',
    tags=['bad_driver', '200_days_with_trips'],
)
@pytest.mark.pgsql(
    'loyalty',
    files=[
        'loyalty_accounts.sql',
        'loyalty_rewards.sql',
        'status_logs.sql',
        'manual_statuses.sql',
    ],
)
async def test_driver_loyalty_details_priority_exp_zones(
        taxi_loyalty,
        driver_metrics_storage,
        mock_driver_ratings,
        mock_fleet_parks_list,
        unique_drivers,
        experiments3,
        load_json,
        position,
        expected_response,
        exp_clause_zone,
        add_exp_clause,
        mocked_time,
):
    time = '2019-04-01T06:10:00+0500'
    wallet = '000000000000000000000017'
    ts_from = '2019-03-31T21:00:00+0000'
    ts_to = '2019-04-01T01:10:00+0000'
    timezone = 'Asia/Yekaterinburg'
    user_agent = 'Taximeter 8.80 (562)'
    unique_driver_id = '000000000000000000000017'

    clauses = None
    if add_exp_clause:
        clauses = [
            test_utils.get_priority_exp_zones_clause(exp_clause_zone, 90),
        ]

    experiments3.add_experiment(
        **test_utils.make_priority_exp3_wo_default(clauses),
    )
    experiments3.add_experiments_json(
        load_json('loyalty_manual_status_settings.json'),
    )
    experiments3.add_experiments_json(load_json('loyalty_ui_statuses.json'))
    driver_metrics_storage.set_wallet_balance_value(
        wallet, ts_from, ts_to, 221,
    )
    mock_driver_ratings.set_rating(unique_driver_id, 3.9886)
    unique_drivers.set_unique_driver(
        'driver_db_id1', 'driver_uuid1', unique_driver_id,
    )
    mocked_time.set(utils.to_utc(dateutil.parser.parse(time)))
    await taxi_loyalty.invalidate_caches()

    response = await taxi_loyalty.post(
        CODEGEN_HANDLER_URL,
        json={'position': position, 'timezone': timezone},
        headers=test_utils.get_auth_headers(
            'driver_db_id1', 'driver_uuid1', user_agent,
        ),
    )

    assert response.status_code == 200
    assert response.json() == load_json('response/' + expected_response)


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    """position,unique_driver_id,wallet_balance,
    user_agent,expected_response,with_priority""",
    [
        (
            [37.590533, 55.733863],
            '000000000000000000000014',
            3,
            'Taximeter 8.80 (562)',
            'new_driver_expected_response1.json',
            False,
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000014',
            6,
            'Taximeter 8.80 (562)',
            'new_driver_expected_response2.json',
            False,
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000014',
            None,
            'Taximeter 8.80 (562)',
            'new_driver_expected_response3.json',
            False,
        ),
        pytest.param(
            [37.590533, 55.733863],
            '000000000000000000000014',
            1,
            'Taximeter 8.80 (562)',
            'new_driver_expected_response3.json',
            False,
            marks=(pytest.mark.config(LOYALTY_CHECK_WALLET_BALANCE=False),),
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000014',
            3,
            'Taximeter 8.79 (562)',
            'new_driver_expected_response4.json',
            False,
        ),
        (
            [39.590533, 55.733863],
            '000000000000000000000014',
            3,
            'Taximeter 8.80 (562)',
            'new_driver_expected_response5.json',
            False,
        ),
        (
            [37.590533, 59.733863],
            '000000000000000000000014',
            3,
            'Taximeter 8.80 (562)',
            'new_driver_expected_response6.json',
            False,
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000014',
            3,
            'Taximeter 8.80 (562)',
            'new_driver_expected_response7.json',
            True,
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000014',
            6,
            'Taximeter 8.80 (562)',
            'new_driver_expected_response8.json',
            True,
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000014',
            None,
            'Taximeter 8.80 (562)',
            'new_driver_expected_response9.json',
            True,
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000014',
            3,
            'Taximeter 8.79 (562)',
            'new_driver_expected_response10.json',
            True,
        ),
    ],
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'loyalty': '8.75', 'loyalty_cards': '8.80'},
        },
    },
    TVM_ENABLED=True,
)
@pytest.mark.pgsql(
    'loyalty', files=['loyalty_accounts.sql', 'loyalty_rewards.sql'],
)
async def test_driver_loyalty_new_driver_details(
        taxi_loyalty,
        driver_metrics_storage,
        mock_fleet_parks_list,
        unique_drivers,
        experiments3,
        load_json,
        position,
        unique_driver_id,
        wallet_balance,
        user_agent,
        expected_response,
        with_priority,
        mocked_time,
):
    experiments3.add_experiment(
        **test_utils.make_priority_experiment3(with_priority),
    )
    if wallet_balance:
        driver_metrics_storage.set_wallet_balance_value(
            unique_driver_id,
            '2019-02-28T21:00:00+0000',
            '2019-04-01T01:10:00+0000',
            wallet_balance,
        )
    unique_drivers.set_unique_driver(
        'driver_db_id1', 'driver_uuid1', unique_driver_id,
    )
    mocked_time.set(
        utils.to_utc(dateutil.parser.parse('2019-04-01T06:10:00+0500')),
    )
    await taxi_loyalty.invalidate_caches()

    response = await taxi_loyalty.post(
        CODEGEN_HANDLER_URL,
        json={'position': position, 'timezone': 'Europe/Moscow'},
        headers=test_utils.get_auth_headers(
            'driver_db_id1', 'driver_uuid1', user_agent,
        ),
    )

    assert response.status_code == 200
    assert response.json() == load_json('response/' + expected_response)
