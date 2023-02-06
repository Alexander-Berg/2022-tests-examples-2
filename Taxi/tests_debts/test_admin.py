import pytest


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.parametrize(
    'phone_id,yandex_uid,debts',
    [
        ('phone_id_1', None, {'order_id_1', 'order_id_3'}),
        ('phone_id_2', None, {'order_id_4'}),
        ('phone_id_3', 'yandex_uid_4', {'order_id_4', 'order_id_5'}),
        (None, 'yandex_uid_2', {'order_id_3'}),
    ],
)
async def test_admin_by_user(debts_client, yandex_uid, phone_id, debts):
    response, code = await debts_client.admin_get_debts(
        yandex_uid=yandex_uid, phone_id=phone_id,
    )
    assert code == 200
    result_debts = {x['order_id'] for x in response['debts']}
    assert result_debts == debts


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_admin_get_debts_flow(debts_client):
    order_id = 'order_id_1'

    response, code = await debts_client.admin_get_debts(order_id=order_id)
    assert code == 200
    assert response['debts'][0]['order_id'] == order_id

    response, code = await debts_client.admin_release_debt(order_id=order_id)
    assert code == 200

    response, code = await debts_client.admin_get_debts(order_id=order_id)
    assert code == 200
    assert not response['debts']
