import pytest

from tests_coupons.mocks import order_core as order_core_mocks
from tests_coupons.referral import util as referral_util

DEFAULT_ORDER_ID = 'test_order_id'
DEFAULT_YANDEX_UID = 'test_yandex_uid'

DEFAULT_COUPON_ID = 'test_coupon'

PG_FILE = (
    'tests_coupons/stq/static/test_complete_referral/pg_user_referrals.sql'
)


def get_task_kwargs(coupon_id=DEFAULT_COUPON_ID):
    return {
        'order_id': DEFAULT_ORDER_ID,
        'coupon_id': coupon_id,
        'yandex_uid': DEFAULT_YANDEX_UID,
    }


def get_referral_completions(pgsql):
    db_cursor = pgsql[referral_util.REFERRALS_DB_NAME].cursor()
    db_cursor.execute('SELECT * FROM referral.referral_completions')
    columns = [desc[0] for desc in db_cursor.description]
    rows = list(db_cursor)
    return [dict(zip(columns, row)) for row in rows]


def get_referral_promocode(pgsql, promocode):
    db_cursor = pgsql[referral_util.REFERRALS_DB_NAME].cursor()
    db_cursor.execute(
        f'SELECT * FROM referral.promocodes WHERE promocode=\'{promocode}\'',
    )
    columns = [desc[0] for desc in db_cursor.description]
    rows = list(db_cursor)
    return [dict(zip(columns, row)) for row in rows][0]


def get_order_coupon(coupon_id=DEFAULT_COUPON_ID, was_used=True, valid=True):
    return {'id': coupon_id, 'was_used': was_used, 'valid': valid}


def get_order_fields_response(
        order_id=DEFAULT_ORDER_ID,
        status='finished',
        taxi_status='complete',
        coupon=None,
):
    if coupon is None:
        coupon = get_order_coupon()

    fields = {
        'order': {
            '_id': order_id,
            'status': status,
            'taxi_status': taxi_status,
            'coupon': coupon,
        },
        'performer': {'candidate_index': 0},
    }
    return {
        'fields': fields,
        'order_id': order_id,
        'replica': 'secondary',
        'version': 'test_version',
    }


@pytest.fixture(name='task_client_mocks')
def _task_client_mocks(mockserver):
    class Context:
        # /order-core/v1/tc/order-fields
        order_fields = None

    context = Context()
    context.order_fields = order_core_mocks.v1_tc_order_fields(mockserver)
    return context


@pytest.mark.pgsql(referral_util.REFERRALS_DB_NAME, files=[PG_FILE])
@pytest.mark.parametrize('was_coupon_used', [True, False])
async def test_ok(stq_runner, pgsql, stq, task_client_mocks, was_coupon_used):
    task_kwargs = get_task_kwargs()

    task_client_mocks.order_fields.set_expectations(order_id=DEFAULT_ORDER_ID)
    task_client_mocks.order_fields.set_response(
        get_order_fields_response(
            coupon=get_order_coupon(was_used=was_coupon_used),
        ),
    )

    await stq_runner.complete_referral.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )
    referral_completions = get_referral_completions(pgsql)

    assert task_client_mocks.order_fields.times_called == 1

    if was_coupon_used:
        assert stq.coupons_generate_referral_reward.times_called == 1
        gen_reward_task = stq.coupons_generate_referral_reward.next_call()
        assert gen_reward_task['kwargs']['order_id'] == DEFAULT_ORDER_ID

        assert len(referral_completions) == 1
        promocode = get_referral_promocode(pgsql, DEFAULT_COUPON_ID)

        for key, value in {
                'yandex_uid': DEFAULT_YANDEX_UID,
                'order_id': DEFAULT_ORDER_ID,
                'promocode_id': promocode['id'],
        }.items():
            assert referral_completions[0][key] == value
    else:
        assert stq.coupons_generate_referral_reward.times_called == 0
        assert not referral_completions


@pytest.mark.pgsql(referral_util.REFERRALS_DB_NAME, files=[PG_FILE])
@pytest.mark.parametrize(
    'stq_task_kwargs, coupon',
    [
        pytest.param(
            {'coupon_id': 'non_existent_coupon'}, {}, id='Non existent coupon',
        ),
        pytest.param({}, {'was_used': False}, id='Unused coupon'),
        pytest.param({}, {'valid': False}, id='Invalid coupon'),
    ],
)
async def test_not_ok(
        stq_runner, pgsql, stq, task_client_mocks, stq_task_kwargs, coupon,
):
    task_kwargs = get_task_kwargs(**stq_task_kwargs)

    task_client_mocks.order_fields.set_expectations(order_id=DEFAULT_ORDER_ID)
    task_client_mocks.order_fields.set_response(
        get_order_fields_response(coupon=get_order_coupon(**coupon)),
    )

    await stq_runner.complete_referral.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )
    referral_completions = get_referral_completions(pgsql)

    assert task_client_mocks.order_fields.times_called == 1

    assert stq.coupons_generate_referral_reward.times_called == 0
    assert not referral_completions


@pytest.mark.pgsql(referral_util.REFERRALS_DB_NAME, files=[PG_FILE])
@pytest.mark.parametrize(
    'order_fields',
    [
        pytest.param({'status': 'not_finished'}, id='Status != finished'),
        pytest.param(
            {'taxi_status': 'not_complete'}, id='Taxi status != complete',
        ),
    ],
)
async def test_error(stq_runner, pgsql, stq, task_client_mocks, order_fields):
    task_kwargs = get_task_kwargs()

    task_client_mocks.order_fields.set_expectations(order_id=DEFAULT_ORDER_ID)
    task_client_mocks.order_fields.set_response(
        get_order_fields_response(**order_fields),
    )

    await stq_runner.complete_referral.call(
        task_id='whatever', args=[], kwargs=task_kwargs, expect_fail=True,
    )
    referral_completions = get_referral_completions(pgsql)

    assert task_client_mocks.order_fields.times_called == 1

    assert stq.coupons_generate_referral_reward.times_called == 0
    assert not referral_completions


@pytest.mark.pgsql(referral_util.REFERRALS_DB_NAME, files=[PG_FILE])
@pytest.mark.parametrize(
    'coupon_id, grr_called, stq_times_called',
    [
        ('test_coupon', True, 1),
        ('test_coupon1', True, 2),
        ('test_coupon2', False, 2),
    ],
)
async def test_rides_for_reward(
        stq_runner,
        pgsql,
        stq,
        task_client_mocks,
        coupon_id,
        grr_called,
        stq_times_called,
):
    task_kwargs = get_task_kwargs(coupon_id=coupon_id)

    task_client_mocks.order_fields.set_expectations(order_id=DEFAULT_ORDER_ID)
    task_client_mocks.order_fields.set_response(get_order_fields_response())

    for i in range(stq_times_called):
        await stq_runner.complete_referral.call(
            task_id=f'whatever_{i}', args=[], kwargs=task_kwargs,
        )
    referral_completions = get_referral_completions(pgsql)

    assert task_client_mocks.order_fields.times_called == stq_times_called

    assert stq.coupons_generate_referral_reward.times_called == int(grr_called)
    if grr_called:
        gen_reward_task = stq.coupons_generate_referral_reward.next_call()
        assert gen_reward_task['kwargs']['order_id'] == DEFAULT_ORDER_ID

        assert len(referral_completions) == 1
        promocode = get_referral_promocode(pgsql, coupon_id)

        for key, value in {
                'yandex_uid': DEFAULT_YANDEX_UID,
                'order_id': DEFAULT_ORDER_ID,
                'promocode_id': promocode['id'],
        }.items():
            assert referral_completions[0][key] == value
