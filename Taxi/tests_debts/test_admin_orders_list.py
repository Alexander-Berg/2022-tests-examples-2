import pytest


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.parametrize(
    'phone_id,ans_order_id,ans_currency,ans_affect_on_order,'
    'ans_visible_for_user,ans_value, ans_data_source',
    [
        (
            '111111111111111111111111',
            'order_id_7',
            'RUB',
            False,
            True,
            '',
            ['orders'],
        ),
        (
            '222222222222222222222222',
            'order_id_8',
            'BTC',
            True,
            True,
            '10.0000',
            ['pg_debts', 'orders'],
        ),
        (
            '333333333333333333333333',
            'order_id_9',
            'RUB',
            True,
            False,
            '23.0000',
            ['pg_debts'],
        ),
        (
            '666666666666666666666666',
            'order_id_11',
            'BTC',
            False,
            True,
            '',
            ['orders', 'phonelocks'],
        ),
        (
            '777777777777777777777777',
            'order_id_10',
            'BTC',
            True,
            False,
            '1.0000',
            ['pg_debts', 'phonelocks'],
        ),
        (
            '999999999999999999999999',
            'order_id_12',
            None,
            False,
            True,
            '',
            ['orders', 'phonelocks'],
        ),
    ],
)
async def test_basic(
        debts_client,
        phone_id,
        ans_order_id,
        ans_currency,
        ans_affect_on_order,
        ans_visible_for_user,
        ans_value,
        ans_data_source,
):
    response, code = await debts_client.get_admin_orders_list(
        phone_id=phone_id,
    )
    assert code == 200

    if ans_currency is None:
        assert not response['debts']
        return

    assert response['debts'][0]['order_id'] == ans_order_id
    assert response['debts'][0]['currency'] == ans_currency
    assert response['debts'][0]['affects_order'] == ans_affect_on_order
    assert response['debts'][0]['visible_for_user'] == ans_visible_for_user
    assert response['debts'][0]['phone_id'] == phone_id
    if ans_value:
        assert response['debts'][0]['value'] == ans_value
    else:
        assert 'value' not in response['debts'][0]
    assert response['debts'][0]['data_source'] == ans_data_source


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_phonelocks(debts_client):
    phone_id = '888888888888888888888888'
    response, code = await debts_client.get_admin_orders_list(
        phone_id=phone_id,
    )
    assert code == 200
    assert response['debts'][0]['order_id'] == 'order_id_10'
    assert response['debts'][0]['affects_order'] is False
    assert response['debts'][0]['visible_for_user'] is False
    assert response['debts'][0]['phone_id'] == '888888888888888888888888'
    assert response['debts'][0]['data_source'] == ['phonelocks']


async def test_wrong_phone_id(debts_client):
    phone_id = '59e4598383edE0ee28d0145'
    _, code = await debts_client.get_admin_orders_list(phone_id=phone_id)
    assert code == 400

    phone_id = '3jf9349fj934jfoierfioerjf934f3*39'
    _, code = await debts_client.get_admin_orders_list(phone_id=phone_id)
    assert code == 400

    phone_id = '1111111111111111111111111111111111111111111111111111111'
    _, code = await debts_client.get_admin_orders_list(phone_id=phone_id)
    assert code == 400
