import pytest

from protocol import brands


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'child_tariff'],
    },
    APPLICATION_MAP_BRAND={
        '__default__': 'unknown',
        'android': 'yataxi',
        'uber_android': 'yauber',
        'yango_android': 'yango1',
        'yango_iphone': 'yango2',
    },
    BILLING_SERVICE_NAME_MAP_BY_BRAND={
        '__default__': 'unknown',
        'yataxi': 'card',
        'yango1': 'card',
        'yango2': 'yango',
        'yauber': 'uber',
    },
    PASSPORT_SCOPES_REQUIRED_MAP_BY_BRAND={'__default__': ['default:write']},
)
@pytest.mark.parametrize(
    'request_headers, expected_billing_type',
    [
        (brands.yataxi.android.headers, 'card'),
        (brands.yataxi.iphone.headers, 'unknown'),
        ({'User-Agent': 'unknown'}, 'unknown'),
        (brands.yauber.android.headers, 'uber'),
        (brands.yango.android.headers, 'card'),
        (brands.yango.iphone.headers, 'yango'),
    ],
)
@pytest.mark.parametrize(
    'endpoint,params',
    [
        ('3.0/launch', {}),
        (
            '3.0/order',
            {
                'payment': {'type': 'cash'},
                'parks': [],
                'id': '00000000000041111111111111111111',
                'service_level': 50,
                'route': [
                    {
                        'country': 'Россия',
                        'description': 'description',
                        'exact': True,
                        'fullname': 'fullname',
                        'geopoint': [37.588144, 55.733842],
                        'locality': 'locality',
                        'object_type': 'организация',
                        'oid': '1571474321',
                        'premisenumber': '1',
                        'short_text': 'short_text',
                        'thoroughfare': 'thoroughfare',
                        'type': 'organization',
                        'use_geopoint': True,
                    },
                ],
            },
        ),
        (
            '3.0/ordercommit',
            {
                'id': '00000000000041111111111111111111',
                'orderid': '1234567890',
            },
        ),
        ('3.0/paymentstatuses', {}),
        ('3.0/payorder', {}),
        ('3.0/routestats', {}),
    ],
)
def test_uber_terminal_selection(
        taxi_protocol,
        testpoint,
        mockserver,
        endpoint,
        params,
        dummy_feedback,
        mock_stq_agent,
        request_headers,
        expected_billing_type,
):
    state = {'service_type': None}

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {
            'uid': {'value': '123'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'default:write'},
            'phones': [{'attributes': {'102': '+71112223344'}, 'id': '1111'}],
        }

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surger(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.2,
                    'reason': 'pins_free',
                    'antisurge': False,
                },
            ],
        }

    @testpoint('BillingComponent::CreateBillingService')
    def update_service_type(data):
        state['service_type'] = data['service_type']

    taxi_protocol.post(
        endpoint, json=params, bearer='test_token', headers=request_headers,
    )
    assert state['service_type'] == expected_billing_type
