import copy
import decimal

import pytest

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(TVM_RULES=[{'src': 'cashback', 'dst': 'archive-api'}]),
]

DEFAULT_ORDER_ID = 'order_id_default'
DEFAULT_TARIFF_CLASS = 'econom'

DEFAULT_PROC = {
    '_id': DEFAULT_ORDER_ID,
    'status': 'finished',
    'order': {
        'user_uid': 'yandex_uid_66',
        'taxi_status': 'complete',
        'performer': {'tariff': {'class': DEFAULT_TARIFF_CLASS}},
        'nz': 'moscow',
        'cost': '300',
    },
    'extra_data': {'cashback': {'is_cashback': True}},
    'payment_tech': {'type': 'card'},
}


@pytest.mark.parametrize(
    'payment_type, expected_extra_payload',
    [('card', {}), ('corp', {'payment_type': 'corp'})],
)
@pytest.mark.parametrize(
    'order_id, cleared, expected_cashback',
    [
        # 100 * 0.5
        ('order_id_default', '100', decimal.Decimal('50')),
        # min(100 * 0.5, 40)
        ('order_id_with_limit', '100', decimal.Decimal('40')),
    ],
    ids=['basic_cashback', 'basic_cashback_with_limit'],
)
@pytest.mark.config(INSTANT_CASHBACK_ENABLED=True)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_calc_cashback_basic(
        web_cashback,
        order_archive_mock,
        order_id,
        cleared,
        payment_type,
        expected_cashback,
        expected_extra_payload,
):
    proc = copy.deepcopy(DEFAULT_PROC)
    proc.update({'_id': order_id})
    proc['payment_tech']['type'] = payment_type
    order_archive_mock.set_order_proc(proc)

    response = await web_cashback.calc_cashback.make_request(
        override_params={'order_id': order_id},
        override_data={'cleared': cleared},
    )
    assert response.status == 200

    response_data = await response.json()
    actual_cashback = decimal.Decimal(response_data['cashback'])
    assert actual_cashback == expected_cashback
    assert response_data['currency'] == 'RUB'
    assert response_data['payload'].pop('base_amount') == cleared
    assert response_data['payload'].pop('cashback_service') == 'yataxi'
    assert response_data['payload'] == expected_extra_payload


@pytest.mark.parametrize(
    'expected_status,expected_cashback',
    [
        pytest.param(
            200,
            '150',  # 300 * 0.5
            marks=[
                pytest.mark.config(
                    CASHBACK_FOR_CASH_ENABLED=True,
                    CASHBACK_CHECK_CASH_ORDERS=False,
                ),
            ],
            id='cashback-for-cash-enabled-new',
        ),
        pytest.param(
            200,
            '0',
            marks=[
                pytest.mark.config(
                    CASHBACK_FOR_CASH_ENABLED=False,
                    CASHBACK_CHECK_CASH_ORDERS=False,
                ),
            ],
            id='cashback-for-cash-disabled-new',
        ),
        pytest.param(
            409,
            '0',
            marks=pytest.mark.config(
                CASHBACK_FOR_CASH_ENABLED=False,
                CASHBACK_CHECK_CASH_ORDERS=True,
            ),
            id='cashback-for-cash-disabled-old',
        ),
        pytest.param(
            200,
            '150',
            marks=pytest.mark.config(
                CASHBACK_FOR_CASH_ENABLED=True,
                CASHBACK_CHECK_CASH_ORDERS=True,
            ),
            id='cashback-for-cash-enabled-old',
        ),
    ],
)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_calc_cashback_for_cash(
        web_cashback, order_archive_mock, expected_cashback, expected_status,
):
    proc = copy.deepcopy(DEFAULT_PROC)
    proc.update({'payment_tech': {'type': 'cash'}})
    order_archive_mock.set_order_proc(proc)

    response = await web_cashback.calc_cashback.make_request()
    assert response.status == expected_status

    if expected_status == 200:
        response_data = await response.json()
        assert response_data['cashback'] == expected_cashback
        assert response_data['currency'] == 'RUB'


@pytest.mark.parametrize(
    'expected_cashback',
    [
        pytest.param(
            '250',  # 500 * 0.5
            marks=[
                pytest.mark.config(
                    CASHBACK_RIDE_COST_FROM_DECOUPLING_ENABLED=True,
                ),
            ],
            id='cost-from-decoupling',
        ),
        pytest.param(
            '50',  # 100 * 0.5
            marks=[
                pytest.mark.config(
                    CASHBACK_RIDE_COST_FROM_DECOUPLING_ENABLED=False,
                ),
            ],
            id='cost-from-transactions',
        ),
    ],
)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_calc_cashback_for_corp(
        web_cashback, order_archive_mock, expected_cashback,
):
    proc = copy.deepcopy(DEFAULT_PROC)
    proc.update({'payment_tech': {'type': 'corp'}})
    proc['order']['decoupling'] = {
        'driver_price_info': {'fixed_price': 212, 'cost': 212},
        'success': True,
        'user_price_info': {'fixed_price': 500, 'cost': 500},
    }

    order_archive_mock.set_order_proc(proc)

    response = await web_cashback.calc_cashback.make_request()
    assert response.status == 200

    response_data = await response.json()
    assert response_data['cashback'] == expected_cashback
    assert response_data['currency'] == 'RUB'


@pytest.mark.config(INSTANT_CASHBACK_ENABLED=False)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_calc_cashback_for_cleared(web_cashback, order_archive_mock):
    order_archive_mock.set_order_proc(DEFAULT_PROC)

    response = await web_cashback.calc_cashback.make_request(
        override_data={'cleared': '0', 'held': '100'},
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data['cashback'] == '0'
    assert response_data['currency'] == 'RUB'


@pytest.mark.config(
    CASHBACK_SPONSPOR_STATIC_PAYLOAD={
        'possible_cashback': {
            'ticket': 'NEWSERVICE-1689',
            'campaign_name': 'changing_cashback_go',
        },
    },
)
@pytest.mark.parametrize(
    'order_id, cleared, expected_possible_cashback, '
    'expected_payload, is_possible_cashback',
    [
        (
            'order_id_with_marketing_cashback',
            '200',
            decimal.Decimal('20'),
            {
                'base_amount': '200',
                'cashback_service': 'yataxi',
                'order_id': 'order_id_with_marketing_cashback',
                'tariff_class': 'econom',
                'campaign_name': 'changing_cashback_go',
                'ticket': 'NEWSERVICE-1689',
            },
            True,
        ),
        (
            'order_id_with_marketing_cashback',
            '400',
            decimal.Decimal('40'),
            {
                'base_amount': '400',
                'cashback_service': 'yataxi',
                'order_id': 'order_id_with_marketing_cashback',
                'tariff_class': 'econom',
                'campaign_name': 'changing_cashback_go',
                'ticket': 'NEWSERVICE-1689',
            },
            True,
        ),
        (
            'order_id_with_marketing_cashback_with_limit',
            '400',
            decimal.Decimal('40'),
            {
                'base_amount': '400',
                'cashback_service': 'yataxi',
                'order_id': 'order_id_with_marketing_cashback_with_limit',
                'tariff_class': 'econom',
                'campaign_name': 'changing_cashback_go',
                'ticket': 'NEWSERVICE-1689',
            },
            True,
        ),
        (
            'order_id_with_marketing_cashback_with_limit',
            '1200',
            decimal.Decimal('100'),
            {
                'base_amount': '1200',
                'cashback_service': 'yataxi',
                'order_id': 'order_id_with_marketing_cashback_with_limit',
                'tariff_class': 'econom',
                'campaign_name': 'changing_cashback_go',
                'ticket': 'NEWSERVICE-1689',
            },
            True,
        ),
        ('order_id_with_marketing_cashback', '100', None, None, False),
    ],
)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_calc_cashback_possible_cashback(
        web_cashback,
        order_archive_mock,
        order_id,
        cleared,
        expected_possible_cashback,
        expected_payload,
        is_possible_cashback,
):
    proc = copy.deepcopy(DEFAULT_PROC)
    proc.update({'_id': order_id})
    proc.update(
        {
            'extra_data': {
                'cashback': {
                    'is_possible_cashback': is_possible_cashback,
                    'is_cashback': True,
                },
            },
        },
    )
    order_archive_mock.set_order_proc(proc)

    response = await web_cashback.calc_cashback.make_request(
        override_data={'cleared': cleared, 'held': '0'},
        override_params={'order_id': order_id},
    )
    assert response.status == 200

    response_data = await response.json()
    if is_possible_cashback:
        assert (
            decimal.Decimal(response_data['possible_cashback']['cashback'])
            == expected_possible_cashback
        )
        assert response_data['currency'] == 'RUB'
        assert (
            response_data['possible_cashback']['payload'] == expected_payload
        )
    else:
        assert response_data.get('possible_cashback', None) is None


@pytest.mark.parametrize(
    'currency, rounded', [('RUB', '251'), ('BYN', '251.5')],
)
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'BYN': {'__default__': 0.1},
        '__default__': {'__default__': 1},
    },
)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_calc_cashback_round(
        web_cashback, order_archive_mock, currency, rounded,
):
    order_archive_mock.set_order_proc(DEFAULT_PROC)

    response = await web_cashback.calc_cashback.make_request(
        override_data={'cleared': '503.1', 'held': '0', 'currency': currency},
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data['cashback'] == rounded
    assert response_data['currency'] == currency


@pytest.mark.parametrize(
    'currency, rounded', [('RUB', '252'), ('BYN', '251.6')],
)
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'BYN': {'__default__': 0.1},
        '__default__': {'__default__': 1},
    },
    MARKETING_CASHBACK_CEIL_ENABLED=True,
)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_calc_cashback_round_ceil(
        web_cashback, order_archive_mock, currency, rounded,
):
    order_archive_mock.set_order_proc(DEFAULT_PROC)

    response = await web_cashback.calc_cashback.make_request(
        override_data={'cleared': '503.1', 'held': '0', 'currency': currency},
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data['cashback'] == rounded
    assert response_data['currency'] == currency


@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_calc_cashback_rates_not_ready(web_cashback, order_archive_mock):
    order_id = 'order_id_15'
    proc = copy.deepcopy(DEFAULT_PROC)
    proc.update({'_id': order_id})
    order_archive_mock.set_order_proc(proc)

    response = await web_cashback.calc_cashback.make_request(
        override_params={'order_id': order_id},
    )
    assert response.status == 429


@pytest.mark.parametrize(
    'extra_metas,expected_campaign_name',
    [({}, None), ({'cashback_sponsor:mastercard': 1}, 'mastercard')],
)
@pytest.mark.config(CASHBACK_CAMPAIGN_NAME_ENABLED=True)
@pytest.mark.config(
    CASHBACK_SPONSPOR_STATIC_PAYLOAD={'mastercard': {'issuer': 'master'}},
)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_campaign_name(
        web_cashback, order_archive_mock, extra_metas, expected_campaign_name,
):
    proc = copy.deepcopy(DEFAULT_PROC)
    proc.setdefault('order', {}).setdefault('pricing_data', {}).setdefault(
        'user', {},
    ).setdefault('meta', {}).update(extra_metas)
    order_archive_mock.set_order_proc(proc)
    response = await web_cashback.calc_cashback.make_request(
        override_data={'cleared': '0', 'held': '100'},
    )
    assert response.status == 200

    response_data = await response.json()
    payload = response_data['payload']
    if expected_campaign_name:
        assert 'campaign_name' in payload
        assert payload == {
            'base_amount': '0',
            'campaign_name': expected_campaign_name,
            'cashback_service': 'yataxi',
            'issuer': 'master',
        }
    else:
        assert 'campaign_name' not in payload
