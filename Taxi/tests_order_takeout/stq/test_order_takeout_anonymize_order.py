import datetime
from typing import Any, Dict  # noqa: IS001

import bson
import pytest

import testsuite._internal.fixture_types as fixture_types
import testsuite.plugins.mocked_time as mocked_time_plugin
import testsuite.utils.callinfo as callinfo

import tests_order_takeout.mocks.order_core as order_core_mocks

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
                    '2018-01-28T12:08:48.372+00:00',
                ).replace(tzinfo=None),
            },
        ],
    },
    **VIRGIN_ORDER,
}


@pytest.mark.parametrize(
    ['order_proc_doc', 'expected_set_fields_request'],
    [
        pytest.param(
            VIRGIN_ORDER,
            {
                'revision': {'order.version': 16, 'processing.version': 8},
                'update': {
                    '$set': {
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
                    },
                },
                'takeout.version': {'$exists': False},
            },
            id='prepare',
        ),
        pytest.param(
            PREPARED_ORDER,
            {
                'revision': {'order.version': 16, 'processing.version': 8},
                'update': {
                    '$set': {
                        'order.billing_tech.transactions.0.billing_response': {},  # noqa: E501
                        'order.billing_tech.transactions.1.billing_response': {},  # noqa: E501
                        'order.creditcard.credentials.card_number': '',
                        'takeout': {
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
                                        '2018-01-28T12:08:48.372+00:00',
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
                    },
                },
                'takeout.version': 1,
            },
            id='anonymize',
        ),
    ],
)
async def test_set_fields_request(
        stq_runner,
        mock_order_core_service: order_core_mocks.MockedServiceContext,
        mockserver: fixture_types.MockserverFixture,
        mocked_time: mocked_time_plugin.MockedTime,
        order_proc_doc,
        expected_set_fields_request,
):
    date_delete_until = '2018-01-28T12:08:48.372+00:00'
    request_due_or_created = '2018-01-28T12:08:48.372+00:00'
    mocked_time.set(
        datetime.datetime.fromisoformat(date_delete_until)
        + datetime.timedelta(
            days=365,
        ),  # delta must be greater than anonymize delay in config
    )
    mock_order_core_service.order_proc_get_order.response = order_proc_doc

    await stq_runner.order_takeout_anonymize_order.call(
        task_id=TASK_ID,
        kwargs={
            'anonymize_order_request': {
                'order_id': 'testsuite_order_id_1',
                'request_due_or_created': request_due_or_created,
                'date_delete_until': date_delete_until,
            },
        },
    )
    assert (
        mock_order_core_service.order_proc_get_order.handler.times_called == 1
    )
    assert (
        mock_order_core_service.order_proc_set_fields.handler.times_called == 1
    )
    set_fields_request = (
        mock_order_core_service.order_proc_set_fields.handler.next_call()[
            'request'
        ]
    )
    data_json = bson.BSON.decode(set_fields_request.get_data())
    assert data_json == expected_set_fields_request


@pytest.mark.parametrize(
    [
        'order_proc_doc',
        'now',
        'reschedule_eta',
        'times_set_fields_called',
        'order_not_found',
    ],
    [
        pytest.param(
            VIRGIN_ORDER,
            datetime.datetime.fromisoformat('2020-01-11T01:00:00.000+00:00'),
            datetime.datetime.fromisoformat('2020-02-01T00:00:00.000+00:00'),
            1,
            False,
            id='prepare',
        ),
        pytest.param(
            PREPARED_ORDER,
            datetime.datetime.fromisoformat('2020-01-11T02:00:00.000+00:00'),
            datetime.datetime.fromisoformat('2020-02-01T00:00:00.000+00:00'),
            0,
            False,
            id='dont_anonymize_before_due',
        ),
        pytest.param(
            PREPARED_ORDER,
            datetime.datetime.fromisoformat('2020-02-01T01:00:00.000+00:00'),
            None,
            1,
            False,
            id='anonymize_after_due',
        ),
        pytest.param(
            {'code': 'no_such_order', 'message': 'Order not found'},
            datetime.datetime.fromisoformat('2020-02-01T01:00:00.000+00:00'),
            None,
            0,
            True,
            id='order_not_found',
        ),
    ],
)
async def test_state_machine(
        stq,
        stq_runner,
        mock_order_core_service: order_core_mocks.MockedServiceContext,
        mockserver: fixture_types.MockserverFixture,
        mocked_time: mocked_time_plugin.MockedTime,
        order_proc_doc,
        now,
        reschedule_eta: datetime.datetime,
        times_set_fields_called: int,
        order_not_found: bool,
):
    request_due_or_created = '2020-01-01T00:00:00.00+00:00'
    date_delete_until = '2020-11-01T00:00:00.00+00:00'
    mocked_time.set(now)

    mock_order_core_service.order_proc_get_order.response = order_proc_doc
    if order_not_found:
        mock_order_core_service.order_proc_get_order.status = 404

    await stq_runner.order_takeout_anonymize_order.call(
        task_id=TASK_ID,
        kwargs={
            'anonymize_order_request': {
                'order_id': 'testsuite_order_id_1',
                'request_due_or_created': request_due_or_created,
                'date_delete_until': date_delete_until,
            },
        },
    )
    stq_worker: callinfo.AsyncCallQueue = stq.order_takeout_anonymize_order
    if reschedule_eta is not None:
        assert stq_worker.times_called == 1
        task = stq_worker.next_call()
        assert task['kwargs'] is None  # expect no kwargs on rescheduling
        assert task['id'] == TASK_ID  # expect same task_id
        assert task['eta'] == reschedule_eta.replace(tzinfo=None)
    else:
        assert stq_worker.times_called == 0

    mock_set_fields = mock_order_core_service.order_proc_set_fields
    assert mock_set_fields.handler.times_called == times_set_fields_called


@pytest.mark.parametrize(
    ['expect_set_fields_error', 'set_fields_status_code'],
    [
        pytest.param(False, 200, id='normal_flow'),
        pytest.param(True, 500, id='set_fields_error'),
    ],
)
async def test_anonymize_fields_ydb(
        stq_runner,
        mock_order_core_service: order_core_mocks.MockedServiceContext,
        mockserver: fixture_types.MockserverFixture,
        ydb,
        load_json,
        mocked_time: mocked_time_plugin.MockedTime,
        expect_set_fields_error,
        set_fields_status_code,
):

    doc = load_json('order_proc_prepared.json')
    mock_order_core_service.order_proc_get_order.response = doc
    order_id = doc['_id']
    request_due_or_created = doc['order']['request']['due']
    date_delete_until = '2022-03-01T15:12:38.000+00:00'
    mocked_time.set(
        datetime.datetime.fromisoformat(date_delete_until)
        + datetime.timedelta(days=10),
    )

    sql_request = f"""
    --!syntax_v1
    SELECT
        order_id,
        json_path,
        original_value,
        anonymized_value,
        request_due,
        expires_at
    FROM `order_proc_fields`
    WHERE order_id="{order_id}"
    ORDER BY json_path
    """
    # validate YDB state
    cursor = ydb.execute(sql_request)
    assert len(cursor) == 1
    assert not cursor[0].rows

    mock_set_fields = mock_order_core_service.order_proc_set_fields
    mock_set_fields.status = set_fields_status_code

    await stq_runner.order_takeout_anonymize_order.call(
        task_id=TASK_ID,
        kwargs={
            'anonymize_order_request': {
                'order_id': 'testsuite_order_id_1',
                'request_due_or_created': request_due_or_created,
                'date_delete_until': date_delete_until,
            },
        },
        expect_fail=expect_set_fields_error,
    )
    assert mock_set_fields.handler.times_called == 1

    # validate YDB state
    cursor = ydb.execute(sql_request)
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
    FROM `order_proc_fields`
    WHERE order_id="{order_id}"
    """
    cursor = ydb.execute(sql_commited_request)
    assert len(cursor) == 1
    for row in cursor[0].rows:
        assert row.committed != expect_set_fields_error


@pytest.mark.ydb(files=['init_order_proc_fields.sql'])
async def test_commit_fields_ydb(
        stq_runner,
        mock_order_core_service: order_core_mocks.MockedServiceContext,
        mockserver: fixture_types.MockserverFixture,
        ydb,
        load_json,
):
    doc = load_json('order_proc_anonymized.json')
    mock_order_core_service.order_proc_get_order.response = doc

    sql_request = f"""
    --!syntax_v1
    SELECT * FROM `order_proc_fields`
    WHERE order_id="{doc['_id']}"
    """
    # validate YDB state
    cursor = ydb.execute(sql_request)
    assert len(cursor) == 1
    assert not cursor[0].rows[0]['committed']

    await stq_runner.order_takeout_anonymize_order.call(
        task_id=TASK_ID,
        kwargs={
            'anonymize_order_request': {
                'order_id': 'testsuite_order_id_1',
                'request_due_or_created': doc['order']['request']['due'],
                'date_delete_until': '2022-03-01T15:12:38.000+00:00',
            },
        },
    )
    # validate YDB state
    cursor = ydb.execute(sql_request)
    assert len(cursor) == 1
    assert cursor[0].rows[0]['committed']


# TODO Add tests for ttl of corporate orders
