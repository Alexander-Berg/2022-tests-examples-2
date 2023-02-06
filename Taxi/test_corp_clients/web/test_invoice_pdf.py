# pylint: disable=redefined-outer-name
import pytest

GET_ORDERS_INFO_DEF = [
    {'ServiceID': 650, 'ServiceOrderID': 'service_order_id', 'IsGroupRoot': 1},
    {'ServiceID': 1171, 'ServiceOrderID': 'tanker_service_order_id'},
]

GET_ORDERS_INFO_103 = [
    {
        'ServiceID': 1181,
        'ServiceOrderID': 'service_order_id',
        'IsGroupRoot': False,
    },
    {
        'ServiceID': 1183,
        'ServiceOrderID': 'nowat_order_id',
        'IsGroupRoot': False,
    },
]


@pytest.fixture
def get_orders_info_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.get_orders_info')
    async def _get_orders_info(contract_id, **kwargs):
        return (
            GET_ORDERS_INFO_DEF if contract_id != 103 else GET_ORDERS_INFO_103
        )


@pytest.fixture
def get_request_choices_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.get_request_choices')
    async def _get_request_choices(query):
        return {
            'request': {'id': '3833714020', 'client_id': 35822459},
            'persons_parent': {
                'class_id': 35822459,
                'is_agency': 0,
                'id': 35822459,
                'agency_id': None,
                'name': 'БУЛКА',
            },
            'pcp_list': [
                {
                    'person': {
                        'region_id': 225,
                        'name': 'БУЛКА',
                        'resident': 1,
                        'type': 'ur',
                        'id': 4698705,
                        'legal_entity': 1,
                    },
                    'contract': {
                        'person_id': 4698705,
                        'external_id': '72640/17',
                        'id': 301324,
                        'client_id': 35822459,
                    },
                    'paysyses': [
                        {
                            'name': 'Банк для юр.лиц, RUB, резидент, Россия',
                            'payment_method_code': 'bank',
                            'resident': 1,
                            'legal_entity': 1,
                            'currency': 'RUB',
                            'payment_method': {
                                'cc': 'bank',
                                'id': 1001,
                                'name': 'Bank Payment',
                            },
                            'payment_limit': None,
                            'paysys_group': 'default',
                            'disabled_reasons': [],
                            'id': 1301003,
                            'cc': 'ur',
                            'region_id': 225,
                        },
                        {
                            'name': 'Банковская карта RUB, резидент, Россия',
                            'payment_method_code': 'card',
                            'resident': 1,
                            'legal_entity': 1,
                            'currency': 'RUB',
                            'payment_method': {
                                'cc': 'card',
                                'id': 1101,
                                'name': 'Credit Card',
                            },
                            'payment_limit': '299999.99',
                            'paysys_group': 'default',
                            'disabled_reasons': [],
                            'id': 1301033,
                            'cc': 'cc_ur',
                            'region_id': 225,
                        },
                    ],
                },
            ],
            'paysys_list': [
                {
                    'cc': 'ur',
                    'id': 1301003,
                    'name': 'Банк для юр.лиц, RUB, резидент, Россия',
                },
                {
                    'cc': 'cc_ur',
                    'id': 1301033,
                    'name': (
                        'Банковская карта для юр.лиц, RUB, резидент, Россия'
                    ),
                },
            ],
        }


@pytest.fixture
def create_invoice_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.create_invoice')
    async def _create_invoice(operator_uid, invoice_params):
        return 123456


@pytest.mark.parametrize(
    'contract_id', [pytest.param(101), pytest.param(102), pytest.param(103)],
)
async def test_invoice_post(
        web_app_client,
        load_json,
        contract_id,
        patch,
        get_orders_info_mock,
        get_request_choices_mock,
        create_invoice_mock,
        mock_ext_balance_invoice_pdf,
):
    @patch('taxi.clients.billing_v2.BalanceClient.create_request2')
    async def _create_request2(
            operator_uid, client_id, billing_order, optional_args,
    ):
        assert client_id == '100001'
        expected = (
            {
                'Qty': '1000',
                'ServiceOrderID': 'service_order_id',
                'ServiceID': 650,
            }
            if contract_id != 103
            else {
                'Qty': '1000',
                'ServiceOrderID': 'nowat_order_id',
                'ServiceID': 1183,
            }
        )

        assert billing_order == [expected]
        return {'RequestID': 'request_id'}

    response = await web_app_client.post(
        '/v1/invoice',
        params={'client_id': 'client_id_1'},
        json={'contract_id': contract_id, 'value': '1000'},
    )

    assert response.status == 200
    assert (
        response.headers['X-Accel-Redirect']
        == '/proxy-mds/balance/invoices_d7.pdf'
    )
    assert (
        response.headers['Content-Disposition']
        == 'attachment; filename="Б-1593066-2.pdf"'
    )
