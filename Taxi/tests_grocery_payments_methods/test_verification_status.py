import pytest

from tests_grocery_payments_methods import consts


@pytest.fixture(name='verification_status')
def _verification_status(taxi_grocery_payments_methods):
    async def _inner(request, headers=None):
        headers = headers or consts.DEFAULT_HEADERS
        return await taxi_grocery_payments_methods.get(
            '/lavka/v1/payments-methods/v1/verification/status',
            params=request,
            headers=headers,
        )

    return _inner


async def test_card_antifraud_request(verification_status, card_antifraud):
    request = {'verification_id': 'verification_id'}

    headers = {
        **consts.DEFAULT_HEADERS,
        'X-YProxy-Header-Host': 'X-YProxy-Header-Host',
    }

    headers_check = {'X-YProxy-Header-Host': 'X-YProxy-Header-Host'}

    card_antifraud.verifications_status.check(headers=headers_check, **request)

    response = await verification_status(request=request, headers=headers)

    assert response.json() == consts.VERIFICATION_STATUS_RESPONSE

    assert card_antifraud.verifications_status.times_called == 1


@pytest.mark.parametrize('status_code', [404, 429])
async def test_card_antifraud_errors(
        verification_status, card_antifraud, status_code,
):
    request = {'verification_id': 'verification_id'}

    card_antifraud.verifications_status.status_code = status_code
    response = await verification_status(request=request)

    assert card_antifraud.verifications_status.times_called == 1
    assert response.status_code == status_code
