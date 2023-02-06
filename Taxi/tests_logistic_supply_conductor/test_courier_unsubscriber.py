import pytest


TASK_NAME = 'logistic-supply-conductor-courier-unsubscriber'


def check_red_button_completed(pgsql):
    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT red_button_cancelling
    FROM logistic_supply_conductor.workshift_metadata
    """,
    )
    assert list(cursor) == [(False,), (False,)]


def check_red_button_not_completed(pgsql):
    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
    SELECT red_button_cancelling
    FROM logistic_supply_conductor.workshift_metadata
    """,
    )
    assert list(cursor) == [(False,), (True,)]


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
        'pg_workshift_slot_subscribers.sql',
    ],
)
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_COURIER_UNSUBSCRIBER_SETTINGS={
        'default_period': 1,
        'repetitive_period': 1,
        'enabled': True,
    },
)
@pytest.mark.parametrize(
    'init_sql, expected_cancel_request, expected_cancel_all_request, check',
    [
        pytest.param(None, [], [], None, id='empty'),
        pytest.param(
            """
        UPDATE logistic_supply_conductor.workshift_slot_subscribers
        SET free_time_end = '2020-01-01T00:00:00Z'
        """,
            [
                {
                    'cancel_reason': 'workshift_violations',
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                    'contractors': [
                        {
                            'contractor_id': {
                                'park_id': '458f82d8dbf24ecd81d1de2c7826d1b5',
                                'driver_profile_id': (
                                    'e2b66c10ece54751a8db96b3a2039b0f'
                                ),
                            },
                        },
                    ],
                },
            ],
            [],
            None,
            id='free time end',
        ),
        pytest.param(
            """
        UPDATE logistic_supply_conductor.workshift_slots
        SET
            time_start = '2020-01-01T00:00:00Z',
            time_stop = '2020-01-02T00:00:00Z'
        WHERE id=1
        """,
            [
                {
                    'cancel_reason': 'workshift_not_started',
                    'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
                    'contractors': [
                        {
                            'contractor_id': {
                                'park_id': '458f82d8dbf24ecd81d1de2c7826d1b5',
                                'driver_profile_id': (
                                    'e2b66c10ece54751a8db96b3a2039b0f'
                                ),
                            },
                        },
                    ],
                },
            ],
            [
                {
                    'cancel_reason': 'emergency',
                    'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
                },
            ],
            None,
            id='finished slot with reservation',
        ),
        pytest.param(
            """
        UPDATE logistic_supply_conductor.workshift_slots
        SET
            time_start = '2020-01-01T00:00:00Z',
            time_stop = '2020-01-02T00:00:00Z'
        WHERE id=2
        """,
            [],
            [],
            None,
            id='finished slot without reservation',
        ),
        pytest.param(
            """
        UPDATE logistic_supply_conductor.workshift_metadata
        SET red_button_cancelling=True
        WHERE id=1
        """,
            [],
            [
                {
                    'cancel_reason': 'emergency',
                    'slot_id': 'a4e20684-fd40-490c-b6ac-faf0ee074b89',
                },
            ],
            check_red_button_completed,
            id='red button not completed',
        ),
        pytest.param(
            """
        UPDATE logistic_supply_conductor.workshift_metadata
        SET red_button_cancelling=True
        WHERE id=2
        """,
            [],
            [
                {
                    'cancel_reason': 'emergency',
                    'slot_id': '57079d82-fabd-4e70-9961-09a4733bbc57',
                },
                {
                    'cancel_reason': 'emergency',
                    'slot_id': 'a278134c-49f2-48bc-b9b6-941c76650508',
                },
                {
                    'cancel_reason': 'emergency',
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                },
                {
                    'cancel_reason': 'emergency',
                    'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
                },
            ],
            check_red_button_not_completed,
            id='red button completed',
        ),
    ],
)
async def test_courier_unsubscriber(
        taxi_logistic_supply_conductor,
        mockserver,
        pgsql,
        init_sql,
        expected_cancel_request,
        expected_cancel_all_request,
        check,
):
    if init_sql is not None:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(init_sql)

    @mockserver.json_handler(
        '/driver-mode-subscription/v1/logistic-workshifts'
        '/slots/cancel-reservations',
    )
    def cancel_reservations(request):
        assert (
            request.json
            == expected_cancel_request[cancel_reservations.times_called]
        )
        return {}

    @mockserver.json_handler(
        '/driver-mode-subscription/v1/logistic-workshifts'
        '/slots/cancel-all-reservations',
    )
    def cancel_all_reservations(request):
        assert (
            request.json
            == expected_cancel_all_request[
                cancel_all_reservations.times_called
            ]
        )
        return {}

    await taxi_logistic_supply_conductor.invalidate_caches()

    await taxi_logistic_supply_conductor.run_task(TASK_NAME)

    assert cancel_reservations.times_called == len(expected_cancel_request)
    assert cancel_all_reservations.times_called == len(
        expected_cancel_all_request,
    )

    if check is not None:
        check(pgsql)
