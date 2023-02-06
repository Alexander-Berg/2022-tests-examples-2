import datetime
from typing import Any, Dict  # noqa: IS001

import bson
import pytest

import testsuite._internal.fixture_types as fixture_types
import testsuite.plugins.mocked_time as mocked_time_plugin
import testsuite.utils.callinfo as callinfo

import tests_invoices_archive.mocks.invoices_archive as invoices_archive

TASK_ID = 'testsuite_task_id_1'

VIRGIN_ORDER: Dict[str, Any] = {
    '_id': 'virgin_order',
    'processing': {'version': 8},
    'order': {
        'version': 16,
        'creditcard': {'credentials': {'card_number': '400000****3692'}},
        'billing_tech': {
            'transactions': [
                {'billing_response': {'key_1': 'value_1'}},
                {'billing_response': {'key_2': 'value_2'}},
            ],
        },
    },
    'yandex_uid': '4086105037',
}
PREPARED_ORDER: Dict[str, Any] = {
    'takeout': {
        'status': 'prepared',
        'version': 1,
        'date_delete_request': (
            datetime.datetime.fromisoformat(
                '2018-01-28T12:08:48.372+00:00',
            ).replace(tzinfo=None)
        ),
        'events': [
            {
                'status': 'prepared',
                'date': datetime.datetime.fromisoformat(
                    '2019-01-28T12:08:48.372+00:00',
                ).replace(tzinfo=None),
            },
        ],
    },
    **VIRGIN_ORDER,
}


@pytest.mark.parametrize(
    ['orders_doc', 'expected_takeout_obj'],
    [
        pytest.param(
            VIRGIN_ORDER,
            {
                'status': 'prepared',
                'version': 1,
                'date_delete_request': (
                    datetime.datetime.fromisoformat(
                        '2018-01-28T12:08:48.372+00:00',
                    ).replace(tzinfo=None)
                ),
                'events': [
                    {
                        'status': 'prepared',
                        'date': datetime.datetime.fromisoformat(
                            '2019-01-28T12:08:48.372+00:00',
                        ).replace(tzinfo=None),
                    },
                ],
            },
            marks=pytest.mark.filldb(orders='virgin'),
            id='prepare',
        ),
        pytest.param(
            PREPARED_ORDER,
            {
                'status': 'anonymized',
                'version': 2,
                'date_delete_request': (
                    datetime.datetime.fromisoformat(
                        '2018-01-28T12:08:48.372+00:00',
                    ).replace(tzinfo=None)
                ),
                'events': [
                    {
                        'status': 'prepared',
                        'date': datetime.datetime.fromisoformat(
                            '2019-01-28T12:08:48.372+00:00',
                        ).replace(tzinfo=None),
                    },
                    {
                        'status': 'anonymized',
                        'date': datetime.datetime.fromisoformat(
                            '2019-01-28T12:08:48.372+00:00',
                        ).replace(tzinfo=None),
                    },
                ],
            },
            marks=pytest.mark.filldb(orders='virgin_prepared'),
            id='anonymize',
        ),
    ],
)
@pytest.mark.filldb()
async def test_mongo_state_before_after(
        stq_runner,
        mock_invoices_archive_service: invoices_archive.MockedServiceContext,
        mockserver: fixture_types.MockserverFixture,
        mocked_time: mocked_time_plugin.MockedTime,
        mongodb,
        orders_doc,
        expected_takeout_obj,
):
    date_delete_until = '2018-01-28T12:08:48.372+00:00'
    mocked_time.set(
        datetime.datetime.fromisoformat(date_delete_until)
        + datetime.timedelta(
            days=365,
        ),  # delta must be greater than anonymize delay in config
    )
    invoices_archive_get_order = (
        mock_invoices_archive_service.invoices_archive_get_order
    )
    invoices_archive_get_order.response = orders_doc

    await stq_runner.invoices_archive_anonymize_order.call(
        task_id=TASK_ID,
        kwargs={
            'anonymize_order_request': {
                'order_id': 'testsuite_order_id_1',
                'request_due_or_created': '2018-01-28T12:08:48.372+00:00',
                'date_delete_until': date_delete_until,
            },
        },
    )
    assert invoices_archive_get_order.handler.times_called == 1

    order = mongodb.orders.find_one({'_id': 'virgin_order'})
    assert order['takeout'] == expected_takeout_obj


@pytest.mark.parametrize(
    [
        'orders_doc',
        'now',
        'reschedule_eta',
        'expected_takeout_obj',
        'order_not_found',
    ],
    [
        pytest.param(
            VIRGIN_ORDER,
            datetime.datetime.fromisoformat('2020-01-11T01:00:00.000+00:00'),
            datetime.datetime.fromisoformat('2020-02-01T00:00:00.000+00:00'),
            {
                'status': 'prepared',
                'version': 1,
                'date_delete_request': (
                    datetime.datetime.fromisoformat(
                        '2020-01-01T00:00:00.000+00:00',
                    ).replace(tzinfo=None)
                ),
                'events': [
                    {
                        'status': 'prepared',
                        'date': datetime.datetime.fromisoformat(
                            '2020-01-11T01:00:00.000+00:00',
                        ).replace(tzinfo=None),
                    },
                ],
            },
            False,
            marks=pytest.mark.filldb(orders='virgin'),
            id='prepare',
        ),
        pytest.param(
            PREPARED_ORDER,
            datetime.datetime.fromisoformat('2020-01-11T02:00:00.000+00:00'),
            datetime.datetime.fromisoformat('2020-02-01T00:00:00.000+00:00'),
            {'status': 'prepared', 'version': 1},
            False,
            marks=pytest.mark.filldb(orders='virgin_prepared'),
            id='dont_anonymize_before_due',
        ),
        pytest.param(
            PREPARED_ORDER,
            datetime.datetime.fromisoformat('2020-02-01T01:00:00.000+00:00'),
            None,
            {
                'status': 'anonymized',
                'version': 2,
                'date_delete_request': (
                    datetime.datetime.fromisoformat(
                        '2018-01-28T12:08:48.372+00:00',
                    ).replace(tzinfo=None)
                ),
                'events': [
                    {
                        'status': 'prepared',
                        'date': datetime.datetime.fromisoformat(
                            '2019-01-28T12:08:48.372+00:00',
                        ).replace(tzinfo=None),
                    },
                    {
                        'status': 'anonymized',
                        'date': datetime.datetime.fromisoformat(
                            '2020-02-01T01:00:00.000+00:00',
                        ).replace(tzinfo=None),
                    },
                ],
            },
            False,
            marks=pytest.mark.filldb(orders='virgin_prepared'),
            id='anonymize_after_due',
        ),
        pytest.param(
            {'code': 'no_such_order', 'message': 'Order not found'},
            datetime.datetime.fromisoformat('2020-02-01T01:00:00.000+00:00'),
            None,
            None,
            True,
            marks=pytest.mark.filldb(orders='virgin'),
            id='order_not_found',
        ),
    ],
)
async def test_state_machine(
        stq,
        stq_runner,
        mock_invoices_archive_service: invoices_archive.MockedServiceContext,
        mockserver: fixture_types.MockserverFixture,
        mocked_time: mocked_time_plugin.MockedTime,
        mongodb,
        orders_doc,
        now,
        reschedule_eta: datetime.datetime,
        expected_takeout_obj,
        order_not_found,
):
    mocked_time.set(now)
    mock_invoices_archive_service.invoices_archive_get_order.response = (
        orders_doc
    )
    if order_not_found:
        mock_invoices_archive_service.invoices_archive_get_order.status = 404

    await stq_runner.invoices_archive_anonymize_order.call(
        task_id=TASK_ID,
        kwargs={
            'anonymize_order_request': {
                'order_id': 'testsuite_order_id_1',
                'request_due_or_created': '2020-01-01T00:00:00.00+00:00',
                'date_delete_until': '2020-11-01T00:00:00.00+00:00',
            },
        },
    )
    stq_worker: callinfo.AsyncCallQueue = stq.invoices_archive_anonymize_order
    if reschedule_eta is not None:
        assert stq_worker.times_called == 1
        task = stq_worker.next_call()
        assert task['kwargs'] is None  # expect no kwargs on rescheduling
        assert task['id'] == TASK_ID  # expect same task_id
        assert task['eta'] == reschedule_eta.replace(tzinfo=None)
    else:
        assert stq_worker.times_called == 0

    order = mongodb.orders.find_one({'_id': 'virgin_order'})
    assert order.get('takeout') == expected_takeout_obj


@pytest.mark.parametrize(
    ['expect_update_mongo_error', 'order_in_mongo', 'order_in_archive'],
    [
        pytest.param(
            False,
            True,  # must have marks=pytest.mark.filldb(orders='prepared')
            False,
            marks=pytest.mark.filldb(orders='prepared'),
            id='normal_flow',
        ),
        pytest.param(False, False, True, id='not_in_mongo_but_in_archive'),
        pytest.param(
            True, False, False, id='mongo_not_found_or_race_condition',
        ),
    ],
)
async def test_anonymize_fields_ydb(
        stq_runner,
        mock_invoices_archive_service: invoices_archive.MockedServiceContext,
        mock_archive_api,
        mockserver: fixture_types.MockserverFixture,
        ydb,
        load_json,
        mocked_time: mocked_time_plugin.MockedTime,
        expect_update_mongo_error,
        order_in_mongo,
        order_in_archive,
):
    doc = load_json('db_orders_prepared.json')[0]
    mock_invoices_archive_service.invoices_archive_get_order.response = doc
    if order_in_archive:
        mock_archive_api.set_order(doc)

    order_id = doc['_id']
    date_delete_until = '2022-03-01T15:12:38.000+00:00'
    mocked_time.set(
        datetime.datetime.fromisoformat(date_delete_until)
        + datetime.timedelta(days=10),
    )

    sql_request = f"""
    --!syntax_v1
    SELECT COUNT(*) AS count
    FROM `orders_fields`
    WHERE order_id="{order_id}"
    """
    # validate YDB state
    cursor = ydb.execute(sql_request)
    assert len(cursor) == 1
    assert cursor[0].rows[0]['count'] == 0

    await stq_runner.invoices_archive_anonymize_order.call(
        task_id=TASK_ID,
        kwargs={
            'anonymize_order_request': {
                'order_id': 'testsuite_order_id_1',
                'request_due_or_created': '2022-02-07T15:12:38Z',
                'date_delete_until': date_delete_until,
            },
        },
        expect_fail=expect_update_mongo_error,
    )
    if not order_in_mongo:
        assert mock_archive_api.mock_restore.times_called == 1

    # validate YDB state
    cursor = ydb.execute(
        f"""
    --!syntax_v1
    SELECT
        json_path,
        original_value,
        anonymized_value
    FROM `orders_fields`
    WHERE order_id="{order_id}"
    ORDER BY json_path
    """,
    )
    assert len(cursor) == 1

    def decode_stored_bson(bson_str):
        return bson.BSON.decode(bson_str)['data']

    rows = [
        {
            'json_path': row['json_path'].decode('utf-8'),
            'original_value': decode_stored_bson(row['original_value']),
            'anonymized_value': decode_stored_bson(row['anonymized_value']),
        }
        for row in cursor[0].rows
    ]
    expected_rows = load_json('ydb_state.json')
    assert rows == expected_rows

    sql_commited_request = f"""
    --!syntax_v1
    SELECT committed
    FROM `orders_fields`
    WHERE order_id="{order_id}"
    """
    cursor = ydb.execute(sql_commited_request)
    assert len(cursor) == 1
    for row in cursor[0].rows:
        assert row.committed != expect_update_mongo_error


@pytest.mark.ydb(files=['init_orders_fields.sql'])
async def test_commit_fields_ydb(
        stq_runner,
        mock_invoices_archive_service: invoices_archive.MockedServiceContext,
        mockserver: fixture_types.MockserverFixture,
        ydb,
        load_json,
):
    doc = load_json('db_orders_anonymized.json')[0]
    mock_invoices_archive_service.invoices_archive_get_order.response = doc

    sql_request = f"""
    --!syntax_v1
    SELECT * FROM `orders_fields`
    WHERE order_id="{doc['_id']}"
    """
    # validate YDB state
    cursor = ydb.execute(sql_request)
    assert len(cursor) == 1
    assert not cursor[0].rows[0]['committed']

    await stq_runner.invoices_archive_anonymize_order.call(
        task_id=TASK_ID,
        kwargs={
            'anonymize_order_request': {
                'order_id': 'testsuite_order_id_1',
                'request_due_or_created': '2022-02-07T15:12:38Z',
                'date_delete_until': '2022-03-01T15:12:38.000+00:00',
            },
        },
    )
    # validate YDB state
    cursor = ydb.execute(sql_request)
    assert len(cursor) == 1
    assert cursor[0].rows[0]['committed']


@pytest.fixture(name='mock_archive_api')
def _mock_archive_api(mockserver, mongodb):
    cache = {}

    @mockserver.json_handler('/archive-api/archive/orders/restore')
    async def _restore(request):
        order_id = request.json['id']
        order = cache.get(order_id)
        if order is not None:
            query = {'_id': order_id, '_shard_id': order['_shard_id']}
            order['updated'] = datetime.datetime.utcnow()
            mongodb.orders.replace_one(query, order, upsert=True)
            return [{'id': order_id, 'status': 'restored'}]
        return [{'id': order_id, 'status': 'not_found'}]

    class Mock:
        @classmethod
        def set_order(cls, order):
            cache[order['_id']] = order

        mock_restore = _restore

    return Mock()


# TODO Add tests for ttl of corporate orders
