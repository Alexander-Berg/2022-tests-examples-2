import pytest

import testsuite.utils.callinfo as callinfo

DEFAULT_TAKEOUT_YANDEX_UIDS = [
    {'is_portal': True, 'uid': 'yandex_uid_1'},
    {'is_portal': False, 'uid': 'yandex_uid_2'},
    {'is_portal': False, 'uid': 'yandex_uid_3'},
    {'is_portal': False, 'uid': 'yandex_uid_4'},
    {'is_portal': False, 'uid': 'yandex_uid_5'},
]

DATE_DELETE_UNTIL = '2020-01-01T00:00:00+00:00'
DEFAULT_JSON_REQUEST = {
    'request_id': 'sjjf38a8',
    'yandex_uids': DEFAULT_TAKEOUT_YANDEX_UIDS,
    'date_delete_until': '2020-01-01T00:00:00+00:00',
}


@pytest.mark.ydb(files=['init_deletion_requests.sql'])
async def test_ok(
        taxi_order_takeout,
        stq,
        mockserver,  # To fail if there are unmocked calls
        ydb,
):
    response = await taxi_order_takeout.post(
        '/v1/takeout/delete', json=DEFAULT_JSON_REQUEST,
    )
    assert response.status == 200

    stq_worker: callinfo.AsyncCallQueue = (
        stq.order_takeout_process_delete_request
    )
    assert stq_worker.times_called == 3
    task_list = [
        stq_worker.next_call() for _ in range(stq_worker.times_called)
    ]
    task_dict = {
        task['id']: task['kwargs']['delete_request'] for task in task_list
    }
    assert task_dict == {
        'sjjf38a8_yandex_uid_1_2020-01-01T00:00:00+00:00': {
            'date_delete_since': '2010-01-01T00:00:00+00:00',
            'date_delete_until': '2020-01-01T00:00:00+00:00',
            'yandex_uid': 'yandex_uid_1',
        },
        'sjjf38a8_yandex_uid_4_2020-01-01T00:00:00+00:00': {
            'date_delete_until': '2020-01-01T00:00:00+00:00',
            'yandex_uid': 'yandex_uid_4',
        },
        'sjjf38a8_yandex_uid_5_2020-01-01T00:00:00+00:00': {
            'date_delete_until': '2020-01-01T00:00:00+00:00',
            'yandex_uid': 'yandex_uid_5',
        },
    }
    # validate YDB state
    sql_request = f"""
    --!syntax_v1
    SELECT
        yandex_uid, date_delete_since, date_delete_until, status
    FROM `deletion_requests`
    WHERE
        date_delete_until = Datetime("2020-01-01T00:00:00Z")
        AND
        status = "pending"
    """
    cursor = ydb.execute(sql_request)
    assert len(cursor) == 1
    rows = [
        {
            'yandex_uid': row['yandex_uid'].decode('utf-8'),
            'status': row['status'].decode('utf-8'),
            'date_delete_since': row['date_delete_since'],
            'date_delete_until': row['date_delete_until'],
        }
        for row in cursor[0].rows
    ]
    assert rows == [
        {
            'date_delete_since': 1262304000000000,
            'date_delete_until': 1577836800000000,
            'status': 'pending',
            'yandex_uid': 'yandex_uid_1',
        },
        {
            'date_delete_since': None,
            'date_delete_until': 1577836800000000,
            'status': 'pending',
            'yandex_uid': 'yandex_uid_4',
        },
        {
            'date_delete_since': None,
            'date_delete_until': 1577836800000000,
            'status': 'pending',
            'yandex_uid': 'yandex_uid_5',
        },
    ]
