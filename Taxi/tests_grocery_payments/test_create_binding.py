import pytest

from . import headers
from . import models
from .plugins import configs

COUNTRY = models.Country.Russia
DOMAIN_SFX = 'com'


@pytest.fixture(name='grocery_payments_create_binding')
def _grocery_payments_create_binding(taxi_grocery_payments):
    async def _inner(**kwargs):
        return await taxi_grocery_payments.post(
            '/lavka/v1/payments/v1/create-binding',
            json={
                'country_iso3': COUNTRY.country_iso3,
                'domain_sfx': DOMAIN_SFX,
                **kwargs,
            },
            headers=headers.DEFAULT_HEADERS,
        )

    return _inner


async def test_basic(
        grocery_payments_create_binding, grocery_payments_configs, trust,
):
    purchase_token = 'purchase_token'
    binding_url = 'binding_url'
    service_token = 'service_token'

    grocery_payments_configs.grocery_service_token(service_token)

    trust.bindings_create.mock_response(
        status='success', purchase_token=purchase_token,
    )

    trust.bindings_start.mock_response(
        status='success', binding_url=binding_url,
    )

    trust.bindings_create.check(
        currency=COUNTRY.currency,
        domain_sfx=DOMAIN_SFX,
        lang=headers.DEFAULT_LOCALE,
        headers={
            'X-Service-Token': service_token,
            'X-Uid': headers.YANDEX_UID,
        },
    )

    trust.bindings_start.check(
        headers={
            'X-Service-Token': service_token,
            'X-Uid': headers.YANDEX_UID,
        },
    )

    response = await grocery_payments_create_binding()
    assert response.status_code == 200
    assert response.json() == {'binding_url': binding_url}

    assert trust.bindings_create.times_called == 1
    assert trust.bindings_start.times_called == 1


async def test_400_create(grocery_payments_create_binding, trust):
    status = 'fail'

    trust.bindings_create.mock_response(status=status, purchase_token='')

    response = await grocery_payments_create_binding()
    assert response.status_code == 400
    assert response.json() == {
        'code': 'create_binding_error',
        'message': status,
    }

    assert trust.bindings_create.times_called == 1
    assert trust.bindings_start.times_called == 0


async def test_400_start(grocery_payments_create_binding, trust):
    status = 'fail'

    trust.bindings_start.mock_response(status=status, binding_url='')

    response = await grocery_payments_create_binding()
    assert response.status_code == 400
    assert response.json() == {
        'code': 'start_binding_error',
        'message': status,
    }

    assert trust.bindings_create.times_called == 1
    assert trust.bindings_start.times_called == 1


async def test_400_too_many_bindings(
        grocery_payments_create_binding, trust, taxi_config,
):
    status_code = 'too_many_active_bindings'
    status_desc = 'User has too many active bindings'

    taxi_config.set_values(
        {'PERSONAL_WALLET_FIRM_BY_SERVICE': {'grocery': {'RUB': ''}}},
    )

    trust.bindings_create.status_code = 500
    trust.bindings_create.mock_response(
        status='error', status_code=status_code, status_desc=status_desc,
    )

    response = await grocery_payments_create_binding()
    assert response.status_code == 400
    assert response.json() == {'code': status_code, 'message': status_desc}

    assert trust.bindings_create.times_called == 1
    assert trust.bindings_start.times_called == 0


@configs.CARDSTORAGE_AVS_DATA
async def test_create_pass_params(grocery_payments_create_binding, trust):
    trust.bindings_create.check(pass_params=configs.PASS_PARAMS)

    response = await grocery_payments_create_binding()

    assert response.status_code == 200
    assert trust.bindings_create.times_called == 1
    assert trust.bindings_start.times_called == 1
