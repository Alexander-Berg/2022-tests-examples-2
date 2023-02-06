import pytest

from . import headers
from .plugins import mock_api_proxy


def _make_payment_method(payment_type, payment_id=None):
    payment = {'type': payment_type}
    if payment_id is not None:
        payment['id'] = payment_id
    return payment


def _to_request_pm(api_proxy_pm):
    return _make_payment_method(
        api_proxy_pm.get('type'), api_proxy_pm.get('id'),
    )


CARD = _to_request_pm(mock_api_proxy.CARD)
APPLE_PAY = _to_request_pm(mock_api_proxy.APPLE_PAY)
GOOGLE_PAY = _to_request_pm(mock_api_proxy.GOOGLE_PAY)
CIBUS = _to_request_pm(mock_api_proxy.CIBUS)
SBP = _to_request_pm(mock_api_proxy.SBP)


@pytest.fixture(name='grocery_payments_validate')
def _grocery_payments_validate(taxi_grocery_payments, api_proxy):
    async def _inner(
            payment_methods, need_track_payment=None, status_code=200,
    ):
        response = await taxi_grocery_payments.post(
            '/payments/v1/validate',
            json={
                'payment_methods': payment_methods,
                'location': mock_api_proxy.LOCATION,
                'need_track_payment': need_track_payment,
            },
            headers=headers.DEFAULT_HEADERS,
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


@pytest.mark.parametrize(
    'payment_methods', [[], [CARD], [APPLE_PAY, GOOGLE_PAY, CIBUS], [SBP]],
)
async def test_validate(grocery_payments_validate, api_proxy, payment_methods):
    response = await grocery_payments_validate(payment_methods=payment_methods)

    if payment_methods:
        assert api_proxy.lpm_times_called() == 1

    assert response == {}


@pytest.mark.parametrize(
    'payment_method, api_proxy_payment, error_code',
    [
        (GOOGLE_PAY, mock_api_proxy.GOOGLE_PAY, None),
        (GOOGLE_PAY, None, 'not_exists'),
    ],
)
async def test_validate_google_pay(
        grocery_payments_validate,
        api_proxy,
        payment_method,
        api_proxy_payment,
        error_code,
):
    api_proxy.googlepay_data = api_proxy_payment

    response = await grocery_payments_validate(
        payment_methods=[payment_method],
    )

    if error_code is None:
        assert response == {}
    else:
        assert response['errors'][0]['error_code'] == error_code


@pytest.mark.parametrize(
    'payment_method, api_proxy_payment, error_code',
    [
        (APPLE_PAY, mock_api_proxy.APPLE_PAY, None),
        (APPLE_PAY, None, 'not_exists'),
    ],
)
async def test_validate_apple_pay(
        grocery_payments_validate,
        api_proxy,
        payment_method,
        api_proxy_payment,
        error_code,
):
    api_proxy.applepay_data = api_proxy_payment

    response = await grocery_payments_validate(
        payment_methods=[payment_method],
    )

    if error_code is None:
        assert response == {}
    else:
        assert response['errors'][0]['error_code'] == error_code


@pytest.mark.parametrize(
    'payment_method, error_code',
    [
        (_make_payment_method('card', 'card-x0000'), 'not_exists'),
        (_make_payment_method('card', 'card-x1234'), 'not_available'),
    ],
)
async def test_validate_with_errors(
        grocery_payments_validate, api_proxy, payment_method, error_code,
):
    api_proxy.add_payment_method(
        {
            **mock_api_proxy.CARD,
            'id': 'card-x1234',
            'availability': {'available': False, 'disabled_reason': ''},
        },
    )

    response = await grocery_payments_validate(
        payment_methods=[payment_method],
    )

    assert response == {
        'errors': [{'error_code': error_code, 'method': payment_method}],
    }


@pytest.mark.parametrize(
    'need_track_payment, error_code', [(False, 'not_available'), (True, None)],
)
async def test_validate_with_need_track_payment(
        grocery_payments_validate, api_proxy, need_track_payment, error_code,
):
    payment_method = _make_payment_method('card', 'card-x1234')

    api_proxy.add_payment_method(
        {
            **mock_api_proxy.CARD,
            'id': 'card-x1234',
            'availability': {'available': False, 'disabled_reason': ''},
        },
    )

    response = await grocery_payments_validate(
        payment_methods=[payment_method],
        need_track_payment=need_track_payment,
    )

    if error_code is None:
        assert response == {}
    else:
        assert response == {
            'errors': [{'error_code': error_code, 'method': payment_method}],
        }


@pytest.mark.parametrize(
    'verified, error_code', [(False, None), (True, 'not_available')],
)
async def test_non_valid_verified_meta(
        grocery_payments_validate, api_proxy, verified, error_code,
):
    payment_method = _make_payment_method('card', 'card-x1234')
    payment_method['meta'] = {'card': {'verified': verified}}

    api_proxy.add_payment_method(
        {
            **mock_api_proxy.CARD,
            'id': 'card-x1234',
            'availability': {'available': False, 'disabled_reason': ''},
        },
    )

    response = await grocery_payments_validate(
        payment_methods=[payment_method], need_track_payment=True,
    )

    if error_code is None:
        assert response == {}
    else:
        assert response == {
            'errors': [{'error_code': error_code, 'method': payment_method}],
        }


@pytest.mark.parametrize(
    'payment_method, is_available, error_code',
    [
        (_make_payment_method('corp', 'correct-id'), True, ''),
        (_make_payment_method('corp', 'wrong-id'), True, 'not_exists'),
        (_make_payment_method('corp', 'correct-id'), False, 'not_available'),
    ],
)
async def test_validate_corp_pm(
        grocery_payments_validate,
        api_proxy,
        payment_method,
        is_available,
        error_code,
):
    api_proxy.corp_data['id'] = 'correct-id'
    api_proxy.corp_data['availability']['available'] = is_available

    response = await grocery_payments_validate(
        payment_methods=[payment_method],
    )

    if error_code == '':
        assert response == {}
    else:
        assert response == {
            'errors': [{'error_code': error_code, 'method': payment_method}],
        }


@pytest.mark.parametrize(
    'payment_method, is_available, error_code',
    [
        (
            _make_payment_method('badge', 'badge:yandex_badge:correct-id'),
            True,
            '',
        ),
        (
            _make_payment_method('badge', 'badge:yandex_badge:wrong-id'),
            True,
            'not_exists',
        ),
        (
            _make_payment_method('badge', 'badge:yandex_badge:correct-id'),
            False,
            'not_available',
        ),
    ],
)
async def test_validate_badge_pm(
        grocery_payments_validate,
        api_proxy,
        payment_method,
        is_available,
        error_code,
):
    api_proxy.badge_data['id'] = 'badge:yandex_badge:correct-id'
    api_proxy.badge_data['availability']['available'] = is_available

    response = await grocery_payments_validate(
        payment_methods=[payment_method],
    )

    if error_code == '':
        assert response == {}
    else:
        assert response == {
            'errors': [{'error_code': error_code, 'method': payment_method}],
        }


@pytest.mark.parametrize(
    'exp_validate_methods, payment_methods, expected_errors, lpm_times_called',
    [
        (
            ['card'],
            [CARD, APPLE_PAY, GOOGLE_PAY],
            [{'error_code': 'not_available', 'method': CARD}],
            1,
        ),
        (
            ['applepay', 'googlepay'],
            [CARD, APPLE_PAY, GOOGLE_PAY],
            [
                {'error_code': 'not_exists', 'method': APPLE_PAY},
                {'error_code': 'not_exists', 'method': GOOGLE_PAY},
            ],
            1,
        ),
        (['applepay', 'googlepay'], [CARD], None, 0),
    ],
)
async def test_filter_payment_methods_to_validate(
        grocery_payments_validate,
        api_proxy,
        experiments3,
        exp_validate_methods,
        payment_methods,
        expected_errors,
        lpm_times_called,
):
    experiments3.add_config(
        name='grocery_payments_validate_methods',
        consumers=['grocery-payments'],
        default_value={'payment_types': exp_validate_methods},
    )

    api_proxy.card_data['availability']['available'] = False
    api_proxy.card_data['available'] = False

    api_proxy.badge_data['availability']['available'] = False
    api_proxy.badge_data['available'] = False

    api_proxy.corp_data['availability']['available'] = False
    api_proxy.corp_data['available'] = False

    api_proxy.applepay_data = None
    api_proxy.googlepay_data = None
    api_proxy.cibus_data = None

    response = await grocery_payments_validate(payment_methods=payment_methods)

    assert api_proxy.lpm_times_called() == lpm_times_called

    if expected_errors is None:
        assert response == {}
    else:
        for expected_error in expected_errors:
            assert expected_error in response['errors']
