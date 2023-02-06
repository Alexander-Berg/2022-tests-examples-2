import pytest


PERIODIC_NAME = 'digest-sending-max-delay-periodic'


def insert_into_table(pgsql, values):
    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        f"""
        INSERT INTO eats_restapp_communications.place_digest_send_schedule
            (place_id, is_active, timezone, to_send_at, sent_at)
        VALUES ({values});
        """,
    )


@pytest.mark.pgsql(
    'eats_restapp_communications', files=['test_digest_send_schedule.sql'],
)
@pytest.mark.now('2022-06-20T10:20:00+0300')
@pytest.mark.parametrize(
    'values, expected_max_delay',
    [
        pytest.param(None, 5),
        pytest.param(
            '55, true, \'Europe/Moscow\', \'10:00\', '
            + '\'2022-06-20T10:02:00+0300\'',
            5,
        ),
        pytest.param(
            '66, true, \'Europe/Moscow\', \'10:00\', '
            + '\'2022-06-20T10:07:30+0300\'',
            7,
        ),
        pytest.param(
            '77, true, \'Asia/Yekaterinburg\', \'08:00\', '
            + '\'2022-06-20T08:09:00+0500\'',
            9,
        ),
        pytest.param(
            '88, true, \'Asia/Yekaterinburg\', NULL, '
            + '\'2022-06-20T10:10:00+0500\'',
            10,
        ),
        pytest.param('99, true, \'Asia/Yekaterinburg\', \'12:00\', NULL', 20),
        pytest.param('111, false, \'Asia/Yekaterinburg\', NULL, NULL', 5),
        pytest.param('222, true, \'Europe/Moscow\', NULL, NULL', 20),
    ],
)
async def test_digest_sending_max_delay_periodic(
        taxi_eats_restapp_communications,
        taxi_eats_restapp_communications_monitor,
        pgsql,
        values,
        expected_max_delay,
):
    if values is not None:
        insert_into_table(pgsql, values)

    await taxi_eats_restapp_communications.run_distlock_task(PERIODIC_NAME)
    metrics = await taxi_eats_restapp_communications_monitor.get_metric(
        'digest-sending',
    )
    assert metrics['max_delay_in_minutes'] == expected_max_delay
