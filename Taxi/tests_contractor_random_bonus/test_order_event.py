import math

import pytest

NOW = '2020-11-01T00:00:00+03:00'
SHORT_AGO = '2020-10-31T23:30:00+03:00'
PARK_ID = 'someParkId'
DRIVER_ID = 'someDriverId'


@pytest.mark.pgsql(
    'random-bonus-db',
    queries=[
        f"""
        INSERT INTO random_bonus.progress
          (park_id, driver_id, progress, is_first,
           last_status,
           status_updated_at, last_online_at,
           last_bonus_at)
        VALUES
          ('{PARK_ID}', '{DRIVER_ID}', 15, FALSE,
           'online'::random_bonus.STATUS,
           '{SHORT_AGO}'::TIMESTAMPTZ, '{SHORT_AGO}'::TIMESTAMPTZ,
           '{SHORT_AGO}'::TIMESTAMPTZ);""",
    ],
)
@pytest.mark.now(NOW)
@pytest.mark.config(
    RANDOM_BONUS_EVENTS_SETTINGS={
        'fines': {
            '__default__': 0,
            'cancel': 20,
            'reject': 10,
            'offer_timeout': 5,
        },
        'stq': {'retries': 3},
    },
)
@pytest.mark.parametrize(
    'event_type, expected',
    [('cancel', 0), ('reject', 5), ('offer_timeout', 10), ('unknown', 15)],
)
@pytest.mark.parametrize('is_sender_processing', [True, False])
async def test_order_event_ok(
        stq_runner, pgsql, is_sender_processing, event_type, expected,
):
    for _ in range(2):
        args, kwargs = (
            (
                [
                    {
                        'park_driver_profile_id': f'{PARK_ID}_{DRIVER_ID}',
                        'ordered_at': '2020-11-11T20:13:01+0300',
                        'order_id': 'someOrderId',
                        'event_type': event_type,
                    },
                ],
                {},
            )
            if not is_sender_processing
            else (
                [],
                {
                    'park_id': PARK_ID,
                    'clid_uuid': f'something_{DRIVER_ID}',
                    'order_id': 'someOrderId',
                    'event_type': event_type,
                },
            )
        )
        await stq_runner.random_bonus_order_event.call(
            task_id='some_task_id', args=args, kwargs=kwargs,
        )

        with pgsql['random-bonus-db'].cursor() as cursor:
            cursor.execute(
                f"""
                SELECT progress
                FROM random_bonus.progress
                WHERE park_id = '{PARK_ID}'
                  AND driver_id = '{DRIVER_ID}';
                """,
            )
            response = cursor.fetchone()
            assert math.isclose(response[0], expected)
