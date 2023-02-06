import copy
import decimal

import pytest

from taxi.util import dates as dates_utils

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(TVM_RULES=[{'src': 'cashback', 'dst': 'archive-api'}]),
]

DEFAULT_ORDER_ID = 'order_id_default'
DEFAULT_TARIFF_CLASS = 'econom'


DEFAULT_PROC = {
    '_id': DEFAULT_ORDER_ID,
    'commit_state': 'done',
    'status': 'finished',
    'created': dates_utils.parse_timestring(
        '2020-02-05T10:05:50.508000Z', timezone='UTC',
    ),
    'order': {
        'user_uid': 'yandex_uid_66',
        'taxi_status': 'complete',
        'performer': {
            'tariff': {'class': DEFAULT_TARIFF_CLASS},
            'taxi_alias': {'id': 'alias_id'},
        },
        'nz': 'moscow',
        'cost': '300',
        'pricing_data': {
            'currency': {'name': 'RUB'},
            'user': {'data': {'country_code2': 'RU'}, 'meta': {}},
        },
    },
    'extra_data': {'cashback': {'is_cashback': True}},
    'payment_tech': {'type': 'card'},
}
DEFAULT_CLEARED = [
    {
        'payment_type': 'card',
        'items': [
            {'item_id': 'ride', 'amount': '100'},
            {'item_id': 'cashback', 'amount': '100'},
        ],
    },
    {
        'payment_type': 'personal_wallet',
        'items': [{'item_id': 'ride', 'amount': '100'}],
    },
]
DEFAULT_SERVICE_CASHBACK_RESP = {
    'amount': '50',
    'payload': {'base_amount': '100', 'cashback_service': 'yataxi'},
}
DEFAULT_CASHBACK_RESP = {
    'amount': '100',
    'payload': {
        'alias_id': 'alias_id',
        'base_amount': '100',
        'cashback_service': 'yataxi',
        'country': 'RU',
        'currency': 'RUB',
        'oebs_mvp_id': 'MSKc',
        'order_id': 'order_id_with_limit',
        'payment_type': 'card',
        'tariff_class': 'econom',
    },
}


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        CASHBACK_SERVICES={
            'yataxi': {
                'scenario': 'internal_service',
                'configuration': {
                    'transactions': 'yataxi',
                    'url': '$mockserver/cashback/get',
                    'tvm_name': 'taxi',
                    'payment_methods_blacklist': ['personal_wallet'],
                    'cashback_item_ids': ['ride'],
                    'marketing_cashback_item_ids': ['ride', 'cashback'],
                    'some_extra_field': True,
                },
            },
        },
        CASHBACK_PROC_COUNTRY_CODE2_REQUIRED_SINCE={
            'created': '2020-09-05T00:00:00',
            'enabled': True,
        },
    ),
]


def make_cashback_response(
        amount=None,
        order_id=None,
        payment_type=None,
        default_response=None,
        base_amount=None,
) -> dict:
    if default_response is None:
        default_response = DEFAULT_CASHBACK_RESP
    result = copy.deepcopy(default_response)
    payload = result.get('payload', {})

    if amount:
        result['amount'] = amount
    if order_id:
        payload['order_id'] = order_id
    if payment_type:
        payload['payment_type'] = payment_type
    if base_amount:
        payload['base_amount'] = base_amount

    result['payload'] = payload
    return result


@pytest.mark.parametrize(
    'order_id, payment_type',
    [
        ('order_id_default', 'card'),
        ('order_id_default', 'corp'),
        ('order_id_with_limit', 'card'),
        ('order_id_with_limit', 'corp'),
    ],
    ids=[
        'basic_cashback_card',
        'basic_cashback_corp',
        'basic_cashback_with_limit_card',
        'basic_cashback_with_limit_corp',
    ],
)
@pytest.mark.config(INSTANT_CASHBACK_ENABLED=True)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_calc_cashback_basic(
        web_cashback,
        order_archive_mock,
        order_id,
        payment_type,
        mock_taxi_agglomerations,
):
    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def _mock_oebs_mvp(request):
        mvp_id_by_zone = {'moscow': 'MSKc'}
        request_zone = request.query['tariff_zone']

        return {'oebs_mvp_id': mvp_id_by_zone[request_zone]}

    proc = copy.deepcopy(DEFAULT_PROC)
    proc.update({'_id': order_id})
    proc['payment_tech']['type'] = payment_type
    proc['order']['pricing_data']['user']['data'] = {}
    order_archive_mock.set_order_proc(proc)

    cleared = copy.deepcopy(DEFAULT_CLEARED)
    cleared[0]['payment_type'] = payment_type

    response = await web_cashback.v2_calc_cashback.make_request(
        override_data={'order_id': order_id, 'cleared': cleared},
    )
    assert response.status == 200

    response_data = await response.json()

    service_cashback_amount = None
    if order_id == 'order_id_with_limit':
        service_cashback_amount = '40'
    expected_cashback = {
        'service': make_cashback_response(
            payment_type=payment_type if payment_type == 'corp' else None,
            amount=service_cashback_amount,
            default_response=DEFAULT_SERVICE_CASHBACK_RESP,
        ),
        'user': make_cashback_response(
            payment_type=payment_type, order_id=order_id,
        ),
    }

    assert expected_cashback == response_data['cashback_by_sources']


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
        web_cashback,
        order_archive_mock,
        expected_cashback,
        expected_status,
        mock_taxi_agglomerations,
):
    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def _mock_oebs_mvp(request):
        mvp_id_by_zone = {'moscow': 'MSKc'}
        request_zone = request.query['tariff_zone']

        return {'oebs_mvp_id': mvp_id_by_zone[request_zone]}

    proc = copy.deepcopy(DEFAULT_PROC)
    proc.update({'payment_tech': {'type': 'cash'}})
    order_archive_mock.set_order_proc(proc)

    response = await web_cashback.v2_calc_cashback.make_request(
        override_data={'order_id': 'order_id_default'},
    )
    assert response.status == expected_status

    base_amount = '300'
    if expected_cashback == '0' and expected_status == 200:
        base_amount = '0'
    expected_cashback = {
        'service': make_cashback_response(
            amount=expected_cashback,
            default_response=DEFAULT_SERVICE_CASHBACK_RESP,
            base_amount=base_amount,
        ),
        'user': make_cashback_response(
            payment_type='cash',
            order_id='order_id_default',
            amount='0',
            base_amount=base_amount,
        ),
    }

    if expected_status == 200:
        response_data = await response.json()
        assert response_data['cashback_by_sources'] == expected_cashback


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
        web_cashback,
        order_archive_mock,
        expected_cashback,
        mock_taxi_agglomerations,
):
    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def _mock_oebs_mvp(request):
        mvp_id_by_zone = {'moscow': 'MSKc'}
        request_zone = request.query['tariff_zone']

        return {'oebs_mvp_id': mvp_id_by_zone[request_zone]}

    proc = copy.deepcopy(DEFAULT_PROC)
    proc.update({'payment_tech': {'type': 'corp'}})
    proc['order']['decoupling'] = {
        'driver_price_info': {'fixed_price': 212, 'cost': 212},
        'success': True,
        'user_price_info': {'fixed_price': 500, 'cost': 500},
    }

    order_archive_mock.set_order_proc(proc)

    response = await web_cashback.v2_calc_cashback.make_request(
        override_data={'order_id': 'order_id_default'},
    )
    assert response.status == 200

    response_data = await response.json()
    assert (
        response_data['cashback_by_sources']['service']['amount']
        == expected_cashback
    )
    assert response_data['cashback_by_sources']['user']['amount'] == '0'


@pytest.mark.config(INSTANT_CASHBACK_ENABLED=False)
@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_calc_cashback_for_cleared(
        web_cashback, order_archive_mock, mock_taxi_agglomerations,
):
    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def _mock_oebs_mvp(request):
        mvp_id_by_zone = {'moscow': 'MSKc'}
        request_zone = request.query['tariff_zone']

        return {'oebs_mvp_id': mvp_id_by_zone[request_zone]}

    order_archive_mock.set_order_proc(DEFAULT_PROC)

    response = await web_cashback.v2_calc_cashback.make_request(
        override_data={
            'cleared': [],
            'held': [
                {
                    'payment_type': 'card',
                    'items': [{'item_id': 'ride', 'amount': '100'}],
                },
            ],
            'order_id': 'order_id_default',
        },
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data['cashback_by_sources']['service']['amount'] == '0'
    assert response_data['cashback_by_sources']['user']['amount'] == '0'


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
        web_cashback,
        order_archive_mock,
        currency,
        rounded,
        mock_taxi_agglomerations,
):
    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def _mock_oebs_mvp(request):
        mvp_id_by_zone = {'moscow': 'MSKc'}
        request_zone = request.query['tariff_zone']

        return {'oebs_mvp_id': mvp_id_by_zone[request_zone]}

    order_archive_mock.set_order_proc(DEFAULT_PROC)

    response = await web_cashback.v2_calc_cashback.make_request(
        override_data={
            'cleared': [
                {
                    'payment_type': 'card',
                    'items': [{'item_id': 'ride', 'amount': '503.1'}],
                },
            ],
            'currency': currency,
            'order_id': 'order_id_default',
        },
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data['cashback_by_sources']['service']['amount'] == rounded
    assert response_data['cashback_by_sources']['user']['amount'] == '0'


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
        web_cashback,
        order_archive_mock,
        currency,
        rounded,
        mock_taxi_agglomerations,
):
    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def _mock_oebs_mvp(request):
        mvp_id_by_zone = {'moscow': 'MSKc'}
        request_zone = request.query['tariff_zone']

        return {'oebs_mvp_id': mvp_id_by_zone[request_zone]}

    order_archive_mock.set_order_proc(DEFAULT_PROC)

    response = await web_cashback.v2_calc_cashback.make_request(
        override_data={
            'cleared': [
                {
                    'payment_type': 'card',
                    'items': [{'item_id': 'ride', 'amount': '503.1'}],
                },
            ],
            'currency': currency,
            'order_id': 'order_id_default',
        },
    )
    assert response.status == 200

    response_data = await response.json()
    assert response_data['cashback_by_sources']['service']['amount'] == rounded
    assert response_data['cashback_by_sources']['user']['amount'] == '0'


@pytest.mark.pgsql('cashback', files=['basic_cashback_with_service.sql'])
async def test_calc_cashback_rates_not_ready(web_cashback, order_archive_mock):
    order_id = 'order_id_15'
    proc = copy.deepcopy(DEFAULT_PROC)
    proc.update({'_id': order_id})
    order_archive_mock.set_order_proc(proc)

    response = await web_cashback.v2_calc_cashback.make_request(
        override_data={'order_id': order_id},
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
        web_cashback,
        order_archive_mock,
        extra_metas,
        expected_campaign_name,
        mock_taxi_agglomerations,
):
    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def _mock_oebs_mvp(request):
        mvp_id_by_zone = {'moscow': 'MSKc'}
        request_zone = request.query['tariff_zone']

        return {'oebs_mvp_id': mvp_id_by_zone[request_zone]}

    proc = copy.deepcopy(DEFAULT_PROC)
    proc.setdefault('order', {}).setdefault('pricing_data', {}).setdefault(
        'user', {},
    ).setdefault('meta', {}).update(extra_metas)
    order_archive_mock.set_order_proc(proc)
    response = await web_cashback.v2_calc_cashback.make_request(
        override_data={
            'cleared': [],
            'held': [
                {
                    'payment_type': 'card',
                    'items': [{'item_id': 'ride', 'amount': '100'}],
                },
            ],
            'order_id': 'order_id_default',
        },
    )
    assert response.status == 200

    response_data = await response.json()
    payload = response_data['cashback_by_sources']['service']['payload']
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
            decimal.Decimal('40'),
            {
                'base_amount': '200',
                'cashback_service': 'yataxi',
                'order_id': 'order_id_with_marketing_cashback',
                'alias_id': 'alias_id',
                'country': 'RU',
                'currency': 'RUB',
                'payment_type': 'card',
                'oebs_mvp_id': 'MSKc',
                'tariff_class': 'econom',
                'campaign_name': 'changing_cashback_go',
                'ticket': 'NEWSERVICE-1689',
            },
            True,
        ),
        (
            'order_id_with_marketing_cashback',
            '400',
            decimal.Decimal('80'),
            {
                'base_amount': '400',
                'cashback_service': 'yataxi',
                'order_id': 'order_id_with_marketing_cashback',
                'alias_id': 'alias_id',
                'country': 'RU',
                'currency': 'RUB',
                'payment_type': 'card',
                'oebs_mvp_id': 'MSKc',
                'tariff_class': 'econom',
                'campaign_name': 'changing_cashback_go',
                'ticket': 'NEWSERVICE-1689',
            },
            True,
        ),
        (
            'order_id_with_marketing_cashback_with_limit',
            '400',
            decimal.Decimal('80'),
            {
                'base_amount': '400',
                'cashback_service': 'yataxi',
                'order_id': 'order_id_with_marketing_cashback_with_limit',
                'alias_id': 'alias_id',
                'country': 'RU',
                'currency': 'RUB',
                'payment_type': 'card',
                'oebs_mvp_id': 'MSKc',
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
                'alias_id': 'alias_id',
                'country': 'RU',
                'currency': 'RUB',
                'payment_type': 'card',
                'oebs_mvp_id': 'MSKc',
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
        mock_taxi_agglomerations,
):
    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def _mock_oebs_mvp(request):
        mvp_id_by_zone = {'moscow': 'MSKc'}
        request_zone = request.query['tariff_zone']

        return {'oebs_mvp_id': mvp_id_by_zone[request_zone]}

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

    response = await web_cashback.v2_calc_cashback.make_request(
        override_data={
            'cleared': [
                {
                    'payment_type': 'card',
                    'items': [
                        {'item_id': 'ride', 'amount': cleared},
                        {'item_id': 'cashback', 'amount': cleared},
                    ],
                },
            ],
            'held': [],
            'order_id': order_id,
        },
    )
    assert response.status == 200

    response_data = await response.json()
    if is_possible_cashback:
        assert (
            decimal.Decimal(
                response_data['cashback_by_sources']['possible_cashback'][
                    'amount'
                ],
            )
            == expected_possible_cashback
        )
        assert (
            response_data['cashback_by_sources']['possible_cashback'][
                'payload'
            ]
            == expected_payload
        )
    else:
        assert (
            response_data['cashback_by_sources'].get('possible_cashback', None)
            is None
        )
