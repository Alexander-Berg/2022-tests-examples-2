import pytest

EXPECTED_TAKEOUTS = [
    [1, 'id1', 'all', 'uid1', 'new'],
    [2, 'id1', 'all', 'uid2', 'new'],
]

EXPECTED_TASKS = [
    [1, 'process_incoming_request', False, 1, None],
    [2, 'process_incoming_request', False, 2, None],
]

REQUEST = {
    'request_id': 'id1',
    'yandex_uids': [
        {'uid': 'uid1', 'is_portal': False},
        {'uid': 'uid2', 'is_portal': False},
    ],
}


async def test_takeout_delete(taxi_eats_data_mappings, get_cursor):
    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/delete/all', json=REQUEST,
    )
    assert response.status_code == 200

    cursor = get_cursor()
    query = (
        'SELECT takeout_id, request_id, takeout_policy, '
        'yandex_uid, status FROM eats_data_mappings.takeout'
    )
    cursor.execute(query)
    takeouts = list(cursor)
    assert len(takeouts) == len(EXPECTED_TAKEOUTS)
    for takeout in EXPECTED_TAKEOUTS:
        assert takeout in takeouts

    query = (
        'SELECT id, task_type, done, takeout_id, '
        'mapping_id FROM eats_data_mappings.takeout_tasks'
    )
    cursor.execute(query)
    tasks = list(cursor)
    assert len(tasks) == len(EXPECTED_TASKS)
    for task in EXPECTED_TASKS:
        assert task in tasks


async def test_takeout_status_data_state(
        taxi_eats_data_mappings, get_cursor, update_status,
):
    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/status/all', json=REQUEST,
    )
    assert response.status_code == 200
    assert response.json()['data_state'] == 'ready_to_delete'

    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/delete/all', json=REQUEST,
    )
    assert response.status_code == 200

    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/status/all', json=REQUEST,
    )
    assert response.status_code == 200
    assert response.json()['data_state'] == 'delete_in_progress'

    update_status(
        [REQUEST['yandex_uids'][0]['uid']],
        [REQUEST['request_id']],
        'finished',
    )

    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/status/all', json=REQUEST,
    )
    assert response.status_code == 200
    assert response.json()['data_state'] == 'delete_in_progress'

    update_status(
        [REQUEST['yandex_uids'][1]['uid']],
        [REQUEST['request_id']],
        'finished',
    )

    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/status/all', json=REQUEST,
    )
    assert response.status_code == 200
    assert response.json()['data_state'] == 'empty'


REQUEST2 = {
    'request_id': 'id2',
    'yandex_uids': [
        {'uid': 'uid1', 'is_portal': False},
        {'uid': 'uid2', 'is_portal': False},
    ],
}

STATUS_REQUEST_1 = {'yandex_uids': [{'uid': 'uid1', 'is_portal': False}]}
STATUS_REQUEST_2 = {
    'yandex_uids': [
        {'uid': 'uid1', 'is_portal': False},
        {'uid': 'uid2', 'is_portal': False},
    ],
}
STATUS_REQUEST_3 = {
    'request_id': 'id1',
    'yandex_uids': [{'uid': 'uid1', 'is_portal': False}],
}


async def test_takeout_status_request_id(
        taxi_eats_data_mappings, update_status,
):
    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/delete/all', json=REQUEST,
    )
    assert response.status_code == 200

    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/delete/all', json=REQUEST2,
    )
    assert response.status_code == 200

    update_status(
        [REQUEST['yandex_uids'][0]['uid']],
        [REQUEST['request_id']],
        'finished',
    )

    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/status/all', json=STATUS_REQUEST_1,
    )
    assert response.status_code == 200
    assert response.json()['data_state'] == 'delete_in_progress'

    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/status/all', json=STATUS_REQUEST_2,
    )
    assert response.status_code == 200
    assert response.json()['data_state'] == 'delete_in_progress'

    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/status/all', json=STATUS_REQUEST_3,
    )
    assert response.status_code == 200
    assert response.json()['data_state'] == 'empty'


async def test_takeout_status_policy(taxi_eats_data_mappings):
    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/delete/all', json=REQUEST,
    )
    assert response.status_code == 200

    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/status/all', json=REQUEST,
    )
    assert response.status_code == 200
    assert response.json()['data_state'] == 'delete_in_progress'

    response = await taxi_eats_data_mappings.post(
        '/takeout/v1/status/something_else', json=REQUEST,
    )
    assert response.status_code == 200
    assert response.json()['data_state'] == 'ready_to_delete'
