from tests_bank_userinfo import utils


async def test_empty_buid(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/delete_user', json={'buid': ''},
    )
    assert response.status == 400


async def test_invalid_buid(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/delete_user', json={'buid': '1-2-3-4-5'},
    )
    assert response.status == 400


async def test_unknown_buid(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/delete_user',
        json={'buid': '00000000-0000-0000-0000-000000000001'},
    )
    assert response.status == 404


async def test_delete_buid(taxi_bank_userinfo, mockserver, pgsql):
    buid = 'eec3d97f-a6d0-4047-b2a0-cdb64a5fc855'
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/delete_user',
        json={'buid': buid, 'reason': 'testing'},
    )
    assert response.status == 200

    cursor = pgsql['bank_userinfo'].cursor()
    cursor.execute(
        'SELECT bank_uid, yandex_uid, phone_id, status '
        'FROM bank_userinfo.buids '
        f'WHERE bank_uid = \'{buid}\'::UUID',
    )
    buids = cursor.fetchall()

    last_hist_record = utils.select_buid_history(pgsql, buid)[0]
    assert last_hist_record['bank_uid'] == buid
    assert last_hist_record['status'] == 'NEW'
    assert last_hist_record['operation_type'] == 'DELETE'
    assert last_hist_record['reason'] == 'testing'

    assert len(buids) == 1
    assert buids[0] == (buid, None, None, 'DEACTIVATED')


async def test_delete_buid_without_uid_and_phone_id(
        taxi_bank_userinfo, mockserver, pgsql,
):
    buid = 'eec3d97f-a6d0-4047-b2a0-cdb64a5fc866'
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/delete_user',
        json={'buid': buid, 'reason': 'testing'},
    )
    assert response.status == 200

    cursor = pgsql['bank_userinfo'].cursor()
    cursor.execute(
        'SELECT bank_uid, yandex_uid, phone_id, status '
        'FROM bank_userinfo.buids '
        f'WHERE bank_uid = \'{buid}\'::UUID',
    )
    buids = cursor.fetchall()

    last_hist_record = utils.select_buid_history(pgsql, buid)[0]
    assert last_hist_record['bank_uid'] == buid
    assert last_hist_record['status'] == 'FINAL'
    assert last_hist_record['operation_type'] == 'DELETE'
    assert last_hist_record['reason'] == 'testing'

    assert len(buids) == 1
    assert buids[0] == (buid, None, None, 'DEACTIVATED')
