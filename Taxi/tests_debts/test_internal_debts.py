import pytest


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_debt(debts_client):
    application = 'android'
    yandex_uid = 'yandex_uid_2'
    phone_id = 'phone_id_3'
    response, code = await debts_client.get_debts_list(
        yandex_uid=yandex_uid, phone_id=phone_id, application=application,
    )
    assert code == 200
    assert len(response['debts']) == 1
    assert response['debts'] == [
        {'currency': 'BTC', 'order_id': 'order_id_5', 'value': '3'},
    ]


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_uknow_user(debts_client):
    application = 'android'
    yandex_uid = 'random_uid'
    phone_id = 'random_phone_id'
    response, code = await debts_client.get_debts_list(
        yandex_uid=yandex_uid, phone_id=phone_id, application=application,
    )
    assert code == 200

    assert not response['debts']
