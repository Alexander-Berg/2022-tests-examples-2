from typing import List, Optional  # noqa: IS001

import pytest

from tests_plugins import userver_client
import testsuite.utils.http as utils_http

import tests_order_takeout.mocks.order_archive as order_archive_mocks


def _get_find_order_id_by_uid(order_infos_by_uid):
    def _find_order_id_by_uid(request: utils_http.Request):
        yandex_uid = request.json['yandex_uid']
        order_infos = order_infos_by_uid.get(yandex_uid, [])
        return {'order_infos': order_infos}

    return _find_order_id_by_uid


@pytest.mark.parametrize(
    ['yandex_uid', 'orders', 'expected_status'],
    [
        pytest.param('yandex_uid_1', [], 'empty', id='no deletion, no orders'),
        pytest.param(
            'yandex_uid_1',
            [
                {
                    'id': 'order_id',
                    'request_due_or_created': '2022-03-01T00:00:00+00:00',
                },
            ],
            'ready_to_delete',
            id='no deletion, has orders',
        ),
        pytest.param(
            'yandex_uid_2',
            [],
            'delete_in_progress',
            id='active deletion, no orders',
        ),
        pytest.param(
            'yandex_uid_3', [], 'empty', id='deletion finished, no orders',
        ),
        pytest.param(
            'yandex_uid_3',
            [
                {
                    'id': 'order_id',
                    'request_due_or_created': '2022-03-01T00:00:00+00:00',
                },
            ],
            'ready_to_delete',
            id='deletion finished, has orders',
        ),
    ],
)
@pytest.mark.ydb(files=['init_deletion_requests.sql'])
async def test_ok(
        taxi_order_takeout: userver_client.ClientWrapper,
        mock_order_archive_service: order_archive_mocks.MockedServiceContext,
        mockserver,  # To fail if there are unmocked calls
        ydb,
        yandex_uid,
        orders,
        expected_status,
):
    status_request = {
        'request_id': 'sjjf38a8',
        'yandex_uids': [{'is_portal': True, 'uid': yandex_uid}],
        'date_request_at': '2020-01-01T00:00:00+00:00',
    }
    mock_order_archive_service.find_order_ids_by_uid.response_func = (
        _get_find_order_id_by_uid({yandex_uid: orders})
    )
    response = await taxi_order_takeout.post(
        '/v1/takeout/status', json=status_request,
    )
    assert response.status == 200
    response_json = response.json()
    assert response_json == {'data_state': expected_status}


def _calc_status(db_status: Optional[str], orders: List) -> str:
    if db_status is None or db_status == 'sent_to_anonymizer':
        if not orders:
            return 'empty'
        return 'ready_to_delete'
    return 'delete_in_progress'


SORTED_STATUSES = ['delete_in_progress', 'ready_to_delete', 'empty']


def _get_higher_status(statuses: List[str]) -> str:
    if 'delete_in_progress' in statuses:
        return 'delete_in_progress'
    if 'ready_to_delete' in statuses:
        return 'ready_to_delete'
    return 'empty'


def _insert_status_to_db(
        ydb, status: Optional[str], date_str: str, yandex_uid: str,
):
    if status is None:
        return
    sql_request = f"""
    --!syntax_v1
    INSERT INTO `deletion_requests`
        (yandex_uid, date_delete_until, status)
    VALUES
        (
            "{yandex_uid}",
            Timestamp("{date_str}"),
            "{status}"
        )
    ;
    """
    ydb.execute(sql_request)


@pytest.mark.parametrize(
    ['orders'],
    [
        ([],),
        (
            [
                {
                    'id': 'order_id',
                    'request_due_or_created': '2022-03-01T00:00:00+00:00',
                },
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    ['db_status_before_request'],
    [(None,), ('pending',), ('processing',), ('sent_to_anonymizer',)],
)
@pytest.mark.parametrize(
    ['db_status_after_request'],
    [(None,), ('pending',), ('processing',), ('sent_to_anonymizer',)],
)
async def test_1_uid_all_states(
        taxi_order_takeout: userver_client.ClientWrapper,
        mock_order_archive_service: order_archive_mocks.MockedServiceContext,
        mockserver,  # To fail if there are unmocked calls
        ydb,
        orders,
        db_status_before_request,
        db_status_after_request,
):
    yandex_uid_1 = 'yandex_uid_1'
    date_str_before_request = '2015-01-01T00:00:00Z'
    date_str_after_request = '2025-01-01T00:00:00Z'
    _insert_status_to_db(
        ydb, db_status_before_request, date_str_before_request, yandex_uid_1,
    )
    _insert_status_to_db(
        ydb, db_status_after_request, date_str_after_request, yandex_uid_1,
    )
    status_request = {
        'request_id': 'sjjf38a8',
        'yandex_uids': [{'is_portal': True, 'uid': yandex_uid_1}],
        'date_request_at': '2020-01-01T00:00:00+00:00',
    }
    mock_order_archive_service.find_order_ids_by_uid.response_func = (
        _get_find_order_id_by_uid({yandex_uid_1: orders})
    )
    response = await taxi_order_takeout.post(
        '/v1/takeout/status', json=status_request,
    )
    assert response.status == 200
    response_json = response.json()
    expected_status = _calc_status(db_status_before_request, orders)
    assert response_json == {'data_state': expected_status}


@pytest.mark.parametrize(
    ['orders_1'],
    [
        pytest.param([], id='no orders'),
        pytest.param(
            [
                {
                    'id': 'order_id',
                    'request_due_or_created': '2022-03-01T00:00:00+00:00',
                },
            ],
            id='has orders',
        ),
    ],
)
@pytest.mark.parametrize(
    ['db_status_1'],
    [(None,), ('pending',), ('processing',), ('sent_to_anonymizer',)],
)
@pytest.mark.parametrize(
    ['orders_2'],
    [
        pytest.param([], id='no orders'),
        pytest.param(
            [
                {
                    'id': 'order_id',
                    'request_due_or_created': '2022-03-01T00:00:00+00:00',
                },
            ],
            id='has orders',
        ),
    ],
)
@pytest.mark.parametrize(
    ['db_status_2'],
    [(None,), ('pending',), ('processing',), ('sent_to_anonymizer',)],
)
async def test_2_uids_all_states(
        taxi_order_takeout: userver_client.ClientWrapper,
        mock_order_archive_service: order_archive_mocks.MockedServiceContext,
        mockserver,  # To fail if there are unmocked calls
        ydb,
        orders_1,
        db_status_1,
        orders_2,
        db_status_2,
):
    yandex_uid_1 = 'yandex_uid_1'
    yandex_uid_2 = 'yandex_uid_2'
    date_str_before_request = '2015-01-01T00:00:00Z'
    _insert_status_to_db(
        ydb, db_status_1, date_str_before_request, yandex_uid_1,
    )
    _insert_status_to_db(
        ydb, db_status_2, date_str_before_request, yandex_uid_2,
    )
    status_request = {
        'request_id': 'sjjf38a8',
        'yandex_uids': [
            {'is_portal': True, 'uid': yandex_uid_1},
            {'is_portal': False, 'uid': yandex_uid_2},
        ],
        'date_request_at': '2020-01-01T00:00:00+00:00',
    }
    mock_order_archive_service.find_order_ids_by_uid.response_func = (
        _get_find_order_id_by_uid(
            {yandex_uid_1: orders_1, yandex_uid_2: orders_2},
        )
    )
    response = await taxi_order_takeout.post(
        '/v1/takeout/status', json=status_request,
    )
    assert response.status == 200
    response_json = response.json()
    expected_status_1 = _calc_status(db_status_1, orders_1)
    expected_status_2 = _calc_status(db_status_2, orders_2)
    expected_status = _get_higher_status(
        [expected_status_1, expected_status_2],
    )
    assert response_json == {'data_state': expected_status}
