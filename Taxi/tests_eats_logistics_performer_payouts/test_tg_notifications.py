import pytest


TASK_NAME = 'tg-notifications'


@pytest.mark.parametrize(
    'has_time_come,has_time_come_times_called,'
    'shifts_to_notify,shifts_to_notify_times_called,reports_times_called',
    [
        pytest.param(
            False,
            1,
            0,
            0,
            0,
            marks=[
                pytest.mark.now('2022-05-25T21:29:00+03:00'),
                pytest.mark.config(
                    EATS_LOGISTICS_PERFORMER_PAYOUTS_TG_NOTIFICATIONS_SETTING={
                        'is_enabled': True,
                        'period_ms': 60000,
                        'times': ['21:30'],
                        'batch_size': 30,
                        'batch_delay': 1000,
                    },
                ),
            ],
            id='Time has not come yet',
        ),
        pytest.param(
            True,
            1,
            0,
            1,
            1,
            marks=[
                pytest.mark.now('2022-05-25T21:31:00+03:00'),
                pytest.mark.config(
                    EATS_LOGISTICS_PERFORMER_PAYOUTS_TG_NOTIFICATIONS_SETTING={
                        'is_enabled': True,
                        'period_ms': 60000,
                        'times': ['21:30'],
                        'batch_size': 30,
                        'batch_delay': 1000,
                    },
                ),
            ],
            id='Time has come, no shifts',
        ),
        pytest.param(
            True,
            1,
            0,
            1,
            1,
            marks=[
                pytest.mark.now('2022-05-25T21:31:00+03:00'),
                pytest.mark.config(
                    EATS_LOGISTICS_PERFORMER_PAYOUTS_TG_NOTIFICATIONS_SETTING={
                        'is_enabled': True,
                        'period_ms': 60000,
                        'times': ['21:30'],
                        'batch_size': 30,
                        'batch_delay': 1000,
                    },
                ),
                pytest.mark.pgsql(
                    'eats_logistics_performer_payouts',
                    files=['init_no_shifts_bordered_test.sql'],
                ),
            ],
            id='Time has come, no shifts (bordered)',
        ),
        pytest.param(
            True,
            1,
            1,
            1,
            1,
            marks=[
                pytest.mark.now('2022-05-25T21:31:00+03:00'),
                pytest.mark.config(
                    EATS_LOGISTICS_PERFORMER_PAYOUTS_TG_NOTIFICATIONS_SETTING={
                        'is_enabled': True,
                        'period_ms': 60000,
                        'times': ['21:30'],
                        'batch_size': 30,
                        'batch_delay': 1000,
                    },
                ),
                pytest.mark.pgsql(
                    'eats_logistics_performer_payouts',
                    files=[
                        'init_no_shifts_bordered_test.sql',
                        'init_shifts_exists_test.sql',
                    ],
                ),
            ],
            id='Time has come, shifts exists (bordered)',
        ),
        pytest.param(
            True,
            1,
            3,
            1,
            1,
            marks=[
                pytest.mark.now('2022-05-25T21:31:00+03:00'),
                pytest.mark.config(
                    EATS_LOGISTICS_PERFORMER_PAYOUTS_TG_NOTIFICATIONS_SETTING={
                        'is_enabled': True,
                        'period_ms': 60000,
                        'times': ['21:30'],
                        'batch_size': 30,
                        'batch_delay': 1000,
                        'notify_since': '2022-05-23T00:00:00+03:00',
                    },
                ),
                pytest.mark.pgsql(
                    'eats_logistics_performer_payouts',
                    files=[
                        'init_shifts_exists_test.sql',
                        'init_shifts_exists_multidays_test.sql',
                    ],
                ),
            ],
            id='Time has come, shifts exists, multidays (bordered)',
        ),
    ],
)
async def test_tg_notifications(
        taxi_eats_logistics_performer_payouts,
        testpoint,
        load,
        has_time_come,
        has_time_come_times_called,
        shifts_to_notify,
        shifts_to_notify_times_called,
        reports_times_called,
):
    @testpoint(f'{TASK_NAME}_has_time_come')
    def time_has_come_tp(arg):
        assert arg == has_time_come

    @testpoint(f'{TASK_NAME}_shifts_to_notify')
    def shifts_to_notify_tp(arg):
        assert arg == shifts_to_notify

    @testpoint(f'{TASK_NAME}_report')
    def reports_tp(arg):
        if arg is None:
            return

        for courier in arg.keys():
            for date in arg[courier]:
                assert arg[courier][date] == load(
                    f'{courier}_{date}_report.txt',
                )

    await taxi_eats_logistics_performer_payouts.run_periodic_task(
        f'{TASK_NAME}-periodic',
    )
    assert time_has_come_tp.times_called == has_time_come_times_called
    assert shifts_to_notify_tp.times_called == shifts_to_notify_times_called
    assert reports_tp.times_called == reports_times_called
