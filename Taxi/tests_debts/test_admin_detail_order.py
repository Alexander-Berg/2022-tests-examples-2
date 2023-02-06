import pytest


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_order_exist_in_dborders_and_debts(debts_client):
    response, code = await debts_client.get_admin_detail_order(
        order_id='order_id_8',
    )
    assert code == 200
    assert response['order_id'] == 'order_id_8'
    assert response['phone_id'] == '222222222222222222222222'
    assert response['yandex_uid'] == 'yandex_uid_123'
    assert response['affects_order'] is True
    assert response['visible_for_user'] is True
    assert response['card_related_debts'] == ['order_id_1', 'order_id_2']
    assert response['phone_related_debts'] == []
    assert 'orderlocks' not in response['data_source']
    assert 'pg_debts' in response['data_source']
    assert 'orders' in response['data_source']
    assert response['currency'] == 'BTC'


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_order_exist_only_in_dborders(debts_client):
    response, code = await debts_client.get_admin_detail_order(
        order_id='mongo_order_3',
    )
    assert code == 200
    assert response['order_id'] == 'mongo_order_3'
    assert response['currency'] == 'RUB'
    assert response['phone_id'] == '555555555555555555555555'
    assert response['yandex_uid'] == 'yandex_uid_123'
    assert response['affects_order'] is False
    assert response['visible_for_user'] is True
    assert response['card_related_debts'] == []
    assert response['phone_related_debts'] == []
    assert 'orderlocks' not in response['data_source']
    assert 'pg_debts' not in response['data_source']
    assert 'orders' in response['data_source']


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_order_exist_only_in_debts(debts_client):
    response, code = await debts_client.get_admin_detail_order(
        order_id='order_id_10',
    )
    assert code == 200
    assert response['order_id'] == 'order_id_10'
    assert response['phone_id'] == '777777777777777777777777'
    assert response['currency'] == 'BTC'
    assert response['brand'] == 'yataxi2'
    assert response['yandex_uid'] == 'yandex_uid_123'
    assert response['affects_order'] is True
    assert response['visible_for_user'] is False
    assert response['phone_related_debts'] == ['order_id_10']
    assert 'orderlocks' in response['data_source']
    assert 'pg_debts' in response['data_source']
    assert 'orders' not in response['data_source']


@pytest.mark.parametrize(
    'order_id,orderlocks',
    [
        ('order_id_30', True),
        ('order_id_31', True),
        ('order_id_32', True),
        ('order_id_33', False),
    ],
)
@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_order_not_exist_in_dborders_and_debts(
        debts_client, order_id, orderlocks,
):
    response, code = await debts_client.get_admin_detail_order(
        order_id=order_id,
    )
    assert code == 200
    assert response['affects_order'] is False
    assert response['visible_for_user'] is False
    assert ('orderlocks' in response['data_source']) == orderlocks
    assert 'pg_debts' not in response['data_source']
    assert 'orders' not in response['data_source']
