import math

import pytest

from tests_eats_cart import utils


@pytest.mark.parametrize(
    'eater_id, eater_ok, subtotal, total',
    [
        pytest.param(21, False, 0, 0, id='user_wo_cart'),
        pytest.param(1, True, 115, 135, id='user_with_promocode'),
        pytest.param(2, True, 115, 135, id='user_without_promocode'),
        pytest.param(3, True, 115, 135, id='user_with_discount_and_promocode'),
    ],
)
@pytest.mark.parametrize(
    'promocode_valid, with_code_domain',
    [
        pytest.param(False, True, id='invalid_promocode_with_code_domain'),
        pytest.param(False, False, id='invalid_promocode_wo_code_domain'),
        pytest.param(True, False, id='valid_promocode'),
    ],
)
@pytest.mark.parametrize(
    'code_type, amount, percent, amount_limit, expected_disount',
    [
        pytest.param(
            'fixed', '100', None, None, 100, id='fixed_promocode_below_total',
        ),
        pytest.param(
            'fixed', '200', None, None, 135, id='fixed_promocode_above_total',
        ),
        pytest.param(
            'percent',
            None,
            '15',
            '30',
            20.25,
            id='percent_promocode_below_limit',
        ),
        pytest.param(
            'percent',
            None,
            '14',
            '30',
            18.9,
            id='percent_promocode_below_limit',
        ),
        pytest.param(
            'percent',
            None,
            '15',
            '20',
            20,
            id='percent_promocode_above_limit',
        ),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
async def test_apply_promocode(
        taxi_eats_cart,
        mockserver,
        local_services,
        eater_id,
        eater_ok,
        promocode_valid,
        with_code_domain,
        code_type,
        amount,
        percent,
        amount_limit,
        expected_disount,
        subtotal,
        total,
):
    code = 'PROMOCODE'
    local_services.set_place_slug('place_2')

    @mockserver.json_handler(
        '/eats-core-promocode/internal-api/v1/promocodes/validate',
    )
    def mock_validate(request):
        assert request.json == {
            'code': code,
            'user': {'id': str(eater_id), 'idProvider': 'eats'},
            'place': {'id': '2', 'eda_id': 2},
            'place_business': 'restaurant',
            'shipping_type': 'delivery',
            'paymentMethod': 'taxi',
            'applyForAmount': str(subtotal),
            'items': [{'id': '232323'}],
        }
        validation_response = {
            'payload': {
                'validationResult': {
                    'valid': promocode_valid,
                    'message': 'msg',
                },
            },
        }
        if promocode_valid:
            promocode = {
                'discount': (amount if code_type == 'fixed' else percent),
                'discountType': code_type,
                'discountResult': '0',
            }
            if amount_limit:
                promocode['discountLimit'] = amount_limit
            validation_response['payload']['validationResult'][
                'promocode'
            ] = promocode
        elif with_code_domain:
            validation_response['code'] = 20
            validation_response['domain'] = 'Network'
        return validation_response

    response = await taxi_eats_cart.post(
        '/api/v1/cart/promocode',
        json={'code': code},
        headers=utils.get_auth_headers(eater_id=eater_id),
    )
    if eater_ok and promocode_valid:
        assert response.status_code == 204
    else:
        assert response.status_code == 400
        if eater_ok:
            promocode_resp = response.json()
            assert promocode_resp['code'] == 20 if with_code_domain else 25
            assert (
                promocode_resp['domain'] == 'Network'
                if with_code_domain
                else 'UserData'
            )
    assert mock_validate.times_called == (1 if eater_ok else 0)

    cart_resp = await taxi_eats_cart.get(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id=eater_id),
    )
    assert cart_resp.status_code == 200

    cart = cart_resp.json()

    proposal_response = await taxi_eats_cart.get(
        '/api/v1/cart/promocode/proposal/paymethod',
        params={'code': code, 'payment_method_id': 3},
        headers=utils.get_auth_headers(eater_id=eater_id),
    )

    if eater_ok and promocode_valid:
        assert proposal_response.status_code == 200
    else:
        assert proposal_response.status_code == 400
    assert mock_validate.times_called == (2 if eater_ok else 0)

    if eater_ok and promocode_valid:
        int_discount = math.floor(expected_disount)
        int_total = math.ceil(total - expected_disount)
        assert cart['discount'] == int_discount
        assert float(cart['decimal_discount']) == expected_disount
        assert cart['total'] == int_total
        assert float(cart['decimal_total']) == total - expected_disount
        assert 'promocode' in cart
        assert cart['promocode']['code'] == code
        assert cart['promocode']['description'] == ''  # TODO(EDAJAM-30)
        assert proposal_response.json()['discount'] == int_discount


@pytest.mark.parametrize(
    'eater_id, eater_ok',
    [
        pytest.param(21, False, id='user_wo_cart'),
        pytest.param(1, True, id='user_with_promocode'),
        pytest.param(2, True, id='user_without_promocode'),
    ],
)
@pytest.mark.pgsql('eats_cart', files=['cart.sql'])
async def test_delete_promocode(
        taxi_eats_cart, local_services, eater_id, eater_ok,
):
    local_services.set_place_slug('place_2')
    response = await taxi_eats_cart.delete(
        '/api/v1/cart/promocode',
        headers=utils.get_auth_headers(eater_id=eater_id),
    )

    assert response.status_code == (204 if eater_ok else 400)

    cart_resp = await taxi_eats_cart.get(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(eater_id=eater_id),
    )
    assert cart_resp.status_code == 200

    cart = cart_resp.json()

    if 'promocode' in cart:
        assert not cart['promocode']
    assert cart['discount'] == 0
    assert cart['decimal_discount'] == '0'
