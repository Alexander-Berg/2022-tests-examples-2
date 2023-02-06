import pytest


@pytest.mark.now('2019-12-10T09:19:00.000Z')
async def test_internal_payment_debts_empty(debts_client):
    response, status = await debts_client.get_payment_filters(
        phone_id='777775555555555555555555', brand='yataxi',
    )
    assert status == 200
    assert not response['payment_filters']


@pytest.mark.now('2019-12-10T09:19:00.000Z')
@pytest.mark.config(
    APPLICATION_BRAND_RELATED_BRANDS={'yataxi': ['yango']},
    APPLICATION_MAP_BRAND={'iphone': 'yango'},
)
async def test_can_be_paid_by_card(debts_client):
    response, status = await debts_client.get_payment_filters(
        phone_id='555555555555555555555555', brand='yataxi',
    )
    assert status == 200
    assert response['payment_filters'] == ['can_be_paid_by_card']


@pytest.mark.now('2019-12-10T09:19:00.000Z')
@pytest.mark.config(APPLICATION_MAP_BRAND={'uber_iphone': 'yataxi'})
async def test_need_cvn(debts_client):
    response, status = await debts_client.get_payment_filters(
        phone_id='555555555555555555555555', brand='yataxi',
    )
    assert status == 200
    assert response['payment_filters'] == ['need_cvn', 'debt']


@pytest.mark.now('2019-12-10T09:19:00.000Z')
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
async def test_need_accept(debts_client):
    response, status = await debts_client.get_payment_filters(
        phone_id='555555555555555555555555', brand='yataxi',
    )
    assert status == 200
    assert response['payment_filters'] == ['need_accept', 'debt']


@pytest.mark.now('2019-12-10T09:19:00.000Z')
@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'some_app': 'yataxi2'})
async def test_debts(debts_client):
    response, status = await debts_client.get_payment_filters(
        phone_id='555555555555555555555555', brand='yataxi2',
    )
    assert status == 200
    assert response['payment_filters'] == ['debt']


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'some_app': 'yataxi'},
    APPLICATION_BRAND_RELATED_BRANDS={'yataxi': ['yataxi2']},
)
async def test_related_brands(debts_client):
    response, status = await debts_client.get_payment_filters(
        phone_id='555555555555555555555555', brand='yataxi',
    )
    assert status == 200
    assert response['payment_filters'] == ['debt']
