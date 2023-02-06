import pytest

from signal_device_api_worker.generated.cron import run_cron

CRON_PARAMS = [
    'signal_device_api_worker.crontasks.add_events_to_park',
    '-t',
    '0',
]


def _get_amount(pgsql, park_id, device_id, event_types) -> int:
    db = pgsql['signal_device_api_meta_db'].cursor()
    query = f"""
              SELECT COUNT(*)
              FROM signal_device_api.events AS e
              WHERE
                    e.park_id = '{park_id}'
                    AND e.event_type IN {tuple(event_types)}
             """
    if device_id:
        query += f' AND e.device_id = \'{device_id}\''

    db.execute(query)
    return list(db)[0][0]


def _get_delay(pgsql, park_id, device_id) -> int:
    db = pgsql['signal_device_api_meta_db'].cursor()
    query = f"""
              SELECT e.created_at - e.event_at
              FROM signal_device_api.events AS e
              WHERE
                    e.park_id = '{park_id}'
             """
    if device_id:
        query += f' AND e.device_id = \'{device_id}\''

    db.execute(query)
    return list(db)[0]


@pytest.mark.parametrize(
    'park_id, device_id, event_types, expected_amount, expected_delay',
    [
        pytest.param(
            'p1',
            None,
            ['driver_lost', 'seatbelt', 'sleep'],
            1,
            60,
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_WORKER_ADD_EVENTS_TO_PARK_SETTINGS_V2={
                    'park_id': 'p1',
                    'event_types': ['driver_lost', 'seatbelt', 'sleep'],
                    'amount': 1,
                    'video_file_id': 'video',
                    'photo_file_id': 'photo',
                    'created_at_delay': 60,
                },
            ),
        ),
        pytest.param(
            'p4',
            None,
            ['driver_lost', 'seatbelt', 'sleep'],
            0,
            None,
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_WORKER_ADD_EVENTS_TO_PARK_SETTINGS_V2={
                    'park_id': 'p4',
                    'event_types': ['driver_lost', 'seatbelt', 'sleep'],
                    'amount': 1,
                    'video_file_id': 'video',
                    'photo_file_id': 'photo',
                    'created_at_delay': 60,
                },
            ),
        ),
        pytest.param(
            'p8',
            8,
            ['driver_lost', 'seatbelt', 'sleep'],
            1,
            60,
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_WORKER_ADD_EVENTS_TO_PARK_SETTINGS_V2={
                    'park_id': 'p8',
                    'event_types': ['driver_lost', 'seatbelt', 'sleep'],
                    'amount': 1,
                    'video_file_id': 'video',
                    'photo_file_id': 'photo',
                    'created_at_delay': 60,
                    'serial_number': 'FFFDEAD4',
                },
            ),
        ),
        pytest.param(
            'p8',
            9,
            ['driver_lost', 'seatbelt', 'sleep'],
            0,
            None,
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_WORKER_ADD_EVENTS_TO_PARK_SETTINGS_V2={
                    'park_id': 'p8',
                    'event_types': ['driver_lost', 'seatbelt', 'sleep'],
                    'amount': 1,
                    'video_file_id': 'video',
                    'photo_file_id': 'photo',
                    'created_at_delay': 60,
                    'serial_number': '1337587103',
                },
            ),
        ),
        pytest.param(
            'p8',
            None,
            ['driver_lost', 'seatbelt', 'sleep'],
            2,
            60,
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_WORKER_ADD_EVENTS_TO_PARK_SETTINGS_V2={
                    'park_id': 'p8',
                    'event_types': ['driver_lost', 'seatbelt', 'sleep'],
                    'amount': 2,
                    'video_file_id': 'video',
                    'photo_file_id': 'photo',
                    'created_at_delay': 60,
                },
            ),
        ),
        pytest.param(
            'p8',
            None,
            ['driver_lost', 'seatbelt', 'sleep'],
            1,
            2,
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_WORKER_ADD_EVENTS_TO_PARK_SETTINGS_V2={
                    'park_id': 'p8',
                    'event_types': ['driver_lost', 'seatbelt', 'sleep'],
                    'amount': 1,
                    'video_file_id': 'video',
                    'photo_file_id': 'photo',
                    'created_at_delay': 2,
                },
            ),
        ),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
async def test_all(
        pgsql,
        park_id,
        device_id,
        event_types,
        expected_amount,
        expected_delay,
):
    assert _get_amount(pgsql, park_id, device_id, event_types) == 0
    await run_cron.main(CRON_PARAMS)
    assert (
        _get_amount(pgsql, park_id, device_id, event_types) == expected_amount
    )
    if expected_delay:
        for delay in _get_delay(pgsql, park_id, device_id):
            assert delay.total_seconds() // 60 == expected_delay
