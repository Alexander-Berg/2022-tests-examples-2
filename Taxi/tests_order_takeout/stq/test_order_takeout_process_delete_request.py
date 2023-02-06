import datetime

import pytest

import testsuite._internal.fixture_types as fixture_types
import testsuite.utils.callinfo as callinfo
import testsuite.utils.http as utils_http

import tests_order_takeout.mocks.order_archive as order_archive_mocks


YANDEX_UID = 'yandex_uid_1'
ORDER_INFOS = [
    {
        'id': 'order_id_1',
        'request_due_or_created': '2014-03-18T04:30:00+00:00',
    },
    {
        'id': 'order_id_2',
        'request_due_or_created': '2022-01-24T04:30:00+00:00',
    },
]


def _find_order_id_by_uid(request: utils_http.Request):
    order_infos = [
        info
        for info in ORDER_INFOS
        if YANDEX_UID == request.json['yandex_uid']
    ]
    date_lower_bound_str = request.json.get('date_lower_bound')
    if date_lower_bound_str is not None:
        date_lower_bound = datetime.datetime.fromisoformat(
            date_lower_bound_str,
        )
        order_infos = [
            info
            for info in ORDER_INFOS
            if datetime.datetime.fromisoformat(info['request_due_or_created'])
            >= date_lower_bound
        ]
    return {'order_infos': order_infos}


@pytest.mark.parametrize(
    [
        'expected_order_ids',
        'expected_find_order_by_uid_calls',
        'expected_statuses',
        'date_delete_since',
    ],
    [
        pytest.param(
            ['order_id_1', 'order_id_2'],
            1,
            ['sent_to_anonymizer'],
            '2012-03-01T18:22:03Z',
            marks=(pytest.mark.ydb(files=['init_stq_1.sql']),),
            id='expect 2 orders',
        ),
        pytest.param(
            ['order_id_1', 'order_id_2'],
            1,
            ['sent_to_anonymizer'],
            None,
            marks=(pytest.mark.ydb(files=['init_stq_2.sql']),),
            id='1 stq failed, expect 2 orders',
        ),
        pytest.param(
            ['order_id_2'],
            1,
            ['sent_to_anonymizer'],
            '2015-03-01T18:22:03Z',
            marks=(pytest.mark.ydb(files=['init_stq_3.sql']),),
            id='had deletion before, expect 1 order to delete',
        ),
        pytest.param(
            [],
            0,
            [],
            None,
            marks=(pytest.mark.ydb(files=['init_stq_4.sql']),),
            id='deletion record not found in deletion_requests',
        ),
        pytest.param(
            [],
            1,
            ['sent_to_anonymizer'],
            '2022-01-25T09:08:47Z',
            marks=(pytest.mark.ydb(files=['init_stq_5.sql']),),
            id='current deletion is active, but expect 0 orders to delete',
        ),
    ],
)
async def test_ok(
        stq_runner,
        stq,
        mock_order_archive_service: order_archive_mocks.MockedServiceContext,
        mockserver: fixture_types.MockserverFixture,
        ydb,
        expected_order_ids,
        expected_find_order_by_uid_calls,
        expected_statuses,
        date_delete_since,
):
    yandex_uid = YANDEX_UID
    date_delete_until = '2022-01-28T09:08:48+00:00'
    mock_order_archive_service.find_order_ids_by_uid.response_func = (
        _find_order_id_by_uid
    )

    await stq_runner.order_takeout_process_delete_request.call(
        task_id='task_id_1',
        kwargs={
            'delete_request': {
                'yandex_uid': yandex_uid,
                'date_delete_until': date_delete_until,
                'date_delete_since': date_delete_since,
            },
        },
    )
    assert (
        mock_order_archive_service.find_order_ids_by_uid.handler.times_called
        == expected_find_order_by_uid_calls
    )
    stq_worker: callinfo.AsyncCallQueue = stq.order_takeout_anonymize_order
    assert stq_worker.times_called == len(expected_order_ids)
    task_list = [
        stq_worker.next_call() for _ in range(stq_worker.times_called)
    ]
    order_ids = [
        task['kwargs']['anonymize_order_request']['order_id']
        for task in task_list
    ]
    assert order_ids == expected_order_ids
    # validate YDB state
    sql_request = f"""
    --!syntax_v1
    SELECT status
    FROM `deletion_requests`
    WHERE yandex_uid = "yandex_uid_1"
        AND
        date_delete_until = Timestamp("2022-01-28T09:08:48Z")
    """
    cursor = ydb.execute(sql_request)
    assert len(cursor) == 1
    statuses = sorted(row.status.decode('utf-8') for row in cursor[0].rows)
    assert statuses == expected_statuses
