import imp
import dateutil
import pytest
import json

driver_profiles_response_json = {
    'courier_by_eats_id': [
        {
            'eats_courier_id': '540',
            'profiles': [{'park_driver_profile_id': 'parkid_driverid540'}],
        },
        {
            'eats_courier_id': '450',
            'profiles': [{'park_driver_profile_id': 'parkid_driverid450'}],
        },
        {
            'eats_courier_id': '676',
            'profiles': [{'park_driver_profile_id': 'parkid_driverid676'}],
        },
        {
            'eats_courier_id': '694',
            'profiles': [{'park_driver_profile_id': 'parkid_driverid694'}],
        },
        {
            'eats_courier_id': '700',
            'profiles': [{'park_driver_profile_id': 'parkid_driverid700'}],
        },
        {
            'eats_courier_id': '800',
            'profiles': [{'park_driver_profile_id': 'parkid_driverid800'}],
        },
    ],
}

unique_drivers_response_json = {
    'uniques': [
        {
            'park_driver_profile_id': 'parkid_driverid540',
            'data': {'unique_driver_id': 'unique_driver_id_540'},
        },
        {
            'park_driver_profile_id': 'parkid_driverid450',
            'data': {'unique_driver_id': 'unique_driver_id_450'},
        },
        {
            'park_driver_profile_id': 'parkid_driverid676',
            'data': {'unique_driver_id': 'unique_driver_id_676'},
        },
        {
            'park_driver_profile_id': 'parkid_driverid694',
            'data': {'unique_driver_id': 'unique_driver_id_694'},
        },
        {
            'park_driver_profile_id': 'parkid_driverid700',
            'data': {'unique_driver_id': 'unique_driver_id_700'},
        },
        {
            'park_driver_profile_id': 'parkid_driverid800',
            'data': {'unique_driver_id': 'unique_driver_id_800'},
        },
    ],
}


@pytest.fixture(name='mock_yql')
def _mock_yql(mockserver, load):
    class Context:
        _results_call_number = 0

        @property
        def results_call_number(self):
            return self._results_call_number

        def inc_results_call_number(self):
            self._results_call_number += 1

    context = Context()

    @mockserver.json_handler('/yql/api/v2/operations')
    def _new_operation(request):
        return {'id': 'abcde12345'}

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)', regex=True,
    )
    def _operation_status(request, operation_id):
        return {'id': operation_id, 'status': 'COMPLETED'}

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/results', regex=True,
    )
    def _operation_status_results(request, operation_id):
        return {'id': operation_id, 'status': 'COMPLETED'}

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/share_id', regex=True,
    )
    def _operation_url(request, operation_id):
        return 'this_is_share_url'

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/results_data',
        regex=True,
    )
    def _operation_results_data(request, operation_id):
        context.inc_results_call_number()
        return mockserver.make_response(
            load('yql_response_{}.txt'.format(context.results_call_number)),
            content_type='application/json',
            status=200,
        )

    return context


async def get_goals(cursor):
    cursor.execute(
        """
SELECT
    *
FROM eats_performer_subventions.performer_subvention_order_goals psog
WHERE source='yt_dxgy'
        """,
    )

    return cursor.fetchall()


async def get_notifications(cursor, goal_id):
    cursor.execute(
        """
SELECT
    *
FROM eats_performer_subventions.performer_subvention_notifications psn
WHERE psn.goal_id = '{}' AND psn.goal_type='dxgy'
ORDER BY psn.runs_at ASC
        """.format(
            goal_id,
        ),
    )

    return cursor.fetchall()


@pytest.mark.geo_nodes(filename='geonodes.json')
@pytest.mark.config(
    EATS_PERFORMER_SUBVENTIONS_SUBVENTION_GOALS_IMPORTER_SETTINGS={
        'period_sec': 600,
        'is_enabled': True,
        'db_read_chunk_size': 2,
        'cancel_outdated': True,
        'daily_goal_groups': ['daily'],
        'retention_goal_groups': ['retention'],
    },
    EATS_PERFORMER_SUBVENTIONS_YQL_QUERY_READER_SETTINGS={
        'status_retry_interval_ms': 1,
        'status_total_wait_ms': 1000,
        'read_chunk_size': 500,
    },
)
@pytest.mark.yt(static_table_data=['yt_goals_data.yaml'])
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'total_count,imported_goals',
    [
        pytest.param(
            6,
            [
                {
                    'goal_type': 'dxgy',
                    'performer_id': '450',
                    'money_to_pay': 750,
                    'performer_group': 'test',
                    'target_orders_count': 15,
                    'starts_at': '2020-12-28T00:00:00+03:00',
                    'finishes_at': '2020-12-30T23:59:59+03:00',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [],
                },
                {
                    'goal_type': 'dxgy',
                    'performer_id': '540',
                    'money_to_pay': 750,
                    'performer_group': 'test',
                    'target_orders_count': 15,
                    'starts_at': '2022-12-28T00:00:00+03:00',
                    'finishes_at': '2022-12-30T23:59:59+03:00',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                        {'type': 'check_state', 'runs_at_date': '2022-12-29'},
                    ],
                },
                {
                    'goal_type': 'dxgy',
                    'performer_id': '676',
                    'money_to_pay': 750,
                    'performer_group': 'test',
                    'target_orders_count': 15,
                    'starts_at': '2022-12-28T00:00:00+03:00',
                    'finishes_at': '2022-12-30T23:59:59+03:00',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                        {'type': 'check_state', 'runs_at_date': '2022-12-29'},
                    ],
                },
                {
                    'goal_type': 'dxgy',
                    'performer_id': '694',
                    'money_to_pay': 1050,
                    'performer_group': 'test',
                    'target_orders_count': 21,
                    'starts_at': '2022-12-28T00:00:00+0300',
                    'finishes_at': '2022-12-30T23:59:59+0300',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                        {'type': 'check_state', 'runs_at_date': '2022-12-29'},
                    ],
                },
                {
                    'goal_type': 'daily_goal',
                    'performer_id': '700',
                    'money_to_pay': 50000,
                    'performer_group': 'daily',
                    'target_orders_count': 21,
                    'starts_at': '2023-01-01T00:00:00+0600',
                    'finishes_at': '2023-01-07T23:59:59+0600',
                    'currency': 'kzt',
                    'timezone': 'Asia/Almaty',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                    ],
                },
                {
                    'goal_type': 'retention',
                    'performer_id': '800',
                    'money_to_pay': 1001,
                    'performer_group': 'retention',
                    'target_orders_count': 11,
                    'starts_at': '2022-12-28T00:00:00+0300',
                    'finishes_at': '2022-12-30T23:59:59+0300',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                    ],
                },
            ],
            marks=[pytest.mark.now('2022-12-20T15:34:00+03:00')],
            id='import without previous data',
        ),
        pytest.param(
            11,
            [
                {
                    'goal_type': 'dxgy',
                    'performer_id': '450',
                    'money_to_pay': 750,
                    'performer_group': 'test',
                    'target_orders_count': 15,
                    'starts_at': '2020-12-28T00:00:00+03:00',
                    'finishes_at': '2020-12-30T23:59:59+03:00',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [],
                },
                {
                    'goal_type': 'dxgy',
                    'performer_id': '540',
                    'money_to_pay': 750,
                    'performer_group': 'test',
                    'target_orders_count': 15,
                    'starts_at': '2022-12-28T00:00:00+03:00',
                    'finishes_at': '2022-12-30T23:59:59+03:00',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                        {'type': 'check_state', 'runs_at_date': '2022-12-29'},
                    ],
                },
                {
                    'goal_type': 'dxgy',
                    'performer_id': '676',
                    'money_to_pay': 750,
                    'performer_group': 'test',
                    'target_orders_count': 15,
                    'starts_at': '2022-12-28T00:00:00+03:00',
                    'finishes_at': '2022-12-30T23:59:59+03:00',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                        {'type': 'check_state', 'runs_at_date': '2022-12-29'},
                    ],
                },
                {
                    'goal_type': 'dxgy',
                    'performer_id': '694',
                    'money_to_pay': 1050,
                    'performer_group': 'test',
                    'target_orders_count': 21,
                    'starts_at': '2022-12-28T00:00:00+0300',
                    'finishes_at': '2022-12-30T23:59:59+0300',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                        {'type': 'check_state', 'runs_at_date': '2022-12-29'},
                    ],
                },
                {
                    'goal_type': 'daily_goal',
                    'performer_id': '700',
                    'money_to_pay': 50000,
                    'performer_group': 'daily',
                    'target_orders_count': 21,
                    'starts_at': '2023-01-01T00:00:00+0600',
                    'finishes_at': '2023-01-07T23:59:59+0600',
                    'currency': 'kzt',
                    'timezone': 'Asia/Almaty',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                    ],
                },
                {
                    'goal_type': 'retention',
                    'performer_id': '800',
                    'money_to_pay': 1001,
                    'performer_group': 'retention',
                    'target_orders_count': 11,
                    'starts_at': '2022-12-28T00:00:00+0300',
                    'finishes_at': '2022-12-30T23:59:59+0300',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                    ],
                },
            ],
            marks=[
                pytest.mark.now('2022-12-20T15:34:00+03:00'),
                pytest.mark.pgsql(
                    'eats_performer_subventions',
                    files=['subvention_goals_with_previous_data.sql'],
                ),
            ],
            id='import with not related previous data',
        ),
        pytest.param(
            8,
            [
                {
                    'goal_type': 'dxgy',
                    'performer_id': '450',
                    'money_to_pay': 6793,
                    'performer_group': 'not_send',
                    'target_orders_count': 97,
                    'starts_at': '2020-12-28T00:00:00+03:00',
                    'finishes_at': '2020-12-30T23:59:59+03:00',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [],
                },
                {
                    'goal_type': 'dxgy',
                    'performer_id': '540',
                    'money_to_pay': 6795,
                    'performer_group': 'send',
                    'target_orders_count': 97,
                    'starts_at': '2022-12-28T00:00:00+03:00',
                    'finishes_at': '2022-12-30T23:59:59+03:00',
                    'timezone': 'Europe/Moscow',
                    'currency': 'rub',
                    'notifications': [],
                },
                {
                    'goal_type': 'dxgy',
                    'performer_id': '676',
                    'money_to_pay': 750,
                    'performer_group': 'test',
                    'target_orders_count': 15,
                    'starts_at': '2022-12-28T00:00:00+03:00',
                    'finishes_at': '2022-12-30T23:59:59+03:00',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                        {'type': 'check_state', 'runs_at_date': '2022-12-29'},
                    ],
                },
                {
                    'goal_type': 'dxgy',
                    'performer_id': '694',
                    'money_to_pay': 1050,
                    'performer_group': 'test',
                    'target_orders_count': 21,
                    'starts_at': '2022-12-28T00:00:00+0300',
                    'finishes_at': '2022-12-30T23:59:59+0300',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                        {'type': 'check_state', 'runs_at_date': '2022-12-29'},
                    ],
                },
                {
                    'goal_type': 'daily_goal',
                    'performer_id': '700',
                    'money_to_pay': 50000,
                    'performer_group': 'daily',
                    'target_orders_count': 21,
                    'starts_at': '2023-01-01T00:00:00+0600',
                    'finishes_at': '2023-01-07T23:59:59+0600',
                    'currency': 'kzt',
                    'timezone': 'Asia/Almaty',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                    ],
                },
                {
                    'goal_type': 'retention',
                    'performer_id': '800',
                    'money_to_pay': 1001,
                    'performer_group': 'retention',
                    'target_orders_count': 11,
                    'starts_at': '2022-12-28T00:00:00+0300',
                    'finishes_at': '2022-12-30T23:59:59+0300',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                    ],
                },
            ],
            marks=[
                pytest.mark.now('2022-12-20T15:34:00+03:00'),
                pytest.mark.pgsql(
                    'eats_performer_subventions',
                    files=['subvention_goals_with_previous_related_data.sql'],
                ),
            ],
            id='import with related previous data',
        ),
        pytest.param(
            8,
            [
                {
                    'goal_type': 'dxgy',
                    'performer_id': '694',
                    'money_to_pay': 1050,
                    'performer_group': 'test',
                    'target_orders_count': 21,
                    'starts_at': '2022-12-28T00:00:00+0300',
                    'finishes_at': '2022-12-30T23:59:59+0300',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                        {'type': 'check_state', 'runs_at_date': '2022-12-29'},
                    ],
                    'region_id': 213,
                },
                {
                    'goal_type': 'daily_goal',
                    'performer_id': '700',
                    'money_to_pay': 50000,
                    'performer_group': 'daily',
                    'target_orders_count': 21,
                    'starts_at': '2023-01-01T00:00:00+0600',
                    'finishes_at': '2023-01-07T23:59:59+0600',
                    'currency': 'kzt',
                    'timezone': 'Asia/Almaty',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-22'},
                    ],
                    'region_id': 213,
                },
                {
                    'goal_type': 'retention',
                    'performer_id': '800',
                    'money_to_pay': 1001,
                    'performer_group': 'retention',
                    'target_orders_count': 11,
                    'starts_at': '2022-12-28T00:00:00+0300',
                    'finishes_at': '2022-12-30T23:59:59+0300',
                    'currency': 'rub',
                    'timezone': 'Europe/Moscow',
                    'notifications': [
                        {'type': 'welcome', 'runs_at_date': '2022-12-21'},
                    ],
                    'region_id': 213,
                },
            ],
            marks=[
                pytest.mark.now('2022-12-20T19:34:00+03:00'),
                pytest.mark.pgsql(
                    'eats_performer_subventions',
                    files=['subvention_goals_with_previous_related_data.sql'],
                ),
            ],
            id='import with related previous data, welcome'
            ' notification is delayed for KZ',
        ),
    ],
)
async def test_subvention_goals_importer(
        taxi_eats_performer_subventions,
        pgsql,
        mock_yql,
        total_count,
        imported_goals,
        mockserver,
        load_json,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/courier/profiles/retrieve_by_eats_id',
    )
    def _driver_profiles_retrieve_by_eats_id(request):
        return mockserver.make_response(
            json=driver_profiles_response_json, status=200,
        )

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _mock_eats_unique_drivers(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json=unique_drivers_response_json, status=200,
        )

    @mockserver.json_handler('/eats-core/v1/export/regions')
    def _mock_core(request):
        return load_json('eats_regions_response.json')

    cursor = pgsql['eats_performer_subventions'].dict_cursor()

    await taxi_eats_performer_subventions.run_periodic_task(
        'subvention-goals-importer-periodic',
    )

    db_goals = await get_goals(cursor)

    assert len(db_goals) == total_count

    def create_goal_key(goal):
        return '{}_{}_{}'.format(
            goal['performer_id'],
            dateutil.parser.isoparse(goal['starts_at'])
            .astimezone(tz=None)
            .strftime('%Y-%m-%d'),
            dateutil.parser.isoparse(goal['finishes_at'])
            .astimezone(tz=None)
            .strftime('%Y-%m-%d'),
        )

    imported_goals = {create_goal_key(goal): goal for goal in imported_goals}

    for goal in db_goals:
        goal_key = '{}_{}_{}'.format(
            goal['performer_id'],
            goal['starts_at'].astimezone(tz=None).strftime('%Y-%m-%d'),
            goal['finishes_at'].astimezone(tz=None).strftime('%Y-%m-%d'),
        )

        if goal_key in imported_goals:
            imported_goal = imported_goals[goal_key]
            assert goal['goal_type'] == imported_goal['goal_type']
            assert goal['performer_id'] == imported_goal['performer_id']
            assert goal['money_to_pay'] == imported_goal['money_to_pay']
            assert goal['performer_group'] == imported_goal['performer_group']
            assert (
                goal['target_orders_count']
                == imported_goal['target_orders_count']
            )
            assert (
                goal['starts_at'].astimezone(tz=None)
                == dateutil.parser.isoparse(
                    imported_goal['starts_at'],
                ).astimezone(tz=None)
            )
            assert (
                goal['finishes_at'].astimezone(tz=None)
                == dateutil.parser.isoparse(
                    imported_goal['finishes_at'],
                ).astimezone(tz=None)
            )
            assert goal['currency'] == imported_goal['currency']
            assert goal['timezone'] == imported_goal['timezone']
            if goal['performer_group'] not in ['send', 'not_send']:
                assert (
                    goal['unique_driver_id']
                    == 'unique_driver_id_' + goal['performer_id']
                )
                assert goal['geonode'] == 'br_root/br_moscow_adm'

            db_notifications = await get_notifications(cursor, goal['id'])

            assert len(db_notifications) == len(imported_goal['notifications'])

            for idx, db_notification in enumerate(db_notifications):
                imported_notification = imported_goal['notifications'][idx]
                assert db_notification['type'] == imported_notification['type']
                assert (
                    db_notification['runs_at'].strftime('%Y-%m-%d')
                    == imported_notification['runs_at_date']
                )

            del imported_goals[goal_key]

    assert not imported_goals
