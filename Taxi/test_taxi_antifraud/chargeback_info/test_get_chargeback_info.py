import pytest


async def test_get_chargeback_no_data(web_app_client):
    response = await web_app_client.get(
        '/v1/chargeback_info',
        params={'trust_payment_id': 'not_existing_value'},
    )
    assert response.status == 200

    assert await response.json() == {}


@pytest.mark.filldb(antifraud_chargeback_info_mdb='one')
async def test_get_chargeback_one_snapshot(web_app_client):
    response = await web_app_client.get(
        '/v1/chargeback_info',
        params={'trust_payment_id': 'transaction_with_no_changes'},
    )
    assert response.status == 200

    raw = {
        'bank_chargeback_code': 'some_code',
        'bank_verdict': 'deducted',
        'first_request_date': '2019-12-20',
        'status': 'accept',
        'tickets': ['t1', 't2'],
        'last_editor_login': 'login',
        'last_modification_time': '2019-12-20T12:05:39+03:00',
    }

    expected = {'chargeback_info': raw}

    assert await response.json() == expected


@pytest.mark.filldb(antifraud_chargeback_info_mdb='few')
async def test_get_chargeback_few_snapshots(web_app_client):
    response = await web_app_client.get(
        '/v1/chargeback_info',
        params={'trust_payment_id': 'transaction_with_no_changes'},
    )
    assert response.status == 200

    raw = {
        'bank_chargeback_code': 'another_code',
        'bank_verdict': 'proved',
        'first_request_date': '2019-12-21',
        'status': 'other',
        'tickets': ['t1', 't2', 't3'],
        'last_editor_login': 'last_login',
        'last_modification_time': '2019-12-25T12:05:39+03:00',
    }

    expected = {'chargeback_info': raw}

    assert await response.json() == expected
