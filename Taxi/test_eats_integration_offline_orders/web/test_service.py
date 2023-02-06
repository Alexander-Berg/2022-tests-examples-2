import pytest


@pytest.mark.skip
@pytest.mark.servicetest
@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_SETTINGS={'fake_pos_enabled': True},
    EI_OFFLINE_ORDERS_PAYTURE_SETTINGS={
        'fake_contact': 'dev0@yandex.ru',
        'frontend_callback_url': (
            'https://eda.yandex.ru?orderid={orderid}&result={success}'
        ),
        'get_state_path': '/apim/GetState',
        'host': 'https://sandbox3.payture.com',
        'init_path': '/apim/Init',
        'pay_path': '/apim/Pay',
    },
)
@pytest.mark.pgsql('eats_integration_offline_orders', files=['tables.sql'])
async def test_service(taxi_eats_integration_offline_orders_web):
    pass
