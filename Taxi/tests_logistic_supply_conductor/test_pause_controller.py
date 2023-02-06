import datetime

import dateutil.parser
import pytest

TASK_NAME = 'logistic-supply-conductor-pause-controller'


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
        'pg_workshift_slot_subscribers_with_free_time.sql',
    ],
)
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_PAUSE_CONTROLLER_SETTINGS={
        'check_period': 1,
        'enabled': True,
        'notify_threshold': 10,
    },
    LOGISTIC_SUPPLY_CONDUCTOR_STATE_TRANSITION_SETTINGS={
        'slot_subscription_start_threshold': 59,
    },
)
@pytest.mark.now('2033-04-09T00:00:00Z')
async def test_pause_controller(
        taxi_logistic_supply_conductor, client_events, mockserver, pgsql,
):
    @mockserver.json_handler('/candidates/profiles')
    def profiles(request):
        assert request.json == {
            'driver_ids': [
                {
                    'dbid': '929f5bc2f0f44c8595faaa818f4d3ab8',
                    'uuid': '31d323d5532440de8a82ee2e2e2e7b5f',
                },
                {
                    'dbid': 'c3ad7a1fdc1a48ef9cb121f457e5a5e0',
                    'uuid': '4a90810b6b2b446bbafa7f2f14fa2010',
                },
                {
                    'dbid': '12abe2811d6249fda94a962afa8fd129',
                    'uuid': '30cd94f445454aeba36f382085f9bb03',
                },
                {
                    'dbid': '5a385e661c8a46e5a575dd9474e49db7',
                    'uuid': 'e79301f26fe842e398bb752aa6381816',
                },
                {
                    'dbid': '20f72c73435f4c0ebd559188a2e7f893',
                    'uuid': 'e6f286baf6594ce9855b08c088a365d2',
                },
                {
                    'dbid': '9b6ef7a02fe24119a7b2a191caf5ed82',
                    'uuid': 'b7023161d1ef4e16ad855b6d7a6173bd',
                },
                {
                    'dbid': '845f055e7f46459b99917e91418e8896',
                    'uuid': 'b84f6d32423747f4a691270c2b61ce4d',
                },
                {
                    'dbid': '74174e1784e340e7a56b949a290b9aea',
                    'uuid': 'fb18bcb2f7ce426fa11b3dd86d20f1c1',
                },
                {
                    'dbid': '064ffd76903746cba731cae5d33172f4',
                    'uuid': '02113168e5e94418bf8b3c9724678c84',
                },
            ],
            'data_keys': ['status'],
        }

        return {
            'drivers': [
                {
                    'uuid': '31d323d5532440de8a82ee2e2e2e7b5f',
                    'dbid': '929f5bc2f0f44c8595faaa818f4d3ab8',
                    'position': [53, 63],
                    'status': {'status': 'busy', 'orders': []},
                },
                {
                    'uuid': '4a90810b6b2b446bbafa7f2f14fa2010',
                    'dbid': 'c3ad7a1fdc1a48ef9cb121f457e5a5e0',
                    'position': [53, 63],
                    'status': {'status': 'online', 'orders': []},
                },
                {
                    'dbid': '12abe2811d6249fda94a962afa8fd129',
                    'uuid': '30cd94f445454aeba36f382085f9bb03',
                    'position': [55, 63],
                    'status': {'status': 'online', 'orders': []},
                },
                {
                    'dbid': '5a385e661c8a46e5a575dd9474e49db7',
                    'uuid': 'e79301f26fe842e398bb752aa6381816',
                    'position': [55, 63],
                    'status': {'status': 'busy', 'orders': ['some_order']},
                },
                {
                    'dbid': '845f055e7f46459b99917e91418e8896',
                    'uuid': 'b84f6d32423747f4a691270c2b61ce4d',
                    'position': [53, 63],
                    'status': {'status': 'busy', 'orders': []},
                },
                {
                    'dbid': '74174e1784e340e7a56b949a290b9aea',
                    'uuid': 'fb18bcb2f7ce426fa11b3dd86d20f1c1',
                    'position': [53, 63],
                    'status': {'status': 'online', 'orders': []},
                },
                {
                    'dbid': '064ffd76903746cba731cae5d33172f4',
                    'uuid': '02113168e5e94418bf8b3c9724678c84',
                    'position': [53, 63],
                    'status': {'status': 'busy', 'orders': []},
                },
            ],
        }

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def locales(request):
        assert request.json == {
            'id_in_set': [
                '929f5bc2f0f44c8595faaa818f4d3ab8_'
                '31d323d5532440de8a82ee2e2e2e7b5f',
                'c3ad7a1fdc1a48ef9cb121f457e5a5e0_'
                '4a90810b6b2b446bbafa7f2f14fa2010',
                '12abe2811d6249fda94a962afa8fd129_'
                '30cd94f445454aeba36f382085f9bb03',
                '5a385e661c8a46e5a575dd9474e49db7_'
                'e79301f26fe842e398bb752aa6381816',
                '20f72c73435f4c0ebd559188a2e7f893_'
                'e6f286baf6594ce9855b08c088a365d2',
                '9b6ef7a02fe24119a7b2a191caf5ed82_'
                'b7023161d1ef4e16ad855b6d7a6173bd',
                '845f055e7f46459b99917e91418e8896_'
                'b84f6d32423747f4a691270c2b61ce4d',
                '74174e1784e340e7a56b949a290b9aea_'
                'fb18bcb2f7ce426fa11b3dd86d20f1c1',
                '064ffd76903746cba731cae5d33172f4_'
                '02113168e5e94418bf8b3c9724678c84',
            ],
            'projection': ['data.locale'],
        }

        return {
            'profiles': [
                {
                    'park_driver_profile_id': (
                        '929f5bc2f0f44c8595faaa818f4d3ab8_'
                        '31d323d5532440de8a82ee2e2e2e7b5f'
                    ),
                    'data': {'locale': 'ru'},
                },
                {
                    'park_driver_profile_id': (
                        'c3ad7a1fdc1a48ef9cb121f457e5a5e0_'
                        '4a90810b6b2b446bbafa7f2f14fa2010'
                    ),
                    'data': {'locale': 'en'},
                },
                {
                    'park_driver_profile_id': (
                        '12abe2811d6249fda94a962afa8fd129_'
                        '30cd94f445454aeba36f382085f9bb03'
                    ),
                },
            ],
        }

    await taxi_logistic_supply_conductor.run_task(TASK_NAME)

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT
        id,
        free_time_left,
        free_time_end,
        out_of_polygon_time_left,
        out_of_polygon_time_end
    FROM logistic_supply_conductor.workshift_slot_subscribers
    ORDER BY id ASC
    """,
    )
    assert list(cursor) == [
        (
            1,
            None,
            dateutil.parser.isoparse('2033-04-09T03:00:00Z'),
            None,
            None,
        ),
        (2, datetime.timedelta(hours=5), None, None, None),
        (
            3,
            datetime.timedelta(hours=2),
            None,
            None,
            dateutil.parser.isoparse('2033-04-09T00:05:00Z'),
        ),
        (4, datetime.timedelta(hours=6), None, None, None),
        (
            5,
            None,
            dateutil.parser.isoparse('2033-04-09T01:00:00Z'),
            None,
            None,
        ),
        (6, datetime.timedelta(hours=8), None, None, None),
        (
            7,
            None,
            dateutil.parser.isoparse('2033-04-09T00:00:01Z'),
            None,
            None,
        ),
        (8, datetime.timedelta(hours=9), None, None, None),
        (
            9,
            None,
            dateutil.parser.isoparse('2033-04-09T10:00:00Z'),
            datetime.timedelta(minutes=5),
            None,
        ),
    ]

    assert profiles.times_called == 1
    assert locales.times_called == 1
    assert client_events.times_called == 2
