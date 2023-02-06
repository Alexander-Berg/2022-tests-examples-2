import pytest


EXPECTED_PARKS_INFO = [
    {
        'park_id': 'p5',
        'clid': 'clid3',
        'city_id': 'CITY_ID5',
        'payment_amount': '500',
    },
    {
        'park_id': 'p4',
        'clid': 'clid3',
        'city_id': 'CITY_ID4',
        'payment_amount': '160',
    },
    {
        'park_id': 'p3',
        'clid': 'clid2',
        'city_id': 'CITY_ID2',
        'payment_amount': '80',
    },
    {
        'park_id': 'p2',
        'clid': 'clid2',
        'city_id': 'CITY_ID1',
        'payment_amount': '60',
    },
]


@pytest.mark.parametrize(
    'payments_not_created_at, billing_orders_req_path',
    [
        pytest.param(
            '2021-10-01T22:00:00+00:00',
            'billing_orders_request.json',
            marks=pytest.mark.now('2021-09-30T22:00:00+00:00'),
        ),
        pytest.param(
            '2021-10-05T21:00:00+00:00',
            'billing_orders_request_2.json',
            marks=[
                pytest.mark.now('2021-10-05T00:00:00+03:00'),
                pytest.mark.config(
                    SIGNALQ_BILLING_PARKS_PAYMENT_SETTINGS_V1={
                        'parks_payment_settings': {
                            '__default__': {
                                'amount_per_active_device': '40.0000',
                            },
                            'p2': {'amount_per_active_device': '3.0000'},
                            'p5': {'amount_per_active_device': '500.0000'},
                        },
                        'period1_min_device_statuses_count': 15,
                        'manual_next_run_at': '2021-10-05',
                    },
                ),
            ],
        ),
    ],
)
async def test_ok_not_cached(
        testpoint,
        pgsql,
        stq,
        stq_runner,
        billing_orders,
        taxi_signalq_billing,
        payments_not_created_at,
        billing_orders_req_path,
):
    billing_orders.set_request_path(billing_orders_req_path)

    @testpoint('monitoring-payments-yt-ok')
    def yt_ok_testpoint(arg):
        pass

    async with taxi_signalq_billing.spawn_task('workers/monitoring-payments'):
        await yt_ok_testpoint.wait_call()

    db = pgsql['signalq_billing'].cursor()
    db.execute(
        """
        SELECT park_id, payment_progress
        FROM signalq_billing.payments_info
        WHERE payments_date = '2021-10-01'
    """,
    )
    assert sorted(list(db), key=lambda x: x[0]) == sorted(
        [
            ('p2', 'in_progress'),
            ('p3', 'in_progress'),
            ('p4', 'in_progress'),
            ('p5', 'in_progress'),
        ],
        key=lambda x: x[0],
    )

    assert stq.signalq_billing_monitoring_payments.times_called == 1
    mp_call = stq.signalq_billing_monitoring_payments.next_call()

    parks_monitoring_info = mp_call['kwargs']['parks_monitoring_info']
    assert (
        parks_monitoring_info['payments_not_created_at']
        == payments_not_created_at
    )
    assert sorted(
        parks_monitoring_info['parks_info'], key=lambda x: x['park_id'],
    ) == sorted(EXPECTED_PARKS_INFO, key=lambda x: x['park_id'])

    await stq_runner.signalq_billing_monitoring_payments.call(
        task_id=mp_call['id'], args=mp_call['args'], kwargs=mp_call['kwargs'],
    )

    db = pgsql['signalq_billing'].cursor()
    db.execute(
        """
        SELECT park_id, payment_progress
        FROM signalq_billing.payments_info
        WHERE payments_date = '2021-10-01'
    """,
    )
    assert sorted(list(db), key=lambda x: x[0]) == sorted(
        [
            ('p2', 'created'),
            ('p3', 'created'),
            ('p4', 'in_progress'),
            ('p5', 'in_progress'),
        ],
        key=lambda x: x[0],
    )


@pytest.mark.pgsql('signalq_billing', files=['signalq_billing_not_set.sql'])
@pytest.mark.now('2021-09-30T22:00:00+00:00')
async def test_ok_cached(testpoint, taxi_signalq_billing):
    @testpoint('monitoring-payments-cached-ok')
    def cached_ok_testpoint(arg):
        pass

    async with taxi_signalq_billing.spawn_task('workers/monitoring-payments'):
        await cached_ok_testpoint.wait_call()


@pytest.mark.now('2021-09-30T22:00:00+00:00')
async def test_no_clusters(
        testpoint, replication, taxi_signalq_billing, pgsql,
):
    replication.set_no_active_clusters()

    @testpoint('monitoring-payments-empty-yt-clusters')
    def empty_yt_clusters_testpoint(arg):
        pass

    async with taxi_signalq_billing.spawn_task('workers/monitoring-payments'):
        await empty_yt_clusters_testpoint.wait_call()


@pytest.mark.config(
    SIGNALQ_BILLING_MONITORING_PAYMENTS_TASK_SETTINGS={
        'task_delay_secs': 0,
        'stq_common_delay_seconds': 0,
        'stq_reschedule_delay_mins': 0,
        'enabled': False,
    },
)
async def test_disabled(testpoint, taxi_signalq_billing):
    @testpoint('monitoring-payments-disabled')
    def disabled_task_testpoint(arg):
        pass

    async with taxi_signalq_billing.spawn_task('workers/monitoring-payments'):
        await disabled_task_testpoint.wait_call()


@pytest.mark.config(SIGNALQ_BILLING_INCLUDED_DEVICES={'serial_numbers': []})
async def test_no_serial_numbers(testpoint, taxi_signalq_billing):
    @testpoint('monitoring-payments-no-serial-numbers')
    def no_serial_numbers_testpoint(arg):
        pass

    async with taxi_signalq_billing.spawn_task('workers/monitoring-payments'):
        await no_serial_numbers_testpoint.wait_call()


@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=pytest.mark.now('2021-02-01T22:00:00+00:00')),
        pytest.param(marks=pytest.mark.now('2021-02-02T00:00:00+00:00')),
    ],
)
async def test_not_day_of_the_run(testpoint, taxi_signalq_billing):
    @testpoint('monitoring-payments-not-day-of-the-run')
    def not_day_of_the_run_testpoint(arg):
        pass

    async with taxi_signalq_billing.spawn_task('workers/monitoring-payments'):
        await not_day_of_the_run_testpoint.wait_call()


@pytest.mark.pgsql('signalq_billing', files=['signalq_billing.sql'])
@pytest.mark.now('2021-09-30T22:00:00+00:00')
async def test_all_task_are_created_testpoint(testpoint, taxi_signalq_billing):
    @testpoint('monitoring-payments-all-created')
    def all_task_are_created_testpoint(arg):
        pass

    async with taxi_signalq_billing.spawn_task('workers/monitoring-payments'):
        await all_task_are_created_testpoint.wait_call()
