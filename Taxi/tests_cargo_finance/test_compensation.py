import copy
import decimal

import pytest


REQUEST = {
    'revision': 0,
    'is_service_complete': False,
    'client': {
        'compensation': {
            'sum': '1234.1234',
            'currency': 'RUB',
            'context': {
                'billing_product': {
                    'id': '100500_80781421_ride',
                    'name': 'ride',
                },
                'yandex_uid': 'yandex_uid',
                'customer_ip': 'some_ip',
                'corp_client_id': '35bf617cf19348e9a4f4a7064774fb8e',
                'invoice_due': '2021-07-01T10:50:00+00:00',
                'taxi_order_id': 'taxi_order_id',
                'taxi_alias_id': 'taxi_alias_id',
                'park_clid': 'park_clid',
                'park_dbid': 'park_dbid',
                'contractor_profile_id': 'contractor_profile_id',
                'taxi_order_due': '2021-07-01T10:45:00+00:00',
                'tariff_class': 'express',
                'nearest_zone': 'moscow',
                'city': 'Москва',
                'taxi_order_source': 'yandex',
                'acquiring_rate': '0.1234',
                'fiscal_receipt_info': {
                    'vat': 'nds_none',
                    'title': 'Услуги курьерской доставки',
                    'personal_tin_id': 'e7fc0c1b184a4a6bb56f8e0b3c344e8c',
                },
            },
        },
    },
    'taxi': {'taxi_order_id': 'test_order_id'},
}
DEBT_URI = (
    '/internal/cargo-finance/pay/order/transactions/debt?'
    'flow=claims&entity_id=test_id'
)
UPSERT_URI = (
    '/internal/cargo-finance/pay/order/transactions/upsert?'
    'flow=claims&entity_id=test_id'
)
RETRIEVE_URI = (
    '/internal/cargo-finance/pay/order/transactions/retrieve?'
    'flow=claims&entity_id=test_id'
)


@pytest.mark.parametrize('uri', [UPSERT_URI, DEBT_URI])
async def test_compensation_create(
        mockserver, taxi_cargo_finance, load_json, uri,
):
    invoice = load_json('empty_invoice.json')

    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def _mock_invoice_retrieve(request):
        if invoice.get('compensation') is None:
            return mockserver.make_response(
                json={'code': 'NOT_FOUND', 'message': 'Not found'}, status=404,
            )
        return mockserver.make_response(json=invoice, status=200)

    @mockserver.json_handler('/transactions-ng/v2/invoice/create')
    def _mock_invoice_create(request):
        return mockserver.make_response('{}', status=200)

    @mockserver.json_handler('/transactions-ng/v3/invoice/compensation/create')
    def _mock_compensation_create(request):
        gross = decimal.Decimal(request.json['gross_amount'])
        acquiring_rate = decimal.Decimal(request.json['acquiring_rate'])
        net = gross * (decimal.Decimal(1.0) - acquiring_rate)
        invoice['compensation'] = {
            'compensations': [
                {
                    'compensated': '2021-11-16T20:05:42.404000+03:00',
                    'external_payment_id': 'a7ff282a723a98a8924bc90524c6e91a',
                    'operation_id': request.json['operation_id'],
                    'status': 'compensation_success',
                    'refunds': [],
                    'sum': [
                        {
                            'amount': str(
                                net.quantize(decimal.Decimal('1.0000')),
                            ),
                            'item_id': 'ride',
                        },
                    ],
                    'terminal_id': '96013002',
                    'trust_payment_id': '6193e4d9b955d76fa886dd2f',
                },
            ],
            'operations': [
                {
                    'created': '2021-11-16T22:57:30.499000+03:00',
                    'id': request.json['operation_id'],
                    'status': 'done',
                    'sum_to_pay': [],
                },
            ],
            'version': 1,
        }
        return mockserver.make_response(
            json={'gross_amount': str(gross), 'net_amount': str(net)},
            status=200,
        )

    response = await taxi_cargo_finance.post(uri, json=REQUEST)
    assert response.status == 200
    assert response.json() == {
        'client': {
            'compensation': {'paid_sum': '1234.1234', 'is_finished': True},
        },
    }


@pytest.mark.parametrize('uri', [UPSERT_URI, DEBT_URI])
async def test_compensation_increase(
        mockserver, taxi_cargo_finance, load_json, uri,
):
    invoice = load_json('invoice_with_compensations.json')

    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def _mock_invoice_retrieve(request):
        return mockserver.make_response(json=invoice, status=200)

    @mockserver.json_handler('/transactions-ng/v3/invoice/compensation/create')
    def _mock_compensation_create(request):
        gross = decimal.Decimal(request.json['gross_amount'])
        acquiring_rate = decimal.Decimal(request.json['acquiring_rate'])
        net = gross * (decimal.Decimal(1.0) - acquiring_rate)
        compensations = invoice['compensation']['compensations']
        compensations.append(
            {
                'compensated': '2021-11-16T23:23:40.133000+03:00',
                'external_payment_id': '9965086423d23cf7d0556a1a930dd7f3',
                'operation_id': request.json['operation_id'],
                'refunds': [],
                'status': 'compensation_success',
                'sum': [
                    {
                        'amount': str(net.quantize(decimal.Decimal('1.0000'))),
                        'item_id': 'ride',
                    },
                ],
                'terminal_id': '96013002',
                'trust_payment_id': 'new_trust_payment_id',
            },
        )
        operations = invoice['compensation']['operations']
        operations.append(
            {
                'created': '2021-11-17T00:53:53.483000+03:00',
                'id': request.json['operation_id'],
                'status': 'done',
                'sum_to_pay': [],
            },
        )
        return mockserver.make_response(
            json={'gross_amount': str(gross), 'net_amount': str(net)},
            status=200,
        )

    response = await taxi_cargo_finance.post(uri, json=REQUEST)
    assert response.status == 200
    assert response.json() == {
        'client': {
            'compensation': {'paid_sum': '1234.1234', 'is_finished': True},
        },
    }
    assert (
        invoice['compensation']['compensations'][-1]['sum'][0]['amount']
        == '864.1234'
    )


@pytest.mark.parametrize('uri', [UPSERT_URI, DEBT_URI])
async def test_compensation_refund(
        mockserver, taxi_cargo_finance, load_json, uri,
):
    invoice = load_json('invoice_with_compensations.json')

    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def _mock_invoice_retrieve(request):
        return mockserver.make_response(json=invoice, status=200)

    @mockserver.json_handler('/transactions-ng/v3/invoice/compensation/refund')
    def _mock_compensation_refund(request):
        compensations = invoice['compensation']['compensations']
        for current in compensations:
            if current['trust_payment_id'] == request.json['trust_payment_id']:
                current['refunds'].append(
                    {
                        'external_payment_id': '61942803910d3981eabe506e',
                        'operation_id': request.json['operation_id'],
                        'refunded': '2021-11-17T00:52:18.860000+03:00',
                        'status': 'refund_success',
                        'sum': [
                            {
                                'amount': request.json['net_amount'],
                                'item_id': 'ride',
                            },
                        ],
                    },
                )
                break

        operations = invoice['compensation']['operations']
        operations.append(
            {
                'created': '2021-11-17T00:53:53.483000+03:00',
                'id': request.json['operation_id'],
                'status': 'done',
                'sum_to_pay': [],
            },
        )
        return mockserver.make_response(json={}, status=200)

    # refund part
    request = copy.deepcopy(REQUEST)
    request['client']['compensation']['sum'] = '220'
    response = await taxi_cargo_finance.post(uri, json=request)
    assert response.status == 200
    assert response.json() == {
        'client': {'compensation': {'paid_sum': '220', 'is_finished': True}},
    }
    compensations = invoice['compensation']['compensations']
    assert _mock_compensation_refund.times_called == 1
    assert compensations[1]['refunds'][-1]['sum'][0]['amount'] == '150'
    # refund all
    request['client']['compensation']['sum'] = '0'
    response = await taxi_cargo_finance.post(uri, json=request)
    assert response.status == 200
    assert response.json() == {
        'client': {'compensation': {'paid_sum': '0', 'is_finished': True}},
    }
    compensations = invoice['compensation']['compensations']
    assert _mock_compensation_refund.times_called == 3
    assert compensations[0]['refunds'][-1]['sum'][0]['amount'] == '120'
    assert compensations[1]['refunds'][-1]['sum'][0]['amount'] == '150'
    assert compensations[2]['refunds'][-1]['sum'][0]['amount'] == '100'


async def test_compensation_retrieve(
        mockserver, taxi_cargo_finance, load_json,
):
    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def _mock_invoice_retrieve(request):
        return mockserver.make_response(
            json=load_json('invoice_with_compensations.json'), status=200,
        )

    response = await taxi_cargo_finance.post(RETRIEVE_URI, json=REQUEST)
    assert response.status == 200
    assert response.json() == {
        'client': {'compensation': {'paid_sum': '370', 'is_finished': True}},
    }
