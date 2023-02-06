import pytest


async def test_internal_payment_client(debts_client):
    _, status = await debts_client.get_payment_availability()
    assert status == 400

    _, status = await debts_client.get_payment_availability(
        phone_id='ph', brand='yataxi',
    )
    assert status == 200


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_internal_payment_debts(debts_client):
    response, status = await debts_client.get_payment_availability(
        phone_id='phone_id_2', brand='yataxi',
    )
    assert status == 200
    assert response['cards_available'] is False

    response, status = await debts_client.get_payment_availability(
        phone_id='phone_id_4', brand='yataxi',
    )
    assert status == 200
    assert response['cards_available'] is True
