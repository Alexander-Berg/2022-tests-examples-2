import datetime as dt

import dateutil
import psycopg2.extras
import pytest

_UPDATES_DISABLED = [pytest.mark.config(DEBT_COLLECTOR_MAX_NUM_CHANGES=0)]
_NOW = dt.datetime(2020, 12, 31, 23, 59, tzinfo=dt.timezone.utc)


def _make_immediate_collection(now):
    return {
        'strategy': {
            'kind': 'time_table',
            'metadata': {'schedule': [now.isoformat()]},
        },
        'installed_at': now.isoformat(),
    }


def make_query(debt_id, version=None, payments=None, collection=None):
    if payments is None:
        payments = [{'type': 'card', 'method': 'some_card_id'}]
    if collection is None:
        collection = {'strategy': {'kind': 'null', 'metadata': {}}}
    query = {
        'debt': {
            'id': debt_id,
            'metadata': {'zone': 'moscow'},
            'service': 'eats',
            'debtors': ['yandex/uid/some_uid', 'yandex/uid/another_uid'],
            'reason': {'code': 'some_code', 'metadata': {'from': 'admin'}},
            'collection': collection,
            'transactions_params': make_transactions_params(),
            'invoice': {
                'id': 'some_invoice_id',
                'id_namespace': 'some_namespace',
                'transactions_installation': 'eda',
                'originator': 'eats_payments',
            },
            'currency': 'RUB',
            'items_by_payment_type': {
                'debt': [
                    {
                        'payment_type': 'card',
                        'items': [{'item_id': 'food', 'amount': '30.5'}],
                    },
                ],
                'total': [
                    {
                        'payment_type': 'card',
                        'items': [{'item_id': 'food', 'amount': '40.5'}],
                    },
                ],
            },
            'payments': payments,
        },
    }
    if version is not None:
        query['debt']['version'] = version
    return query


def _make_sbp_link_payment():
    return {'type': 'sbp', 'method': 'sbp_link'}


def _make_sbp_qr_payment():
    return {'type': 'sbp', 'method': 'sbp_qr'}


def _make_cibus_payment():
    return {'type': 'cibus', 'method': 'some_cibus_method'}


def make_pay_query(debt_id, version):
    query = {
        'debt': {
            'id': debt_id,
            'service': 'eats',
            'reason': {'code': 'some_code', 'metadata': {'from': 'admin'}},
            'currency': 'RUB',
            'transactions_params': make_transactions_params(),
            'items_by_payment_type': make_items_by_payment_type(),
            'payments': [{'type': 'card', 'method': 'some_card_id'}],
            'version': version,
        },
    }
    return query


def make_illegal_pay_query(debt_id, version):
    query = {
        'debt': {
            'id': debt_id,
            'service': 'eats',
            'reason': {'code': 'some_code', 'metadata': {'from': 'admin'}},
            'currency': 'RUB',
            'transactions_params': make_transactions_params(),
            'items_by_payment_type': make_items_by_payment_type(),
            'version': version,
        },
    }
    return query


def make_minimal_pay_query(debt_id, version):
    query = {
        'debt': {
            'id': debt_id,
            'service': 'eats',
            'reason': {'code': 'some_code', 'metadata': {'from': 'admin'}},
            'currency': 'RUB',
            'payments': [{'type': 'card', 'method': 'some_card_id'}],
            'version': version,
        },
    }
    return query


def make_no_op_query(debt_id, version):
    query = {
        'debt': {
            'id': debt_id,
            'service': 'eats',
            'reason': {'code': 'some_code', 'metadata': {'from': 'admin'}},
            'version': version,
        },
    }
    return query


def make_items_by_payment_type(debt_amount='30.5'):
    return {
        'debt': [
            {
                'payment_type': 'card',
                'items': [{'item_id': 'food', 'amount': debt_amount}],
            },
        ],
        'total': [
            {
                'payment_type': 'card',
                'items': [{'item_id': 'food', 'amount': '40.5'}],
            },
        ],
    }


def make_status_change_query(debt_id, version):
    query = {
        'debt': {
            'id': debt_id,
            'service': 'eats',
            'reason': {'code': 'some_code', 'metadata': {'from': 'admin'}},
            'items_by_payment_type': make_items_by_payment_type(
                debt_amount='0',
            ),
            'version': version,
        },
    }
    return query


def make_transactions_params():
    return {
        'payment_timeout': 120,
        'user_ip': '127.0.0.1',
        'yandex_uid': 'some_uid',
        'antifraud_payload': {'antifraud': 1},
        'login_id': 'some_login_id',
        'wallet_payload': {'wallet': 2},
    }


@pytest.mark.parametrize(
    'method, num_queries, idempotency_token, query,'
    'expected_status, expected_version',
    [
        ('create', 1, None, make_query('some_debt_id'), 'unpaid', 1),
        (
            'create',
            1,
            None,
            make_query('some_debt_id', payments=[_make_sbp_link_payment()]),
            'unpaid',
            1,
        ),
        (
            'create',
            1,
            None,
            make_query('some_debt_id', payments=[_make_sbp_qr_payment()]),
            'unpaid',
            1,
        ),
        (
            'create',
            1,
            None,
            make_query('some_debt_id', payments=[_make_cibus_payment()]),
            'unpaid',
            1,
        ),
        ('update', 1, None, make_query('with_two_debtors_id', 3), 'unpaid', 4),
        (
            'update',
            1,
            None,
            make_no_op_query('with_two_debtors_id', 3),
            'unpaid',
            4,
        ),
        (
            'update',
            1,
            None,
            make_status_change_query('with_two_debtors_id', 3),
            'paid',
            4,
        ),
        (
            'pay',
            1,
            None,
            make_pay_query('with_two_debtors_id', 3),
            'unpaid',
            4,
        ),
        (
            'pay',
            1,
            None,
            make_minimal_pay_query('with_two_debtors_id', 3),
            'unpaid',
            4,
        ),
        ('create', 2, 'some_token', make_query('some_debt_id'), 'unpaid', 1),
        (
            'update',
            2,
            'some_token',
            make_query('with_two_debtors_id', 3),
            'unpaid',
            4,
        ),
        (
            'pay',
            2,
            'some_token',
            make_pay_query('with_two_debtors_id', 3),
            'unpaid',
            4,
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    DEBT_COLLECTOR_PLAN_IN_ADVANCE_ENABLED=True,
    DEBT_COLLECTOR_TRANSACTIONS_INSTALLATIONS={
        'eda': {
            'base_url': {'$mockserver': '/transactions-eda'},
            'tvm_name': 'transactions',
        },
    },
)
@pytest.mark.pgsql('eats_debt_collector', files=['eats_debt_collector.sql'])
async def test_change_debt(
        taxi_debt_collector,
        pgsql,
        mockserver,
        load_json,
        stq,
        mocked_time,
        method,
        num_queries,
        idempotency_token,
        query,
        expected_status,
        expected_version,
):
    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def _retrieve(request):
        return load_json('retrieve_response.json')

    debt_id = query['debt']['id']
    debt_before = await _fetch_debt(taxi_debt_collector, debt_id)
    debtors_before = (debt_before or {}).get('debtors', [])
    headers = _get_headers(idempotency_token)
    for _ in range(num_queries):

        response = await taxi_debt_collector.post(
            f'/v1/debt/{method}', query, headers=headers,
        )
        _check_collect_debt_calls(stq, debt_id, mocked_time.now())
        mocked_time.sleep(0.01)
        await taxi_debt_collector.invalidate_caches()
    assert response.status_code == 200
    assert response.json() == {}

    debt_after = _merge_dicts((debt_before or {}), query['debt'])
    expected_debtors = _with_status(
        query['debt'].get('debtors', debtors_before), expected_status,
    )

    if method == 'pay':
        collection = _make_immediate_collection(_NOW)
    else:
        collection = None
    expected_debt = _update(
        debt_after, version=expected_version, collection=collection,
    )
    if 'collection' in query['debt']:
        expected_debt['collection']['installed_at'] = _NOW.isoformat()
    await _check_has_debt(taxi_debt_collector, expected_debt)
    await _check_has_debtors(pgsql, debt_id, expected_debtors)


@pytest.mark.parametrize(
    'method, retrieve_code, idempotency_token, query, status_code',
    [
        ('create', 404, None, make_query('some_debt_id'), 400),
        ('create', 200, None, make_query('with_two_debtors_id'), 409),
        ('update', None, None, make_query('with_two_debtors_id', 1), 409),
        pytest.param(
            'update',
            None,
            None,
            make_query('with_two_debtors_id', 3),
            400,
            marks=_UPDATES_DISABLED,
        ),
        (
            'update',
            None,
            'initial_token',
            make_query('with_two_debtors_id', 3),
            409,
        ),
        ('pay', None, None, make_pay_query('with_two_debtors_id', 1), 409),
        pytest.param(
            'pay',
            None,
            None,
            make_pay_query('with_two_debtors_id', 3),
            400,
            marks=_UPDATES_DISABLED,
        ),
        (
            'pay',
            None,
            'initial_token',
            make_pay_query('with_two_debtors_id', 3),
            409,
        ),
    ],
)
@pytest.mark.config(
    DEBT_COLLECTOR_TRANSACTIONS_INSTALLATIONS={
        'eda': {
            'base_url': {'$mockserver': '/transactions-eda'},
            'tvm_name': 'transactions',
        },
    },
)
@pytest.mark.pgsql('eats_debt_collector', files=['eats_debt_collector.sql'])
async def test_change_debt_failure(
        taxi_debt_collector,
        mockserver,
        load_json,
        pgsql,
        stq,
        method,
        retrieve_code,
        idempotency_token,
        query,
        status_code,
):
    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def _retrieve(request):
        if retrieve_code == 404:
            return mockserver.make_response(
                json={'code': '404', 'message': 'invoice not found'},
                status=404,
            )
        return load_json('retrieve_response.json')

    debt_id = query['debt']['id']
    debt_before = await _fetch_debt(taxi_debt_collector, debt_id)
    headers = _get_headers(idempotency_token)
    response = await taxi_debt_collector.post(
        f'/v1/debt/{method}', query, headers=headers,
    )
    assert response.status_code == status_code
    assert response.json()['code'] == str(status_code)
    assert stq.collect_debt.times_called == 0
    await _check_has_debt(taxi_debt_collector, debt_before, debt_id)
    await _check_has_debtors(
        pgsql,
        debt_id,
        _with_status(debt_before['debtors'] if debt_before else [], 'unpaid'),
    )


@pytest.mark.config(DEBT_COLLECTOR_PLAN_IN_ADVANCE_ENABLED=True)
@pytest.mark.pgsql('eats_debt_collector', files=['eats_debt_collector.sql'])
@pytest.mark.now(_NOW.isoformat())
async def test_pay_debt(taxi_debt_collector, pgsql, stq):
    debt_id = 'with_two_debtors_id'
    debt_before = await _fetch_debt(taxi_debt_collector, debt_id)
    query = make_pay_query(debt_id, 3)
    response = await taxi_debt_collector.post(f'/v1/debt/pay', query)
    assert response.status_code == 200
    _check_collect_debt_calls(stq, debt_id, _NOW.replace(tzinfo=None))

    await _check_has_debt(
        taxi_debt_collector,
        _update(
            debt_before,
            version=4,
            payments=query['debt']['payments'],
            items_by_payment_type=query['debt']['items_by_payment_type'],
            transactions_params=query['debt']['transactions_params'],
            collection=_make_immediate_collection(_NOW),
        ),
    )
    await _check_has_debtors(
        pgsql, debt_id, _with_status(debt_before['debtors'], 'unpaid'),
    )


def _check_collect_debt_calls(stq, debt_id, now):
    assert stq.collect_debt.times_called == 2
    delay_call = stq.collect_debt.next_call()
    _check_collect_debt_params(
        delay_call, debt_id, now + dt.timedelta(seconds=5),
    )
    assert dateutil.parser.isoparse(
        delay_call['kwargs']['plan_in_advance_params']['planned_at'],
    ) == (now + dt.timedelta(seconds=5)).replace(tzinfo=dt.timezone.utc)

    stq_call = stq.collect_debt.next_call()
    _check_collect_debt_params(stq_call, debt_id, now)


def _check_collect_debt_params(stq_call, debt_id, eta):
    assert stq_call['id'] == debt_id
    assert stq_call['kwargs']['debt_id'] == debt_id
    assert stq_call['kwargs']['service'] == 'eats'
    assert stq_call['eta'] == eta


@pytest.mark.parametrize(
    'method, query',
    [
        ('update', make_query('unknown_debt_id', 1)),
        ('pay', make_pay_query('unknown_debt_id', 1)),
    ],
)
@pytest.mark.pgsql('eats_debt_collector', files=['eats_debt_collector.sql'])
async def test_debt_not_found(taxi_debt_collector, pgsql, method, query):
    response = await taxi_debt_collector.post(f'/v1/debt/{method}', query)
    debt_id = query['debt']['id']
    assert response.status_code == 404
    assert response.json()['code'] == '404'
    await _check_has_debt(taxi_debt_collector, None, debt_id)
    await _check_has_debtors(pgsql, debt_id, [])


async def _check_has_debt(taxi_debt_collector, expected, debt_id=None):
    actual = await _fetch_debt(taxi_debt_collector, debt_id or expected['id'])
    assert actual == expected


def _update(
        debt,
        version=None,
        payments=None,
        items_by_payment_type=None,
        transactions_params=None,
        collection=None,
):
    result = dict(debt)
    if version is not None:
        result['version'] = version
    if payments is not None:
        result['payments'] = payments
    if items_by_payment_type is not None:
        result['items_by_payment_type'] = items_by_payment_type
    if transactions_params is not None:
        result['transactions_params'] = transactions_params
    if collection is not None:
        result['collection'] = collection
    return result


async def _fetch_debt(taxi_debt_collector, debt_id):
    response = await taxi_debt_collector.post(
        '/v1/debts/by_id', {'ids': [debt_id], 'service': 'eats'},
    )
    debts = response.json()['debts']
    assert len(debts) <= 1
    if not debts:
        return None
    debt = debts[0]
    debt.pop('created_at')
    debt.pop('updated_at')
    return debt


async def _check_has_debtors(pgsql, debt_id, expected_debtors):
    cursor = pgsql['eats_debt_collector'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        'SELECT debtor, status FROM debt_collector.debts_debtors '
        'WHERE debt_id = %s',
        [debt_id],
    )
    actual = [(row['debtor'], row['status']) for row in cursor]
    assert sorted(actual) == sorted(expected_debtors)


def _get_headers(idempotency_token):
    headers = {}
    if idempotency_token is not None:
        headers['X-Idempotency-Token'] = idempotency_token
    return headers


def _merge_dicts(left, right):
    return {**left, **right}


def _with_status(debtors, status):
    return [(debtor, status) for debtor in debtors]
