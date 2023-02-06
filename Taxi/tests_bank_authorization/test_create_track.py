import pytest

from tests_bank_authorization import common

OPERATION_TYPES = {
    'faster_payments_default_bank': 'faster_payments_default_bank',
    'confirm_transfer_me2me': 'confirm_transfer_me2me',
    'confirm_transfer_c2c': 'confirm_transfer_c2c',
    'confirm_transfer_inner': 'confirm_transfer_inner',
}


def select_track(pgsql, track_id):
    cursor = pgsql['bank_authorization'].cursor()
    cursor.execute(
        (
            'SELECT idempotency_token, buid,'
            'operation_type, antifraud_context_id '
            'FROM bank_authorization.tracks '
            f'WHERE id = \'{track_id}\'::UUID'
        ),
    )
    result = cursor.fetchall()
    assert len(result) == 1
    return result[0]


def insert_track(pgsql, idempotency_token, buid, operation_type):
    cursor = pgsql['bank_authorization'].cursor()
    cursor.execute(
        'INSERT INTO bank_authorization.tracks'
        '(idempotency_token, buid, operation_type) '
        f'VALUES(\'{idempotency_token}\', \'{buid}\', \'{operation_type}\') '
        'RETURNING id;',
    )
    return cursor.fetchone()[0]


async def test_simple(taxi_bank_authorization, pgsql):
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/create_track',
        headers={'X-Idempotency-Token': 'idempotency-key'},
        json={'buid': 'buid1', 'operation_type': 'operation'},
    )

    assert response.status_code == 200
    track_id = response.json()['track_id']

    track = select_track(pgsql, track_id)
    assert track[0] == 'idempotency-key'
    assert track[1] == 'buid1'
    assert track[2] == 'operation'


@pytest.mark.config(BANK_AUTHORIZATION_OPERATIONS_TYPES=OPERATION_TYPES)
async def test_fps(taxi_bank_authorization, pgsql, mockserver):
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/create_track',
        headers={'X-Idempotency-Token': 'idempotency-key'},
        json={
            'buid': common.FPS_BANK_UID,
            'operation_type': OPERATION_TYPES['faster_payments_default_bank'],
        },
    )

    assert response.status_code == 200
    track_id = response.json()['track_id']

    track = select_track(pgsql, track_id)
    assert track[0] == 'idempotency-key'
    assert track[1] == common.FPS_BANK_UID
    assert track[2] == OPERATION_TYPES['faster_payments_default_bank']


async def test_race(taxi_bank_authorization, pgsql, testpoint, mockserver):
    track_id = None
    token = 'idempotency-key'
    buid = 'buid1'
    operation_type = 'operation'

    @testpoint('create_other_track')
    async def _create_other_track(data):
        nonlocal track_id
        track_id = insert_track(pgsql, token, buid, operation_type)

    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/create_track',
        headers={'X-Idempotency-Token': token},
        json={'buid': buid, 'operation_type': operation_type},
    )

    assert response.status_code == 500

    track = select_track(pgsql, track_id)
    assert track[0] == 'idempotency-key'
    assert track[1] == 'buid1'
    assert track[2] == 'operation'


async def test_409(taxi_bank_authorization, pgsql):
    token = 'idempotency-key'
    insert_track(pgsql, token, 'buid2', 'operation')

    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/create_track',
        headers={'X-Idempotency-Token': token},
        json={'buid': 'buid1', 'operation_type': 'operation'},
    )

    assert response.status_code == 409


async def test_double_create(taxi_bank_authorization, pgsql):
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/create_track',
        headers={'X-Idempotency-Token': 'idempotency-key'},
        json={'buid': 'buid1', 'operation_type': 'operation'},
    )

    assert response.status_code == 200
    track_id = response.json()['track_id']

    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/create_track',
        headers={'X-Idempotency-Token': 'idempotency-key'},
        json={'buid': 'buid1', 'operation_type': 'operation'},
    )

    assert response.status_code == 200
    assert track_id == response.json()['track_id']


async def test_antirfraud_context_id(taxi_bank_authorization, pgsql):
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/create_track',
        headers={'X-Idempotency-Token': 'idempotency-key'},
        json={
            'buid': 'buid1',
            'operation_type': 'operation',
            'antifraud_context_id': 'antifraud_context_id',
        },
    )

    assert response.status_code == 200
    track_id = response.json()['track_id']
    track = select_track(pgsql, track_id)
    assert track == (
        'idempotency-key',
        'buid1',
        'operation',
        'antifraud_context_id',
    )
