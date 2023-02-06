import collections
import datetime
import decimal

import pytest

from agent import const

NOT_UPDATED_DATETIME = datetime.datetime(
    2021, 2, 3, 0, tzinfo=datetime.timezone.utc,
)

TEST_MOCK_DATETIME = datetime.datetime(
    2020, 12, 31, 21, 0, tzinfo=datetime.timezone.utc,
)
NOT_ENOUGH_SUBPROD_DATETIME = datetime.datetime(
    2021, 2, 3, 0, tzinfo=datetime.timezone.utc,
)
TEST_BILLING_DATETIME = datetime.datetime(
    2021, 10, 11, 10, 1, 2, tzinfo=datetime.timezone.utc,
)

StqArgs = collections.namedtuple(
    'Stq_args', 'purchase_id subproduct_id price login address_id project',
)

DATA = {
    'task_id': '1111',
    'args': StqArgs('1111', 1, 222.33, 'mikh-vasily', 1, 'test_taxi_project'),
}
PROMO_DATA = {
    'task_id': '4444',
    'args': StqArgs(
        '4444', 3, 222.11, 'mikh-vasily', None, 'test_taxi_project',
    ),
}
NOT_ENOUGH_SUBPROD_DATA = {
    'task_id': '3333',
    'args': StqArgs('3333', 2, 333.33, 'mikh-vasily', None, ''),
}
NOT_ENOUGH_COINS_DATA = {
    'task_id': '2222',
    'args': StqArgs('2222', 1, 333.33, 'webalex', None, 'test_taxi_project'),
}
NOT_ENOUGH_COINS_DATA_PROMO = {
    'task_id': '5555',
    'args': StqArgs('5555', 3, 222.11, 'webalex', None, 'test_taxi_project'),
}
BAD_BILLING_REQ_DATA = {
    'task_id': '400',
    'args': StqArgs('400', 3, 222.11, 'webalex', None, 'test_taxi_project'),
}
BAD_BILLING_REQ_DATA2 = {
    'task_id': '404',
    'args': StqArgs('404', 3, 222.11, 'webalex', None, 'test_taxi_project'),
}
INIT_STATUS_DATA = {
    'task_id': '111',
    'args': StqArgs(
        '111', 3, 222.33, 'mikh-vasily', None, 'test_taxi_project',
    ),
}
RESERVED_STATUS_DATA = {
    'task_id': '666',
    'args': StqArgs(
        '666', 3, 222.11, 'mikh-vasily', None, 'test_taxi_project',
    ),
}


def get_expected_billing_args(data):
    return {
        'data': {
            'account': {
                'entity_external_id': 'staff/%s' % data['args'].login,
                'agreement_id': 'wallet/test_taxi_project',
                'currency': 'XXX',
                'sub_account': 'deposit',
            },
            'amount': '%s' % data['args'].price,
            'details': {
                'transaction_id': data['args'].purchase_id,
                'method': 'charge',
                'operation_type': 'payment',
            },
            'method': 'charge',
            'operation_type': 'payment',
            'schema_version': 'v1',
        },
        'external_ref': '1',
        'kind': 'arbitrary_wallet',
        'topic': 'agent/coins/%s' % data['args'].purchase_id,
        'event_at': '2021-01-01T03:00:00+03:00',
    }


async def check_db_state(web_context, input_data, output_data):
    async with web_context.pg.slave_pool.acquire() as conn:
        purchase_query = (
            'SELECT p.status_key, '
            '    p.created,'
            '    p.updated as p_up, '
            '    p.goods_detail_id, '
            '    p.address_id,'
            '    p.login,'
            '    p.price,'
            '    pc.id as promo_id,'
            '    pc.updated as promo_up,'
            '    pc.used as promo_used,'
            '    sp.amount,'
            '    sp.updated as sp_up, '
            '    pl.doc_id as billing_doc_id, '
            '    pl.id as pl_id, '
            '    pl.dt as pl_dt, '
            '    pl.login as pl_login, '
            '    pl.project as pl_project, '
            '    pl.value as pl_value, '
            '    pl.operation_type as pl_ot, '
            '    pl.section_type as pl_st, '
            '    pl.description as pl_desc, '
            '    pl.viewed as pl_viewed '
            'FROM agent.purchases p '
            '    LEFT JOIN agent.billing_operations_history pl '
            '       ON p.billing_operations_history_id = pl.id'
            '    LEFT JOIN agent.promocodes pc ON p.promocode_id = pc.id '
            '    LEFT JOIN agent.goods_detail sp ON p.goods_de'
            'tail_id = sp.id '
            'WHERE uid = \'{}\''.format(input_data['task_id'])
        )
        purchase_result = await conn.fetchrow(purchase_query)
        assert purchase_result['created'] == TEST_MOCK_DATETIME
        assert purchase_result['status_key'] == output_data['p_status']
        assert purchase_result['p_up'] == TEST_MOCK_DATETIME
        assert (
            purchase_result['billing_doc_id'] == output_data['billing_doc_id']
        )
        assert purchase_result['amount'] == output_data['finish_amount']
        assert purchase_result['sp_up'] == output_data['updated']
        assert purchase_result['promo_id'] == output_data['promo_id']
        assert purchase_result['promo_up'] == output_data['promo_up']
        assert purchase_result['promo_used'] == output_data['promo_used']
        assert float(purchase_result['price']) == input_data['args'].price
        assert purchase_result['address_id'] == input_data['args'].address_id
        assert purchase_result['login'] == input_data['args'].login
        assert purchase_result['pl_id'] == output_data['pl_id']
        assert purchase_result['pl_dt'] == output_data['pl_dt']
        assert purchase_result['pl_login'] == output_data['pl_login']
        assert purchase_result['pl_project'] == output_data['pl_project']
        assert purchase_result['pl_value'] == output_data['pl_value']
        assert purchase_result['pl_ot'] == output_data['pl_ot']
        assert purchase_result['pl_st'] == output_data['pl_st']
        assert purchase_result['pl_desc'] == output_data['pl_desc']
        assert purchase_result['pl_viewed'] == output_data['pl_viewed']
        promo_query = 'SELECT * FROM agent.promocodes WHERE id = {}'.format(
            output_data['promocode_id'],
        )
        promo_result = await conn.fetchrow(promo_query)
        assert promo_result['used'] == output_data['real_used']
        assert promo_result['updated'] == output_data['real_promo_up']


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'test_taxi_project': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
            'wallet': 'test_taxi_project',
        },
    },
)
@pytest.mark.now('2021-01-01T00:00:00')
@pytest.mark.parametrize(
    'input_data, output_data, expected_billing_args',
    [
        (
            DATA,
            {
                'p_status': const.PURCHASE_SUCCESSFULL_STATUS_KEY,
                'finish_amount': 1,
                'updated': TEST_MOCK_DATETIME,
                'promo_id': None,
                'promo_used': None,
                'promo_up': None,
                'promocode_id': 1,
                'real_used': False,
                'real_promo_up': NOT_ENOUGH_SUBPROD_DATETIME,
                'billing_doc_id': '11223344',
                'pl_id': '1111',
                'pl_dt': TEST_BILLING_DATETIME,
                'pl_login': 'mikh-vasily',
                'pl_project': 'test_taxi_project',
                'pl_ot': 'payment_charge',
                'pl_st': 'shop',
                'pl_desc': 'Purchase',
                'pl_viewed': False,
                'pl_value': 222.33,
            },
            get_expected_billing_args(DATA),
        ),
        (
            PROMO_DATA,
            {
                'p_status': const.PURCHASE_SUCCESSFULL_STATUS_KEY,
                'finish_amount': 2,
                'updated': TEST_MOCK_DATETIME,
                'promo_id': 1,
                'promo_used': True,
                'promo_up': TEST_MOCK_DATETIME,
                'promocode_id': 1,
                'real_used': True,
                'real_promo_up': TEST_MOCK_DATETIME,
                'billing_doc_id': '11223344',
                'pl_id': '4444',
                'pl_dt': TEST_BILLING_DATETIME,
                'pl_login': 'mikh-vasily',
                'pl_project': 'test_taxi_project',
                'pl_ot': 'payment_charge',
                'pl_st': 'shop',
                'pl_desc': 'Purchase',
                'pl_viewed': False,
                'pl_value': 222.11,
            },
            get_expected_billing_args(PROMO_DATA),
        ),
        (
            NOT_ENOUGH_SUBPROD_DATA,
            {
                'p_status': const.PURCHASE_NOT_ENOUGH_SUBPRODUCT_KEY,
                'finish_amount': 0,
                'updated': NOT_ENOUGH_SUBPROD_DATETIME,
                'promo_id': None,
                'promo_used': None,
                'promo_up': None,
                'promocode_id': 1,
                'real_used': False,
                'real_promo_up': NOT_ENOUGH_SUBPROD_DATETIME,
                'billing_doc_id': None,
                'pl_id': None,
                'pl_dt': None,
                'pl_login': None,
                'pl_project': None,
                'pl_ot': None,
                'pl_st': None,
                'pl_desc': None,
                'pl_viewed': None,
                'pl_value': None,
            },
            {},
        ),
    ],
)
async def test_purchase_task(
        stq_runner,
        web_context,
        mock_billing_orders,
        input_data,
        output_data,
        expected_billing_args,
):
    await stq_runner.agent_purchase_queue.call(
        task_id=input_data['task_id'], args=input_data['args'],
    )
    await check_db_state(web_context, input_data, output_data)

    if expected_billing_args:
        assert mock_billing_orders.has_calls
        assert mock_billing_orders.times_called == 1
        _request_billing_orders = mock_billing_orders.next_call()['request']
        assert _request_billing_orders.json == expected_billing_args


@pytest.mark.now('2021-01-01T00:00:00')
@pytest.mark.parametrize(
    'input_data, output_data',
    [
        (
            NOT_ENOUGH_COINS_DATA,
            {
                'p_status': const.PURCHASE_NOT_ENOUGH_COINS_KEY,
                'finish_amount': 2,
                'updated': TEST_MOCK_DATETIME,
                'promo_id': None,
                'promo_used': None,
                'promo_up': None,
                'promocode_id': 1,
                'real_used': False,
                'real_promo_up': NOT_ENOUGH_SUBPROD_DATETIME,
                'billing_doc_id': None,
                'pl_id': None,
                'pl_dt': None,
                'pl_login': None,
                'pl_project': None,
                'pl_ot': None,
                'pl_st': None,
                'pl_desc': None,
                'pl_viewed': None,
                'pl_value': None,
            },
        ),
        (
            NOT_ENOUGH_COINS_DATA_PROMO,
            {
                'p_status': const.PURCHASE_NOT_ENOUGH_COINS_KEY,
                'finish_amount': 3,
                'updated': TEST_MOCK_DATETIME,
                'promo_id': None,
                'promo_used': None,
                'promo_up': None,
                'promocode_id': 1,
                'real_used': False,
                'real_promo_up': TEST_MOCK_DATETIME,
                'billing_doc_id': None,
                'pl_id': None,
                'pl_dt': None,
                'pl_login': None,
                'pl_project': None,
                'pl_ot': None,
                'pl_st': None,
                'pl_desc': None,
                'pl_viewed': None,
                'pl_value': None,
            },
        ),
    ],
)
async def test_purchase_task_not_enough_coins(
        stq_runner,
        web_context,
        mock_billing_not_coins,
        input_data,
        output_data,
):
    await stq_runner.agent_purchase_queue.call(
        task_id=input_data['task_id'], args=input_data['args'],
    )
    await check_db_state(web_context, input_data, output_data)


@pytest.mark.now('2021-01-01T00:00:00')
@pytest.mark.parametrize(
    'input_data, output_data',
    [
        (
            BAD_BILLING_REQ_DATA,
            {
                'p_status': const.PURCHASE_BILLING_ERROR_KEY,
                'finish_amount': 3,
                'updated': TEST_MOCK_DATETIME,
                'promo_id': None,
                'promo_used': None,
                'promo_up': None,
                'promocode_id': 1,
                'real_used': False,
                'real_promo_up': TEST_MOCK_DATETIME,
                'billing_doc_id': None,
                'pl_id': None,
                'pl_dt': None,
                'pl_login': None,
                'pl_project': None,
                'pl_ot': None,
                'pl_st': None,
                'pl_desc': None,
                'pl_viewed': None,
                'pl_value': None,
            },
        ),
        (
            BAD_BILLING_REQ_DATA2,
            {
                'p_status': const.PURCHASE_BILLING_ERROR_KEY,
                'finish_amount': 3,
                'updated': TEST_MOCK_DATETIME,
                'promo_id': None,
                'promo_used': None,
                'promo_up': None,
                'promocode_id': 1,
                'real_used': False,
                'real_promo_up': TEST_MOCK_DATETIME,
                'billing_doc_id': None,
                'pl_id': None,
                'pl_dt': None,
                'pl_login': None,
                'pl_project': None,
                'pl_ot': None,
                'pl_st': None,
                'pl_desc': None,
                'pl_viewed': None,
                'pl_value': None,
            },
        ),
    ],
)
async def test_purchase_task_bad_billing_request(
        stq_runner,
        web_context,
        mock_billing_bad_request,
        input_data,
        output_data,
):
    await stq_runner.agent_purchase_queue.call(
        task_id=input_data['task_id'], args=input_data['args'],
    )
    await check_db_state(web_context, input_data, output_data)


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'test_taxi_project': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
            'wallet': 'test_taxi_project',
        },
    },
)
@pytest.mark.now('2021-01-01T00:00:00')
@pytest.mark.parametrize(
    'input_data, output_data, expected_billing_args',
    [
        (
            INIT_STATUS_DATA,
            {
                'p_status': const.PURCHASE_SUCCESSFULL_STATUS_KEY,
                'finish_amount': 2,
                'updated': TEST_MOCK_DATETIME,
                'promo_id': 1,
                'promo_used': True,
                'promo_up': TEST_MOCK_DATETIME,
                'promocode_id': 1,
                'real_used': True,
                'real_promo_up': TEST_MOCK_DATETIME,
                'billing_doc_id': '11223344',
                'pl_id': '111',
                'pl_dt': TEST_BILLING_DATETIME,
                'pl_login': 'mikh-vasily',
                'pl_project': 'test_taxi_project',
                'pl_ot': 'payment_charge',
                'pl_st': 'shop',
                'pl_desc': 'Purchase',
                'pl_viewed': False,
                'pl_value': 222.33,
            },
            get_expected_billing_args(INIT_STATUS_DATA),
        ),
        (
            {
                'task_id': '222',
                'args': StqArgs(
                    '222', 3, 222.33, 'mikh-vasily', None, 'test_taxi_project',
                ),
            },
            {
                'p_status': const.PURCHASE_SUCCESSFULL_STATUS_KEY,
                'finish_amount': 3,
                'updated': NOT_UPDATED_DATETIME,
                'promo_id': 3,
                'promo_used': True,
                'promo_up': NOT_UPDATED_DATETIME,
                'promocode_id': 3,
                'real_used': True,
                'real_promo_up': NOT_UPDATED_DATETIME,
                'billing_doc_id': 'test_doc',
                'pl_id': '222',
                'pl_dt': NOT_UPDATED_DATETIME,
                'pl_login': 'mikh-vasily',
                'pl_project': 'test_taxi_project',
                'pl_ot': 'payment_charge',
                'pl_st': 'shop',
                'pl_desc': 'Purchase',
                'pl_viewed': False,
                'pl_value': decimal.Decimal('222.33'),
            },
            {},
        ),
        (
            {
                'task_id': '333',
                'args': StqArgs(
                    '333', 3, 222.33, 'mikh-vasily', None, 'test_taxi_project',
                ),
            },
            {
                'p_status': const.PURCHASE_NOT_ENOUGH_SUBPRODUCT_KEY,
                'finish_amount': 3,
                'updated': NOT_ENOUGH_SUBPROD_DATETIME,
                'promo_id': None,
                'promo_used': None,
                'promo_up': None,
                'promocode_id': 1,
                'real_used': False,
                'real_promo_up': NOT_ENOUGH_SUBPROD_DATETIME,
                'billing_doc_id': None,
                'pl_id': None,
                'pl_dt': None,
                'pl_login': None,
                'pl_project': None,
                'pl_ot': None,
                'pl_st': None,
                'pl_desc': None,
                'pl_viewed': None,
                'pl_value': None,
            },
            {},
        ),
        (
            {
                'task_id': '444',
                'args': StqArgs(
                    '444', 3, 222.33, 'mikh-vasily', None, 'test_taxi_project',
                ),
            },
            {
                'p_status': const.PURCHASE_NOT_ENOUGH_COINS_KEY,
                'finish_amount': 3,
                'updated': NOT_ENOUGH_SUBPROD_DATETIME,
                'promo_id': None,
                'promo_used': None,
                'promo_up': None,
                'promocode_id': 1,
                'real_used': False,
                'real_promo_up': NOT_ENOUGH_SUBPROD_DATETIME,
                'billing_doc_id': None,
                'pl_id': None,
                'pl_dt': None,
                'pl_login': None,
                'pl_project': None,
                'pl_ot': None,
                'pl_st': None,
                'pl_desc': None,
                'pl_viewed': None,
                'pl_value': None,
            },
            {},
        ),
        (
            {
                'task_id': '555',
                'args': StqArgs(
                    '555', 3, 222.11, 'mikh-vasily', None, 'test_taxi_project',
                ),
            },
            {
                'p_status': const.PURCHASE_BILLING_ERROR_KEY,
                'finish_amount': 3,
                'updated': NOT_ENOUGH_SUBPROD_DATETIME,
                'promo_id': None,
                'promo_used': None,
                'promo_up': None,
                'promocode_id': 1,
                'real_used': False,
                'real_promo_up': NOT_ENOUGH_SUBPROD_DATETIME,
                'billing_doc_id': None,
                'pl_id': None,
                'pl_dt': None,
                'pl_login': None,
                'pl_project': None,
                'pl_ot': None,
                'pl_st': None,
                'pl_desc': None,
                'pl_viewed': None,
                'pl_value': None,
            },
            {},
        ),
        (
            RESERVED_STATUS_DATA,
            {
                'p_status': const.PURCHASE_SUCCESSFULL_STATUS_KEY,
                'finish_amount': 3,
                'updated': NOT_ENOUGH_SUBPROD_DATETIME,
                'promo_id': 3,
                'promo_used': True,
                'promo_up': NOT_ENOUGH_SUBPROD_DATETIME,
                'promocode_id': 3,
                'real_used': True,
                'real_promo_up': NOT_ENOUGH_SUBPROD_DATETIME,
                'billing_doc_id': '11223344',
                'pl_id': '666',
                'pl_dt': TEST_BILLING_DATETIME,
                'pl_login': 'mikh-vasily',
                'pl_project': 'test_taxi_project',
                'pl_ot': 'payment_charge',
                'pl_st': 'shop',
                'pl_desc': 'Purchase',
                'pl_viewed': False,
                'pl_value': 222.11,
            },
            get_expected_billing_args(RESERVED_STATUS_DATA),
        ),
    ],
)
async def test_any_status_purchase_task(
        stq_runner,
        web_context,
        mock_billing_orders,
        input_data,
        output_data,
        expected_billing_args,
):
    await stq_runner.agent_purchase_queue.call(
        task_id=input_data['task_id'], args=input_data['args'],
    )
    await check_db_state(web_context, input_data, output_data)

    if expected_billing_args:
        assert mock_billing_orders.has_calls
        assert mock_billing_orders.times_called == 1
        _request_billing_orders = mock_billing_orders.next_call()['request']
        assert _request_billing_orders.json == expected_billing_args
    else:
        assert not mock_billing_orders.has_calls
