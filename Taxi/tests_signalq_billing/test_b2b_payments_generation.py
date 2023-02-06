import pytest


@pytest.mark.pgsql('signalq_billing', files=['opportunities.sql'])
@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=pytest.mark.now('2021-09-30T22:00:00+00:00')),
        pytest.param(
            marks=[
                pytest.mark.now('2021-10-05T00:00:00+03:00'),
                pytest.mark.config(
                    SIGNALQ_BILLING_B2B_PAYMENT_SETTINGS_V1={
                        'tins_payment_settings': {
                            '__default__': {
                                'amount_per_active_device': '40.0000',
                            },
                            'tin2': {'amount_per_active_device': '32.1326'},
                            'tin4': {'amount_per_active_device': '50.0000'},
                        },
                        'period1_min_device_statuses_count': 15,
                        'manual_next_run_at': '2021-10-05',
                    },
                ),
            ],
        ),
    ],
)
async def test_ok(testpoint, pgsql, taxi_signalq_billing):
    @testpoint('b2b-payments-generation-yt-ok')
    def yt_ok_testpoint(arg):
        pass

    async with taxi_signalq_billing.spawn_task(
            'workers/b2b-payments-generation',
    ):
        await yt_ok_testpoint.wait_call()

    db = pgsql['signalq_billing'].cursor()
    db.execute(
        """
        SELECT tin, active_devices_count, payment_amount, details
        FROM signalq_billing.b2b_payments_info
        WHERE payments_date = '2021-10-01'
    """,
    )
    assert sorted(list(db), key=lambda x: x[0]) == sorted(
        [
            (
                'tin1',
                5,
                '200.0000',
                'serial_number,total_amount\n'
                's11,40.0000\n'
                's12,40.0000\n'
                's13,0.0000\n'
                's14,40.0000\n'
                's15,40.0000\n'
                's0,40.0000\n',
            ),
            (
                'tin2',
                2,
                '64.2652',
                'serial_number,total_amount\ns21,32.1326\ns22,32.1326\n',
            ),
            (
                'tin3',
                4,
                '160.0000',
                'serial_number,total_amount\n'
                's31,40.0000\n'
                's32,40.0000\n'
                's33,0.0000\n'
                's34,40.0000\n'
                's35,40.0000\n'
                's0,0.0000\n',
            ),
            (
                'tin4',
                0,
                '0',
                'serial_number,total_amount\ns41,0.0000\ns42,0.0000\n',
            ),
        ],
        key=lambda x: x[0],
    )


@pytest.mark.now('2021-09-30T22:00:00+00:00')
async def test_no_clusters(
        testpoint, replication, taxi_signalq_billing, pgsql,
):
    replication.set_no_active_clusters()

    @testpoint('b2b-payments-generation-empty-yt-clusters')
    def empty_yt_clusters_testpoint(arg):
        pass

    async with taxi_signalq_billing.spawn_task(
            'workers/b2b-payments-generation',
    ):
        await empty_yt_clusters_testpoint.wait_call()


@pytest.mark.config(
    SIGNALQ_BILLING_B2B_PAYMENTS_GENERATION_TASK_SETTINGS={
        'task_delay_secs': 0,
        'enabled': False,
    },
)
async def test_disabled(testpoint, taxi_signalq_billing):
    @testpoint('b2b-payments-generation-disabled')
    def disabled_task_testpoint(arg):
        pass

    async with taxi_signalq_billing.spawn_task(
            'workers/b2b-payments-generation',
    ):
        await disabled_task_testpoint.wait_call()


@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=pytest.mark.now('2021-02-01T22:00:00+00:00')),
        pytest.param(marks=pytest.mark.now('2021-02-02T00:00:00+00:00')),
    ],
)
async def test_not_day_of_the_run(testpoint, taxi_signalq_billing):
    @testpoint('b2b-payments-generation-not-day-of-the-run')
    def not_day_of_the_run_testpoint(arg):
        pass

    async with taxi_signalq_billing.spawn_task(
            'workers/b2b-payments-generation',
    ):
        await not_day_of_the_run_testpoint.wait_call()


@pytest.mark.pgsql(
    'signalq_billing', files=['opportunities.sql', 'payments.sql'],
)
@pytest.mark.now('2021-09-30T22:00:00+00:00')
async def test_all_task_are_created_testpoint(testpoint, taxi_signalq_billing):
    @testpoint('b2b-payments-generation-all-created')
    def all_task_are_created_testpoint(arg):
        pass

    async with taxi_signalq_billing.spawn_task(
            'workers/b2b-payments-generation',
    ):
        await all_task_are_created_testpoint.wait_call()
