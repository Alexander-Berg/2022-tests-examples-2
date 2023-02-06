import pytest

from tests_coupons import util
from tests_coupons.referral import util as referral_util

PG_FILE = (
    'tests_coupons/stq/static/'
    'test_coupons_generate_referral_reward/pg_user_referrals.sql'
)

DEFAULT_ORDER_ID = 'ok_order_id'
DEFAULT_REFERRAL_PROMOCODE = 'test_referral_promocode'
DFAULT_DONOR_YANDEX_UID = 'creator_yandex_uid'
DFAULT_ACCEPTOR_YANDEX_UID = 'ok_acceptor_yandex_uid'
DEFAULT_CREATOR_SERIES = 'tst_crtr_s'


def get_task_kwargs(order_id=DEFAULT_ORDER_ID):
    return {'order_id': order_id}


def get_referral_completion(pgsql, order_id=DEFAULT_ORDER_ID):
    query = (
        f'SELECT * FROM referral.referral_completions'
        f' WHERE order_id=\'{order_id}\''
    )
    db_cursor = pgsql[referral_util.REFERRALS_DB_NAME].cursor()
    db_cursor.execute(query)
    columns = [desc[0] for desc in db_cursor.description]
    rows = list(db_cursor)
    if rows:
        return [dict(zip(columns, row)) for row in rows][0]
    return None


def get_expected_notify_stq_call(
        promocode,
        idempotence_token,
        referral_promocode=DEFAULT_REFERRAL_PROMOCODE,
        yandex_uid=DFAULT_DONOR_YANDEX_UID,
):
    return {
        'promocode': promocode,
        'idempotence_token': idempotence_token,
        'referral_promocode': referral_promocode,
        'yandex_uid': yandex_uid,
    }


def check_results(
        pgsql,
        promocodes,
        stq,
        is_success=True,
        order_id=DEFAULT_ORDER_ID,
        series_id=DEFAULT_CREATOR_SERIES,
        token=None,
        notify_stq_kwargs=None,
):
    referral_completion = get_referral_completion(pgsql, order_id=order_id)
    db_promocodes = [doc for doc in promocodes.find()]

    if is_success:
        assert referral_completion['series_id'] == series_id
        if token is None:
            token = referral_completion['reward_token']
        assert referral_completion['reward_token'] == token

        assert len(db_promocodes) == 1

        genereated_promocode = db_promocodes[0]
        assert genereated_promocode['series_id'] == series_id
        assert genereated_promocode['generate_token'] == token

        assert stq.referral_reward_notify.times_called == 1
        notify_call = stq.referral_reward_notify.next_call()
        notify_call['kwargs'].pop('log_extra')

        expected_call = get_expected_notify_stq_call(
            promocode=genereated_promocode['code'], idempotence_token=token,
        )
        expected_call.update(**(notify_stq_kwargs or {}))
        assert notify_call['kwargs'] == expected_call
    else:
        assert not db_promocodes
        assert stq.referral_reward_notify.times_called == 0


@pytest.mark.parametrize('collections_tag', util.PROMOCODES_DB_MODE_PARAMS)
async def test_ok(stq_runner, pgsql, mongodb, stq, collections_tag):
    task_kwargs = get_task_kwargs()
    await stq_runner.coupons_generate_referral_reward.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    promocodes = util.tag_to_promocodes_for_read(mongodb, collections_tag)
    check_results(pgsql, promocodes, stq)


@pytest.mark.parametrize('collections_tag', util.PROMOCODES_DB_MODE_PARAMS)
async def test_existing_completion(
        stq_runner, pgsql, mongodb, stq, collections_tag,
):
    order_id = 'existing_completion_order'
    token = 'existing_reward_token'
    series_id = 'exst_series'
    task_kwargs = get_task_kwargs(order_id=order_id)

    await stq_runner.coupons_generate_referral_reward.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    promocodes = util.tag_to_promocodes_for_read(mongodb, collections_tag)
    check_results(
        pgsql,
        promocodes,
        stq,
        order_id=order_id,
        series_id=series_id,
        token=token,
        notify_stq_kwargs={
            'referral_promocode': 'existing_completion_promocode',
            'yandex_uid': 'existing_completion_uid',
        },
    )


@pytest.mark.parametrize(
    'order_id, is_ok_order',
    [
        pytest.param(DEFAULT_ORDER_ID, True),
        pytest.param('no_completion_order', False),
        pytest.param('already_rewarded_order', False),
    ],
)
@pytest.mark.parametrize('collections_tag', util.PROMOCODES_DB_MODE_PARAMS)
async def test_no_reward(
        stq_runner,
        pgsql,
        mongodb,
        stq,
        order_id,
        is_ok_order,
        collections_tag,
):
    order_id = order_id
    task_kwargs = get_task_kwargs(order_id=order_id)

    await stq_runner.coupons_generate_referral_reward.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    is_success = is_ok_order
    promocodes = util.tag_to_promocodes_for_read(mongodb, collections_tag)
    check_results(
        pgsql, promocodes, stq, is_success=is_success, order_id=order_id,
    )


def get_pgsql_mark_n_completions(count):
    def insert_query(yandex_uid, order_id, referral_promocode):
        return f"""
            INSERT INTO referral.referral_completions
            (
            yandex_uid,
            order_id,
            promocode_id
            )
            VALUES
            (
            '{yandex_uid}',
            '{order_id}',
            (SELECT id from referral.promocodes
                WHERE promocode = '{referral_promocode}')
            )
        """

    return pytest.mark.pgsql(
        referral_util.REFERRALS_DB_NAME,
        files=[PG_FILE],
        queries=[
            *[
                insert_query(
                    yandex_uid=f'uid{i}',
                    order_id=f'order{i}',
                    referral_promocode=f'exceeded_limit_promocode',
                )
                for i in range(count)
            ],
            insert_query(
                yandex_uid=f'acceptor_uid',
                order_id=f'exceeded_limit_order',
                referral_promocode=f'exceeded_limit_promocode',
            ),
        ],
    )


@pytest.mark.parametrize(
    'order_id, is_exceeded',
    [
        pytest.param(
            'exceeded_limit_order',
            False,
            marks=get_pgsql_mark_n_completions(49),
        ),
        pytest.param(
            'exceeded_limit_order',
            True,
            marks=get_pgsql_mark_n_completions(50),
        ),
    ],
)
@pytest.mark.parametrize('collections_tag', util.PROMOCODES_DB_MODE_PARAMS)
async def test_exceeded_limit(
        stq_runner,
        pgsql,
        mongodb,
        stq,
        order_id,
        is_exceeded,
        collections_tag,
):
    order_id = order_id
    task_kwargs = get_task_kwargs(order_id=order_id)

    await stq_runner.coupons_generate_referral_reward.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    is_success = not is_exceeded
    promocodes = util.tag_to_promocodes_for_read(mongodb, collections_tag)
    check_results(
        pgsql,
        promocodes,
        stq,
        is_success=is_success,
        order_id=order_id,
        notify_stq_kwargs={
            'referral_promocode': 'exceeded_limit_promocode',
            'yandex_uid': 'exceeded_limit_uid',
        },
    )


@pytest.mark.parametrize('collections_tag', util.PROMOCODES_DB_MODE_PARAMS)
async def test_generate_error(
        stq_runner, pgsql, mongodb, stq, collections_tag,
):
    order_id = 'series_do_not_exist_order'
    task_kwargs = get_task_kwargs(order_id=order_id)
    await stq_runner.coupons_generate_referral_reward.call(
        task_id='whatever', args=[], kwargs=task_kwargs, expect_fail=True,
    )

    promocodes = util.tag_to_promocodes_for_read(mongodb, collections_tag)
    check_results(pgsql, promocodes, stq, is_success=False, order_id=order_id)


async def test_referral_completion_update_race(stq_runner, pgsql, testpoint):
    @testpoint('generate_reward_about_to_save_token_testpoint')
    def simulate_race(data):
        query = (
            f'UPDATE referral.referral_completions'
            f' SET reward_token = \'token_inserted_by_racing_task\''
            f' WHERE order_id = \'{DEFAULT_ORDER_ID}\''
        )
        pgsql[referral_util.REFERRALS_DB_NAME].cursor().execute(query)
        return {}

    task_kwargs = get_task_kwargs()
    await stq_runner.coupons_generate_referral_reward.call(
        task_id='whatever', args=[], kwargs=task_kwargs, expect_fail=True,
    )

    assert simulate_race.times_called == 1
