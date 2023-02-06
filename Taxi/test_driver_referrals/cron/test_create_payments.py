# pylint: disable=redefined-outer-name,unused-variable,global-statement
# pylint: disable=too-many-lines
import datetime
import hashlib

import pytest
import pytz

from taxi.billing.clients.models import billing_orders

from driver_referrals.common import models
from driver_referrals.generated.cron import run_cron
from test_driver_referrals import conftest

BILLING_REQUESTS = []  # type: ignore


async def get_status(context, park_id: str, driver_id: str) -> str:
    async with context.pg.master_pool.acquire() as conn:
        return await conn.fetchval(
            'SELECT status FROM referral_profiles '
            'WHERE park_id = $1 AND driver_id = $2',
            park_id,
            driver_id,
        )


@pytest.mark.config(DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """INSERT INTO tasks (id, task_date) """
        """VALUES ('task_id', '2019-04-20')""",
    ],
    files=['pg_driver_referrals.sql'],
)
async def test_create_payments_no_task(patch):
    @patch('driver_referrals.common.db.get_drivers_to_create_payments')
    def get_drivers_in_progress(*args, **kwargs):
        assert False

    await run_cron.main(
        ['driver_referrals.jobs.create_payments', '-t', '0', '-d'],
    )


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_WRITE_TO_PAYMENT_MAPPING=True,
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False,
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, mark_finished_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals.sql', 'pg_driver_referrals_base.sql'],
)
@pytest.mark.now('2019-04-20 13:01')
async def test_create_payments(cron_context, patch):
    global BILLING_REQUESTS
    BILLING_REQUESTS = []

    @patch(
        'taxi.billing.clients.billing_orders.BillingOrdersApiClient'
        '.process_event',
    )
    async def process_events(request, *args, **kwargs):
        global BILLING_REQUESTS
        BILLING_REQUESTS += [request]
        return billing_orders.ProcessDocResponse(doc_id=10)

    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {'last_name': 'A', 'first_name': 'B', 'middle_name': 'C'}

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    @patch('driver_referrals.common.hiring_candidates.activator_check')
    async def activator_check(_, driver, *args, **kwargs):
        bad_check = ['scout_kid_id_1']
        return driver.driver_id not in bad_check

    await run_cron.main(
        ['driver_referrals.jobs.create_payments', '-t', '0', '-d'],
    )

    def sort_key(x):
        return x.external_obj_id

    assert sorted(BILLING_REQUESTS, key=sort_key) == sorted(
        [
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r2/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r2/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '100',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r2/0/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r3/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r3/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '100',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r3/0/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r4/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r4/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '100',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r4/0/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r6/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r6/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '100',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r6/0/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r7/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r7/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '200',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r7/1/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r91/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r91/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '200',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r91/1/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r92/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r92/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '200',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r92/1/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r93/0/' + str(models.Role.INVITED)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r93/0/' + str(models.Role.INVITED)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '200',
                    'currency': 'RUB',
                    'db_id': 'p12',
                    'driver_license': 'p12_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r93/0/' + str(models.Role.INVITED)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p12_clid',
                    'uuid': 'd12',
                },
                service='driver-referrals',
                reason='',
            ),
        ],
        key=sort_key,
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        stats = await conn.fetch(
            'SELECT id, status, child_status, current_step '
            'FROM referral_profiles ORDER BY id',
        )
    stats = [dict(r) for r in stats]
    assert stats == [
        {
            'id': 'r0',
            'status': 'waiting_for_rule',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r1',
            'status': 'completed',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r2',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r3',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r4',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r6',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r7',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r8',
            'status': 'awaiting_promocode',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r9',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r91',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r92',
            'status': 'awaiting_child_reward',
            'child_status': 'awaiting_promocode',
            'current_step': 1,
        },
        {
            'id': 'r93',
            'status': 'completed',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r94',
            'status': 'awaiting_payment',
            'child_status': 'awaiting_promocode',
            'current_step': 1,
        },
    ]

    payment_stats_ids = [
        stat['id']
        for stat in stats
        if stat['status'] in ['awaiting_payment', 'completed']
    ]
    async with cron_context.pg.master_pool.acquire() as conn:
        invite_referral_count = await conn.fetchrow(
            """
            SELECT COUNT(*) as count
            FROM payment_id_to_referral_id
            WHERE referral_id = ANY($1)
            """,
            payment_stats_ids,
        )
    assert invite_referral_count['count'] == 3


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_WRITE_TO_PAYMENT_MAPPING=True,
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False,
    DRIVER_REFERRALS_PARK_SELFEMPLOYED_CONVERT_SETTING={
        'is_enabled': True,
        'steps': [
            {
                'rides': 1,
                'payment': 100,
                'child_promocode': {
                    'series': 'test_series',
                    'days_for_activation': 100,
                },
            },
            {
                'rides': 2,
                'payment': 200,
                'child_promocode': {
                    'series': 'test_series2',
                    'days_for_activation': 200,
                },
            },
        ],
    },
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, mark_finished_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=[
        'pg_driver_referrals_park_to_selfemployed.sql',
        'pg_driver_referrals_base.sql',
    ],
)
@pytest.mark.now('2019-04-20 13:01')
async def test_create_payments_for_park_to_selfemployed(
        cron_context,
        patch,
        mockserver,
        mock_unique_drivers_retrieve_by_uniques,
):
    global BILLING_REQUESTS
    BILLING_REQUESTS = []

    @patch(
        'taxi.billing.clients.billing_orders.BillingOrdersApiClient'
        '.process_event',
    )
    async def process_events(request, *args, **kwargs):
        global BILLING_REQUESTS
        BILLING_REQUESTS += [request]
        return billing_orders.ProcessDocResponse(doc_id=10)

    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {'last_name': 'A', 'first_name': 'B', 'middle_name': 'C'}

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    uniques = [
        {
            'park_id': 'p1',
            'driver_profile_id': 'd1',
            'park_driver_profile_id': 'p1_d1',
        },
        {
            'park_id': 'p2',
            'driver_profile_id': 'd2',
            'park_driver_profile_id': 'p2_d2',
        },
        {
            'park_id': 'p3',
            'driver_profile_id': 'd3',
            'park_driver_profile_id': 'p3_d3',
        },
        {
            'park_id': 'p4',
            'driver_profile_id': 'd4',
            'park_driver_profile_id': 'p4_d4',
        },
        {
            'park_id': 'p5',
            'driver_profile_id': 'd5',
            'park_driver_profile_id': 'p5_d5',
        },
        {
            'park_id': 'p6',
            'driver_profile_id': 'd6',
            'park_driver_profile_id': 'p6_d6',
        },
        {
            'park_id': 'p7',
            'driver_profile_id': 'd7',
            'park_driver_profile_id': 'p7_d7',
        },
        {
            'park_id': 'p8',
            'driver_profile_id': 'd8',
            'park_driver_profile_id': 'p8_d8',
        },
        {
            'park_id': 'p9',
            'driver_profile_id': 'd9',
            'park_driver_profile_id': 'p9_d9',
        },
        {
            'park_id': 'p91',
            'driver_profile_id': 'd91',
            'park_driver_profile_id': 'p91_d91',
        },
        {
            'park_id': 'p92',
            'driver_profile_id': 'd92',
            'park_driver_profile_id': 'p92_d92',
        },
    ]

    mock_unique_drivers_retrieve_by_uniques(
        {
            'p1_d1': uniques,
            'p2_d2': uniques,
            'p3_d3': uniques,
            'p4_d4': uniques,
            'p5_d5': uniques,
            'p6_d6': uniques,
            'p7_d7': uniques,
            'p8_d8': uniques,
            'p9_d9': uniques,
            'p91_d91': uniques,
            'p92_d92': uniques,
        },
    )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    async def orders_list(request):
        return {
            'orders': [
                {
                    'id': 'order_id_0',
                    'short_id': 123,
                    'status': 'complete',
                    'created_at': '2020-01-01T00:00:00+00:00',
                    'booked_at': '2020-01-01T00:00:00+00:00',
                    'provider': 'platform',
                    'address_from': {
                        'address': (
                            'Street hail: Russia,'
                            ' Moscow, Troparyovsky Forest Park'
                        ),
                        'lat': 55.734803,
                        'lon': 37.643132,
                    },
                    'amenities': [],
                    'events': [],
                    'route_points': [],
                },
            ],
            'limit': 1,
        }

    await run_cron.main(
        ['driver_referrals.jobs.create_payments', '-t', '0', '-d'],
    )

    def sort_key(x):
        return x.external_obj_id

    assert sorted(BILLING_REQUESTS, key=sort_key) == sorted(
        [
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r7/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r7/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '200',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r7/1/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r6/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r6/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '100',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r6/0/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r91/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r91/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '200',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r91/1/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r92/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r92/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '200',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r92/1/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
        ],
        key=sort_key,
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        stats = await conn.fetch(
            'SELECT id, status, child_status, current_step '
            'FROM referral_profiles ORDER BY id',
        )
    stats = [dict(r) for r in stats]
    assert stats == [
        {
            'id': 'r1',
            'status': 'completed',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r6',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r7',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r8',
            'status': 'awaiting_promocode',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r9',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r91',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r92',
            'status': 'awaiting_child_reward',
            'child_status': 'awaiting_promocode',
            'current_step': 1,
        },
    ]

    payment_stats_ids = [
        stat['id']
        for stat in stats
        if stat['status'] in ['awaiting_payment', 'completed']
    ]
    async with cron_context.pg.master_pool.acquire() as conn:
        invite_referral_count = await conn.fetchrow(
            """
            SELECT COUNT(*) as count
            FROM payment_id_to_referral_id
            WHERE referral_id = ANY($1)
            """,
            payment_stats_ids,
        )
    assert invite_referral_count['count'] == 2


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_WRITE_TO_PAYMENT_MAPPING=True,
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False,
    DRIVER_REFERRALS_PARK_SELFEMPLOYED_CONVERT_SETTING={
        'is_enabled': True,
        'steps': [],
    },
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, mark_finished_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=[
        'pg_driver_referrals_park_to_selfemployed.sql',
        'pg_driver_referrals_base.sql',
    ],
)
@pytest.mark.now('2019-04-20 13:01')
async def test_create_payments_for_park_to_selfemployed_wo_config(
        cron_context,
        patch,
        mockserver,
        mock_unique_drivers_retrieve_by_uniques,
):
    global BILLING_REQUESTS
    BILLING_REQUESTS = []

    @patch(
        'taxi.billing.clients.billing_orders.BillingOrdersApiClient'
        '.process_event',
    )
    async def process_events(request, *args, **kwargs):
        global BILLING_REQUESTS
        BILLING_REQUESTS += [request]
        return billing_orders.ProcessDocResponse(doc_id=10)

    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {'last_name': 'A', 'first_name': 'B', 'middle_name': 'C'}

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    uniques = [
        {
            'park_id': 'p1',
            'driver_profile_id': 'd1',
            'park_driver_profile_id': 'p1_d1',
        },
        {
            'park_id': 'p2',
            'driver_profile_id': 'd2',
            'park_driver_profile_id': 'p2_d2',
        },
        {
            'park_id': 'p3',
            'driver_profile_id': 'd3',
            'park_driver_profile_id': 'p3_d3',
        },
        {
            'park_id': 'p4',
            'driver_profile_id': 'd4',
            'park_driver_profile_id': 'p4_d4',
        },
        {
            'park_id': 'p5',
            'driver_profile_id': 'd5',
            'park_driver_profile_id': 'p5_d5',
        },
        {
            'park_id': 'p6',
            'driver_profile_id': 'd6',
            'park_driver_profile_id': 'p6_d6',
        },
        {
            'park_id': 'p7',
            'driver_profile_id': 'd7',
            'park_driver_profile_id': 'p7_d7',
        },
        {
            'park_id': 'p8',
            'driver_profile_id': 'd8',
            'park_driver_profile_id': 'p8_d8',
        },
        {
            'park_id': 'p9',
            'driver_profile_id': 'd9',
            'park_driver_profile_id': 'p9_d9',
        },
        {
            'park_id': 'p91',
            'driver_profile_id': 'd91',
            'park_driver_profile_id': 'p91_d91',
        },
        {
            'park_id': 'p92',
            'driver_profile_id': 'd92',
            'park_driver_profile_id': 'p92_d92',
        },
    ]

    mock_unique_drivers_retrieve_by_uniques(
        {
            'p1_d1': uniques,
            'p2_d2': uniques,
            'p3_d3': uniques,
            'p4_d4': uniques,
            'p5_d5': uniques,
            'p6_d6': uniques,
            'p7_d7': uniques,
            'p8_d8': uniques,
            'p9_d9': uniques,
            'p91_d91': uniques,
            'p92_d92': uniques,
        },
    )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    async def orders_list(request):
        return {
            'orders': [
                {
                    'id': 'order_id_0',
                    'short_id': 123,
                    'status': 'complete',
                    'created_at': '2020-01-01T00:00:00+00:00',
                    'booked_at': '2020-01-01T00:00:00+00:00',
                    'provider': 'platform',
                    'address_from': {
                        'address': (
                            'Street hail: Russia,'
                            ' Moscow, Troparyovsky Forest Park'
                        ),
                        'lat': 55.734803,
                        'lon': 37.643132,
                    },
                    'amenities': [],
                    'events': [],
                    'route_points': [],
                },
            ],
            'limit': 1,
        }

    await run_cron.main(
        ['driver_referrals.jobs.create_payments', '-t', '0', '-d'],
    )

    def sort_key(x):
        return x.external_obj_id

    assert sorted(BILLING_REQUESTS, key=sort_key) == sorted(
        [
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r7/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r7/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '200',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r7/1/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r6/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r6/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '100',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r6/0/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r91/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r91/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '200',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r91/1/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r92/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r92/1/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.UTC,
                ),
                data={
                    'amount': '200',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r92/1/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
        ],
        key=sort_key,
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        stats = await conn.fetch(
            'SELECT id, status, child_status, current_step '
            'FROM referral_profiles ORDER BY id',
        )
    stats = [dict(r) for r in stats]
    assert stats == [
        {
            'id': 'r1',
            'status': 'completed',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r6',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r7',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r8',
            'status': 'awaiting_promocode',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r9',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r91',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r92',
            'status': 'awaiting_child_reward',
            'child_status': 'awaiting_promocode',
            'current_step': 1,
        },
    ]

    payment_stats_ids = [
        stat['id']
        for stat in stats
        if stat['status'] in ['awaiting_payment', 'completed']
    ]
    async with cron_context.pg.master_pool.acquire() as conn:
        invite_referral_count = await conn.fetchrow(
            """
            SELECT COUNT(*) as count
            FROM payment_id_to_referral_id
            WHERE referral_id = ANY($1)
            """,
            payment_stats_ids,
        )
    assert invite_referral_count['count'] == 2


@pytest.mark.parametrize(
    'payment_mapping_count',
    [
        pytest.param(
            0,
            marks=pytest.mark.config(
                DRIVER_REFERRALS_EATS_ENABLE_WRITE_TO_PAYMENT_MAPPING=False,
            ),
            id='saving_disabled',
        ),
        pytest.param(
            2,
            marks=pytest.mark.config(
                DRIVER_REFERRALS_EATS_ENABLE_WRITE_TO_PAYMENT_MAPPING=True,
            ),
            id='saving_enabled',
        ),
    ],
)
@pytest.mark.parametrize(
    ('locale', 'adjustment_comment'),
    [
        ('ru', 'Выплата реферального бонуса за A B C'),
        ('en', 'Payout of referral bonus for A B C'),
    ],
    ids=['ru', 'en'],
)
@pytest.mark.config(DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, mark_finished_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_eats.sql'],
)
@pytest.mark.now('2019-04-20 13:01')
@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
async def test_create_payments_eats(
        payment_mapping_count: int,
        locale: str,
        adjustment_comment: str,
        cron_context,
        mockserver,
        patch,
        mock_driver_profiles_drivers_profiles,
):
    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {
            'last_name': 'A',
            'first_name': 'B',
            'middle_name': 'C',
            'park_locale': locale,
        }

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    mock_driver_profiles_drivers_profiles(
        eats_keys={'d0': 10, 'd1': 11, 'd2': 12, 'd3': 13},
    )

    @mockserver.json_handler(
        '/eats-core-courier-salary/server/api/v1/courier-salary/adjustments',
    )
    async def _(request):
        assert request.json['courierId'] == 10
        assert request.json['amount'] in {100, 200}
        assert (
            request.headers['X-Idempotency-Token']
            == {
                200: '10_4b23bde84ff1b36362ae130b2c3b2c2b',
                100: '10_75c5d18d9da18c3549b86295ac9f7c3c',
            }[request.json['amount']]
        )
        assert request.json['comment'] == adjustment_comment

        return {
            'isSuccess': True,
            'adjustment': {
                'id': 1234,
                'courierId': request.json['courierId'],
                'reasonId': request.json['reasonId'],
                'amount': request.json['amount'],
                'date': request.json['date'],
                'comment': request.json['comment'],
            },
        }

    await run_cron.main(
        ['driver_referrals.jobs.create_payments', '-t', '0', '-d'],
    )

    assert await get_status(cron_context, 'p0', 'd0') == 'completed'
    assert await get_status(cron_context, 'p1', 'd1') == 'waiting_for_rule'
    assert await get_status(cron_context, 'p2', 'd2') == 'in_progress'
    assert await get_status(cron_context, 'p3', 'd3') == 'completed'

    async with cron_context.pg.master_pool.acquire() as conn:
        payment_ids = (
            (
                await conn.fetchrow(
                    """
                    SELECT array_agg(payment_id) AS payment_ids
                    FROM payment_id_to_referral_id
                    """,
                )
            )['payment_ids']
            or []
        )
        assert len(payment_ids) == payment_mapping_count
        assert all(payment_id == 'eats_1234' for payment_id in payment_ids)


@pytest.mark.config(DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, mark_finished_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_2.sql', 'pg_driver_referrals_base.sql'],
)
@pytest.mark.now('2019-04-20 13:01')
async def test_block_self_invites(cron_context, patch):
    @patch(
        'taxi.billing.clients.billing_orders.BillingOrdersApiClient'
        '.process_event',
    )
    async def process_events(request, *args, **kwargs):
        assert False

    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {'last_name': 'A', 'first_name': 'B', 'middle_name': 'C'}

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'SAME_LICENSE'

    await run_cron.main(
        ['driver_referrals.jobs.create_payments', '-t', '0', '-d'],
    )

    status = await get_status(cron_context, 'p2', 'd2')
    assert status == 'blocked'


@pytest.mark.config(DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, mark_finished_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_2.sql', 'pg_driver_referrals_base.sql'],
)
@pytest.mark.now('2019-04-20 13:01')
async def test_block_not_new(
        cron_context,
        patch,
        mockserver,
        mock_unique_drivers_retrieve_by_uniques,
):
    @patch(
        'taxi.billing.clients.billing_orders.BillingOrdersApiClient'
        '.process_event',
    )
    async def process_events(request, *args, **kwargs):
        assert False

    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {'last_name': 'A', 'first_name': 'B', 'middle_name': 'C'}

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    uniques = [
        {
            'park_id': 'p1',
            'driver_profile_id': 'd1',
            'park_driver_profile_id': 'p1_d1',
        },
        {
            'park_id': 'p2',
            'driver_profile_id': 'd2',
            'park_driver_profile_id': 'p2_d2',
        },
        {
            'park_id': 'p3',
            'driver_profile_id': 'd3',
            'park_driver_profile_id': 'p3_d3',
        },
    ]

    mock_unique_drivers_retrieve_by_uniques(
        {'p1_d1': uniques, 'p2_d2': uniques, 'p3_d3': uniques},
    )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    async def orders_list(request):
        return {
            'orders': [
                {
                    'id': 'order_id_0',
                    'short_id': 123,
                    'status': 'complete',
                    'created_at': '2020-01-01T00:00:00+00:00',
                    'booked_at': '2020-01-01T00:00:00+00:00',
                    'provider': 'platform',
                    'address_from': {
                        'address': (
                            'Street hail: Russia,'
                            ' Moscow, Troparyovsky Forest Park'
                        ),
                        'lat': 55.734803,
                        'lon': 37.643132,
                    },
                    'amenities': [],
                    'events': [],
                    'route_points': [],
                },
            ],
            'limit': 1,
        }

    await run_cron.main(
        ['driver_referrals.jobs.create_payments', '-t', '0', '-d'],
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        status = await conn.fetchval(
            'SELECT status FROM referral_profiles '
            'WHERE park_id = \'p2\' AND driver_id = \'d2\'',
        )

    assert status == 'blocked'
