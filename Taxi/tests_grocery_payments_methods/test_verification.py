import pytest

from tests_grocery_payments_methods import consts


@pytest.fixture(name='verification')
def _verification(taxi_grocery_payments_methods):
    async def _inner(request=None, headers=None):
        if request is None:
            request = {'card_id': 'card_id', 'country_iso2': 'RU'}

        if headers is None:
            headers = {
                **consts.DEFAULT_HEADERS,
                'X-Idempotency-Token': 'idempotency_token',
            }

        return await taxi_grocery_payments_methods.post(
            '/lavka/v1/payments-methods/v1/verification',
            json=request,
            headers=headers,
        )

    return _inner


async def test_card_antifraud_request(verification, card_antifraud):
    request = {
        'card_id': 'card_id',
        'region_id': 123,
        'country_iso2': 'RU',
        'currency': 'RUB',
        'pass_params': {
            'avs_data': {
                'post_code': 'post_code',
                'street_address': 'street_address',
            },
        },
    }

    idempotency_token = 'idempotency_token'

    headers = {
        **consts.DEFAULT_HEADERS,
        'X-Idempotency-Token': idempotency_token,
    }

    headers_check = {
        'X-Idempotency-Token': idempotency_token,
        'X-AppMetrica-DeviceId': consts.APPMETRICA_DEVICE_ID,
    }

    card_antifraud.verifications.check(headers=headers_check, **request)

    response = await verification(request=request, headers=headers)

    assert response.json() == consts.VERIFICATION_RESPONSE

    assert card_antifraud.verifications.times_called == 1


@pytest.mark.parametrize('status_code', [409, 429])
async def test_card_antifraud_errors(
        verification, card_antifraud, status_code,
):
    card_antifraud.verifications.status_code = status_code
    response = await verification()

    assert card_antifraud.verifications.times_called == 1
    assert response.status_code == status_code
