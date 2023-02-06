# type: ignore[dict-item]

import pytest

LATEST_EATS_FEEDBACK = '/eats-feedback/v1/latest'
LATEST_API_V1 = '/api/v1/orders/feedback/latest'

MOCK_NOW = '2021-08-10T13:00:00+00:00'


def build_experiment(eater_id):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eats_feedback_handle_latest',
        consumers=['eats_feedback/eaters'],
        clauses=[
            {
                'enabled': True,
                'extension_method': 'replace',
                'value': {'enabled': True},
                'predicate': {
                    'type': 'in_set',
                    'init': {
                        'set': [eater_id],
                        'arg_name': 'eater_id',
                        'set_elem_type': 'string',
                    },
                },
            },
        ],
        default_value={'enabled': False},
    )


TEST_MOCK_RESPONSE = {'test': 'value'}


@pytest.mark.parametrize(
    [
        'url',
        'header',
        'expected_mock_calls',
        'expected_status',
        'expected_response',
    ],
    (
        pytest.param(
            LATEST_EATS_FEEDBACK,
            'user_id=eater1',
            0,
            204,
            None,
            marks=build_experiment('eater1'),
        ),
        pytest.param(
            LATEST_API_V1,
            'user_id=eater1',
            0,
            204,
            None,
            marks=build_experiment('eater1'),
        ),
        pytest.param(
            LATEST_EATS_FEEDBACK,
            'user_id=eater2',
            1,
            200,
            TEST_MOCK_RESPONSE,
            marks=build_experiment('eater1'),
        ),
        pytest.param(
            LATEST_API_V1,
            'user_id=eater2',
            1,
            200,
            TEST_MOCK_RESPONSE,
            marks=build_experiment('eater1'),
        ),
    ),
)
async def test_latest_experiment(
        taxi_eats_feedback,
        mockserver,
        url,
        header,
        expected_mock_calls,
        expected_status,
        expected_response,
):
    @mockserver.json_handler(
        '/eats-core-feedback/api/v1/orders/feedback/latest',
    )
    def _mock_core_latest(request):
        return mockserver.make_response(status=200, json=TEST_MOCK_RESPONSE)

    response = await taxi_eats_feedback.get(
        url, headers={'X-Eats-User': header}, params={},
    )

    assert _mock_core_latest.times_called == expected_mock_calls

    assert response.status_code == expected_status
    if expected_response is not None:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    ['url'], (pytest.param(LATEST_EATS_FEEDBACK), pytest.param(LATEST_API_V1)),
)
async def test_latest_no_auth(taxi_eats_feedback, mockserver, url):
    response = await taxi_eats_feedback.get(url, headers={}, params={})
    assert response.status_code == 401


EXPECTED_RESPONSE_GREEN_FLOW = {
    'address': {
        'building': None,
        'city': '',
        'comment': None,
        'doorcode': None,
        'entrance': None,
        'floor': None,
        'full': None,
        'house': '',
        'location': {'latitude': 0.0, 'longitude': 0.0},
        'office': None,
        'plot': None,
        'short': '',
        'street': '',
    },
    'awaiting_payment': False,
    'can_contact_us': False,
    'cancelable': False,
    'cart': {
        'available_time_picker': [],
        'country': None,
        'delivery_date_time': None,
        'delivery_fee': 0,
        'delivery_fee_rational': '',
        'delivery_time': None,
        'discount': 0,
        'discount_promo': 0,
        'discount_promo_rational': '',
        'discount_rational': '',
        'items': [],
        'place': {
            'available_payment_methods': [],
            'is_store': False,
            'market': False,
            'name': '',
            'slug': '',
        },
        'place_slug': '',
        'promo_items': [],
        'promo_notification': None,
        'promocode': None,
        'promos': [],
        'requirements': {
            'next_delivery_threshold': None,
            'sum_to_free_delivery': None,
            'sum_to_min_order': None,
        },
        'subtotal': 0,
        'subtotal_rational': '',
        'surge': None,
        'total': 1000,
        'total_rational': '1000.50',
        'updated_at': '',
    },
    'client_app': 'native',
    'comment': None,
    'courier': None,
    'created_at': '2021-08-10 13:00:00',
    'currency': {'code': 'RUB', 'sign': '₽'},
    'feedback_status': 'show',
    'has_feedback': False,
    'id': '210810-000000',
    'order_nr': '210810-000000',
    'payment_status': {'id': 0, 'title': '', 'type': 0},
    'persons_quantity': 0,
    'phone_number': '',
    'place': {
        'address': {
            'building': None,
            'city': '',
            'comment': None,
            'doorcode': None,
            'entrance': None,
            'floor': None,
            'full': None,
            'house': '',
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'office': None,
            'plot': None,
            'short': '',
            'street': '',
        },
        'business_hours': [],
        'business_hours_sliced': [],
        'categories': [],
        'delivery_conditions': None,
        'delivery_cost_thresholds': [],
        'description': None,
        'enabled': False,
        'footer_description': '',
        'id': 0,
        'is_new': False,
        'is_promo_available': False,
        'items': [],
        'market': False,
        'minimal_order_price': 0,
        'name': '',
        'picture': '',
        'price_category': {'id': 0, 'name': '', 'value': 0.0},
        'rating': 0.0,
        'resized_picture': '',
        'slug': '',
        'zone': {'is_hole': False, 'points': []},
    },
    'service': 'eats',
    'shipping_type': 'delivery',
    'status': {'date': None, 'id': 0, 'title': ''},
    'without_callback': False,
}


REVISIONS_MOCK_RESPONSE_GREENFLOW = {
    'items': [
        {
            'order_nr': '210810-000000',
            'revision': {
                'number': 1,
                'costs': {
                    'type': 'costs',
                    'cost_for_customer': '1000.50',
                    'cost_for_place': '1000.50',
                    'items_cost': '1000.50',
                    'delivery_cost': '0.00',
                    'assembly_cost': '0.00',
                },
                'items': {'type': 'unfetched_object'},
                'promocode': {'type': 'unfetched_object'},
                'discounts': {'type': 'unfetched_object'},
                'created_at': '2021-08-10T13:00:00+03:00',
                'delivery_date': '2021-08-10T15:00:00+03:00',
            },
            'changes': {'type': 'unfetched_object'},
            'currency_code': 'RUB',
            'payment_method': 'post_payment_cash',
        },
    ],
}


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eats_feedback', files=['latest.sql'])
@build_experiment('eater1')
@pytest.mark.parametrize(
    ['url'], (pytest.param(LATEST_EATS_FEEDBACK), pytest.param(LATEST_API_V1)),
)
async def test_latest_green_flow(taxi_eats_feedback, mockserver, url):
    @mockserver.json_handler('/eats-checkout/orders/fetch-revisions')
    def _mock_core_revisions(request):
        return mockserver.make_response(
            status=200, json=REVISIONS_MOCK_RESPONSE_GREENFLOW,
        )

    response = await taxi_eats_feedback.get(
        url, headers={'X-Eats-User': 'user_id=eater1'}, params={},
    )

    assert _mock_core_revisions.times_called == 1

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE_GREEN_FLOW
