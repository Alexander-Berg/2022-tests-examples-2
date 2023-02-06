import pytest


@pytest.mark.now('2020-03-10T11:20:00')
async def test_add_first_charge_back_info(web_app_client, db, now):
    chargeback_info = {
        'trust_payment_id': 'some_id',
        'bank_chargeback_code': 'some_code',
        'bank_verdict': 'deducted',
        'first_request_date': '2019-12-20',
        'status': 'accept',
        'tickets': ['t1', 't2'],
    }
    login = 'login'
    response = await web_app_client.post(
        '/v1/add_chargeback_info',
        json=chargeback_info,
        headers={'X-Yandex-Login': login},
    )
    assert response.status == 200
    del chargeback_info['trust_payment_id']
    chargeback_info['last_editor_login'] = login
    chargeback_info['last_modification_time'] = '2020-03-10T14:20:00+03:00'
    assert await response.json() == chargeback_info

    row = await db.antifraud_chargeback_info_mdb.find_one({'_id': 'some_id'})
    assert row['updated'] == now
    snapshots = list(row['snapshot_list'])
    assert len(snapshots) == 1
    chargeback_info_row = snapshots[0]
    del chargeback_info['last_modification_time']
    chargeback_info['snapshot_time'] = now
    assert chargeback_info_row == chargeback_info


@pytest.mark.now('2020-03-10T11:20:00')
@pytest.mark.filldb(antifraud_chargeback_info_mdb='few')
async def test_add_charge_back_info(web_app_client, db, now):
    chargeback_info = {
        'trust_payment_id': 'some_id',
        'bank_chargeback_code': 'some_code',
        'bank_verdict': 'deducted',
        'first_request_date': '2019-12-20',
        'status': 'accept',
        'tickets': ['t1', 't2'],
    }
    login = 'login1'
    response = await web_app_client.post(
        '/v1/add_chargeback_info',
        json=chargeback_info,
        headers={'X-Yandex-Login': login},
    )
    assert response.status == 200
    del chargeback_info['trust_payment_id']
    chargeback_info['last_editor_login'] = login
    chargeback_info['last_modification_time'] = '2020-03-10T14:20:00+03:00'
    assert await response.json() == chargeback_info

    row = await db.antifraud_chargeback_info_mdb.find_one({'_id': 'some_id'})
    assert row['updated'] == now
    snapshots = list(row['snapshot_list'])
    assert len(snapshots) == 3
    chargeback_info_row = snapshots[-1]
    del chargeback_info['last_modification_time']
    chargeback_info['snapshot_time'] = now
    assert chargeback_info_row == chargeback_info
