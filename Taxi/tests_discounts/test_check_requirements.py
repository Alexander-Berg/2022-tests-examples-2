import copy
import json

import pytest

from tests_discounts import common

DEFAULT_CHECK_REQUEST = {
    'yandex_uid': 'yandex_uid1',
    'discount_info': {'discount_series_id': 'discount1'},
    'restrictions_data': {'payment_info': {'type': 'none'}},
}


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
@pytest.mark.parametrize(
    'payment_method,payment_method_id,valid',
    [
        pytest.param('googlepay', None, False, id='googlepay not in discount'),
        pytest.param('cash', None, True, id='cash always valid'),
        pytest.param('card', 'method_123456', True, id='card valid'),
        pytest.param(
            'card',
            'method_123456',
            True,
            id='card valid with empty config',
            marks=pytest.mark.config(CARDSTORAGE_SUPPORTED_PAYMENT_TYPES=[]),
        ),
        pytest.param(
            'card',
            'method_123456',
            False,
            id='card invalid',
            marks=pytest.mark.config(
                CARDSTORAGE_SUPPORTED_PAYMENT_TYPES=['does not have card'],
            ),
        ),
        pytest.param('card', 'method_654321', False),
    ],
)
async def test_check_payment_restrictions(
        taxi_discounts, mockserver, payment_method, payment_method_id, valid,
):
    @mockserver.json_handler('/cardstorage/v1/card')
    def _mock_v1_card(request):
        card_numbers = {
            'method_123456': '123456_____________',
            'method_654321': '654321_____________',
        }
        data = json.loads(request.get_data())
        card_id = data['card_id']
        return {
            'card_id': card_id,
            'bin_labels': ['bin_label'],
            'billing_card_id': '',
            'permanent_card_id': '',
            'currency': 'rub',
            'expiration_month': 12,
            'expiration_year': 30,
            'number': card_numbers[card_id],
            'owner': '',
            'possible_moneyless': True,
            'region_id': '',
            'regions_checked': [],
            'system': '',
            'valid': True,
            'bound': False,
            'unverified': False,
            'busy': False,
            'busy_with': [],
            'from_db': True,
        }

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _rules_select(request):
        return {'subventions': []}

    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()
    check_request = copy.deepcopy(DEFAULT_CHECK_REQUEST)
    check_request['yandex_uid'] = 'yandex_uid'
    payment_info = check_request['restrictions_data']['payment_info']
    payment_info['type'] = payment_method
    if payment_method_id:
        payment_info['method_id'] = payment_method_id

    await taxi_discounts.invalidate_caches()
    response = await taxi_discounts.post(
        'v1/check-discount-restrictions',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        json=check_request,
    )
    assert response.status_code == 200
    assert response.json() == {'valid': valid}
