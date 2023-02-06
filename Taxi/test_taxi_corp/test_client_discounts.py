import datetime

from aiohttp import web
import pytest

LEGAL_TEXTS = {
    1: '<h1>Discount title</h1><p>Discount description</p>',
    2: '<h1>New discount title</h1><p>Another discount description</p>',
}

DISCOUNT_LINK_1 = {
    'amount_used': '100',
    'amounts': {
        'spent': {'sum': '100.0000', 'vat': '20.0000', 'with_vat': '120.0000'},
    },
    'currency': 'RUB',
    'discount_id': 1,
    'discount_name': 'fixed rule',
    'discount_services': ['eats2', 'drive'],
    'is_frozen': False,
    'legal_information': LEGAL_TEXTS[1],
    'link_id': 1,
    'rule': {
        'max_discount': '200',
        'max_orders': 5,
        'minimal_order_sum': '600',
        'percent': 10,
        'rule_class': 'first_orders_percent',
    },
    'times_left': 3,
    'times_used': 2,
    'valid_since': '2021-08-17T23:54:00+00:00',
    'valid_until': '2031-08-17T23:54:00+00:00',
}
DISCOUNT_LINK_2 = {
    'activated_at': '2021-10-01T01:00:00+00:00',
    'amount_left': '400.0000',
    'amount_used': '100',
    'amounts': {
        'left': {'sum': '400.0000', 'vat': '80.0000', 'with_vat': '480.0000'},
        'spent': {'sum': '100.0000', 'vat': '20.0000', 'with_vat': '120.0000'},
    },
    'currency': 'RUB',
    'discount_id': 2,
    'discount_name': 'first discount',
    'discount_services': ['eats2'],
    'is_frozen': False,
    'legal_information': LEGAL_TEXTS[2],
    'link_id': 2,
    'rule': {
        'max_amount_spent': '500',
        'max_discount': '200',
        'minimal_order_sum': '600',
        'percent': 10,
        'rule_class': 'amount_spent_percent',
    },
    'times_used': 1,
    'valid_since': '2031-09-01T00:00:00+00:00',
    'valid_until': '2031-10-01T00:00:00+00:00',
}

CORP_DISCOUNT_MOCK = {'items': [DISCOUNT_LINK_1, DISCOUNT_LINK_2]}


@pytest.fixture(name='mock_corp_discounts')
def mock_corp_discounts_fixture(mockserver):
    class MockCorpDiscounts:
        @staticmethod
        @mockserver.handler('/corp-discounts/v1/admin/client/links/list')
        async def links_list(request):
            if request.args.get('client_id') == 'client1':
                return web.json_response(CORP_DISCOUNT_MOCK)
            return web.json_response({'items': []})

        @staticmethod
        @mockserver.handler('/corp-discounts/v1/discounts/activate')
        async def activate_discount(request):
            return web.json_response(
                {'activated_at': datetime.datetime.now().isoformat()},
            )

    return MockCorpDiscounts()


@pytest.mark.parametrize(
    ['client_id', 'expected_response'],
    [
        pytest.param('client2', {'items': []}, id='no discounts'),
        pytest.param('client1', CORP_DISCOUNT_MOCK, id='with discounts'),
    ],
)
async def test_list_client_discounts(
        taxi_corp_auth_client,
        mock_corp_discounts,
        client_id,
        expected_response,
):
    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}/discounts/list'.format(client_id),
    )
    response_content = await response.json()
    assert response_content == expected_response
    assert mock_corp_discounts.links_list.times_called == 1


@pytest.mark.parametrize(
    [
        'passport_mock',
        'client_id',
        'link_id',
        'expected_status',
        'activate_times_called',
    ],
    [
        pytest.param(
            'client1', 'client1', 1, 200, 1, id='legal discount access',
        ),
        pytest.param(
            'client2', 'client2', 1, 403, 0, id='illegal discount access',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_activate_discount(
        passport_mock,
        taxi_corp_real_auth_client,
        mock_corp_discounts,
        client_id,
        link_id,
        expected_status,
        activate_times_called,
):
    response = await taxi_corp_real_auth_client.post(
        f'/1.0/client/{client_id}/discounts/activate',
        json={'link_id': link_id},
    )
    assert response.status == expected_status
    assert mock_corp_discounts.links_list.times_called == 1
    assert (
        mock_corp_discounts.activate_discount.times_called
        == activate_times_called
    )
