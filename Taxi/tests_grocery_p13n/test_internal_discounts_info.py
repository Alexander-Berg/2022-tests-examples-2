import copy

import pytest

from tests_grocery_p13n import depot
from tests_grocery_p13n import experiments
from tests_grocery_p13n import tests_headers

COMMON_INFORMER = {
    'hierarchy_name': 'menu_discounts',
    'informer': {
        'text': 'text',
        'picture': 'picture',
        'color': 'color',
        'modal': {
            'text': 'text',
            'picture': 'picture',
            'title': 'title',
            'buttons': [{'text': 'text', 'color': 'color', 'uri': 'uri'}],
        },
    },
}

HIERARCHY_NAMES = pytest.mark.experiments3(
    name='grocery_discounts_informers',
    consumers=['grocery-p13n/discounts'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True, 'hierarchy_names': ['menu_discounts']},
        },
    ],
    default_value={'enabled': False, 'hierarchy_names': []},
    is_config=True,
)


@HIERARCHY_NAMES
async def test_discount_informers(taxi_grocery_p13n, mockserver, grocery_tags):
    personal_phone_id = 'test_phone_id'
    tags = ['tag_1', 'tag_2']
    grocery_tags.add_tags(personal_phone_id=personal_phone_id, tags=tags)
    orders_counts = 2

    @mockserver.json_handler(
        'grocery-marketing/internal/v1/marketing/v2/tag/retrieve',
    )
    def _mock_marketing(request):
        return mockserver.make_response(
            json={'usage_count': orders_counts}, status=200,
        )

    @mockserver.json_handler('/grocery-discounts/v3/fetch-informers')
    def _mock_fetch_informers(request):
        assert request.json['tags'] == tags
        assert (
            request.json['orders_counts'][0]['orders_count'] == orders_counts
        )
        assert request.json['city'] == '213'
        return mockserver.make_response(
            json={'informers': [COMMON_INFORMER]}, status=200,
        )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discounts-info',
        headers={
            'X-YaTaxi-User': f'personal_phone_id={personal_phone_id}',
            'X-Yandex-UID': 'test_uid',
        },
        json={'offer_time': '2020-10-16T17:15:00Z', 'depot': depot.DEPOT},
    )
    assert response.status_code == 200
    assert response.json()['discount_informers'] == [COMMON_INFORMER]


@HIERARCHY_NAMES
@pytest.mark.parametrize(
    'grocery_discounts_surge_enabled',
    [
        pytest.param(
            False,
            marks=[experiments.GROCERY_DISCOUNTS_SURGE_DISABLED],
            id='grocery_discounts_surge_disabled',
        ),
        pytest.param(
            True,
            marks=[experiments.GROCERY_DISCOUNTS_SURGE_ENABLED],
            id='grocery_discounts_surge_enabled',
        ),
    ],
)
@pytest.mark.parametrize('has_surge', [True, False, None])
async def test_grocery_discounts_receives_surge(
        taxi_grocery_p13n,
        mockserver,
        has_surge,
        grocery_discounts_surge_enabled,
):
    @mockserver.json_handler('/grocery-discounts/v3/fetch-informers')
    def _mock_fetch_informers(request):
        if not grocery_discounts_surge_enabled or has_surge is None:
            assert 'has_surge' not in request.json
        else:
            assert request.json['has_surge'] == has_surge
        return mockserver.make_response(json={'informers': []}, status=200)

    request_body = {'offer_time': '2020-10-16T17:15:00Z', 'depot': depot.DEPOT}
    if has_surge is not None:
        request_body['has_surge'] = has_surge

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discounts-info',
        headers={'X-Yandex-UID': 'test_yuid'},
        json=request_body,
    )
    assert response.status_code == 200
    assert _mock_fetch_informers.times_called == 1


@HIERARCHY_NAMES
async def test_uid_and_phone_passed_to_discount_informers(
        taxi_grocery_p13n, mockserver,
):
    @mockserver.json_handler('/grocery-discounts/v3/fetch-informers')
    def mock_fetch_informers(request):
        assert (
            request.headers['X-Yandex-UID'] == tests_headers.HEADER_YANDEX_UID
        )
        assert (
            request.json['personal_phone_id']
            == tests_headers.PERSONAL_PHONE_ID
        )
        return {'informers': []}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discounts-info',
        headers=tests_headers.HEADERS,
        json={'offer_time': '2020-10-16T17:15:00Z', 'depot': depot.DEPOT},
    )
    assert response.status_code == 200
    assert mock_fetch_informers.times_called == 1


MENU_VALUE = {
    'menu': {'menu_value': {'value': '100', 'value_type': 'absolute'}},
}

CART_VALUE = {
    'cart': {
        'cart_value': {
            'value': [
                {
                    'from_cost': '0',
                    'discount': {'value': '100', 'value_type': 'absolute'},
                },
                {
                    'from_cost': '100',
                    'discount': {'value': '500', 'value_type': 'absolute'},
                },
            ],
        },
    },
}


@HIERARCHY_NAMES
@pytest.mark.parametrize('discount_value', [MENU_VALUE, CART_VALUE])
async def test_informer_discount_value(
        taxi_grocery_p13n, mockserver, discount_value,
):
    @mockserver.json_handler('/grocery-discounts/v3/fetch-informers')
    def _mock_fetch_informers(request):
        informer = copy.deepcopy(COMMON_INFORMER)
        informer['informer']['discount_value'] = {
            'money_value': discount_value,
        }
        return {'informers': [informer]}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discounts-info',
        headers=tests_headers.HEADERS,
        json={'offer_time': '2020-10-16T17:15:00Z', 'depot': depot.DEPOT},
    )
    assert response.status_code == 200
    assert response.json()['discount_informers'][0]['discount_value'] == {
        'discount_value': '100',
        'discount_value_type': 'absolute',
        'payment_type': 'money',
    }


@pytest.mark.parametrize(
    'hierarchy_names',
    [
        ['menu_discounts', 'cart_discounts', 'cart_cashback'],
        ['dynamic_discounts', 'markdown_discounts'],
        [],
    ],
)
async def test_request_hierarchy_names(
        taxi_grocery_p13n, mockserver, experiments3, hierarchy_names,
):

    experiments3.add_config(
        name='grocery_discounts_informers',
        consumers=['grocery-p13n/discounts'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': True, 'hierarchy_names': hierarchy_names},
            },
        ],
        default_value={'enabled': False, 'hierarchy_names': []},
    )

    @mockserver.json_handler('/grocery-discounts/v3/fetch-informers')
    def mock_fetch_informers(request):
        assert set(request.json['hierarchy_names']) == set(hierarchy_names)
        return {'informers': []}

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discounts-info',
        headers=tests_headers.HEADERS,
        json={'offer_time': '2020-10-16T17:15:00Z', 'depot': depot.DEPOT},
    )
    assert response.status_code == 200
    if hierarchy_names:
        assert mock_fetch_informers.times_called == 1
    else:
        assert mock_fetch_informers.times_called == 0
        assert 'discount_informers' not in response.json()


@HIERARCHY_NAMES
@pytest.mark.parametrize(
    'request_orders_count, antifraud_enabled, is_fraud',
    [
        pytest.param(
            None, False, True, marks=experiments.ANTIFRAUD_CHECK_DISABLED,
        ),
        pytest.param(
            None, True, False, marks=experiments.ANTIFRAUD_CHECK_ENABLED,
        ),
        pytest.param(
            None, True, True, marks=experiments.ANTIFRAUD_CHECK_ENABLED,
        ),
        pytest.param(1, True, True, marks=experiments.ANTIFRAUD_CHECK_ENABLED),
    ],
)
async def test_informers_with_antifraud_check(
        taxi_grocery_p13n,
        mockserver,
        antifraud,
        grocery_tags,
        request_orders_count,
        antifraud_enabled,
        is_fraud,
):
    lon = 30.0
    lat = 40.0
    user_agent = 'user-agent'
    city = 'city'
    street = 'street'
    house = 'house'
    flat = 'flat'
    comment = 'comment'
    orders_counts = 2

    @mockserver.json_handler(
        'grocery-marketing/internal/v1/marketing/v2/tag/retrieve',
    )
    def _mock_marketing(request):
        return mockserver.make_response(
            json={'usage_count': orders_counts}, status=200,
        )

    @mockserver.json_handler('/grocery-discounts/v3/fetch-informers')
    def _mock_fetch_informers(request):
        assert (
            request.json['orders_counts'][0]['orders_count']
            == request_orders_count
            or orders_counts
        )
        return mockserver.make_response(
            json={'informers': [COMMON_INFORMER]}, status=200,
        )

    antifraud.set_is_fraud(is_fraud)
    antifraud.check_discount_antifraud(
        user_id=tests_headers.HEADER_YANDEX_UID,
        user_id_service='passport',
        user_personal_phone_id=tests_headers.PERSONAL_PHONE_ID,
        user_agent=user_agent,
        application_type='android',
        service_name='grocery',
        short_address=f'{city}, {street} {house} {flat}',
        address_comment=comment,
        order_coordinates={'lat': lat, 'lon': lon},
        device_coordinates={'lat': lat, 'lon': lon},
        payment_method_id='1',
        payment_method='card',
        user_device_id=tests_headers.APPMETRICA_DEVICE_ID,
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discounts-info',
        headers=tests_headers.HEADERS,
        json={
            'offer_time': '2020-10-16T17:15:00Z',
            'depot': depot.DEPOT,
            'payment_method': {'type': 'card', 'id': '1'},
            'user_agent': user_agent,
            'position': {'location': [lon, lat]},
            'additional_data': {
                'device_coordinates': {'location': [lon, lat]},
                'city': city,
                'street': street,
                'house': house,
                'flat': flat,
                'comment': comment,
            },
            'orders_count': request_orders_count,
        },
    )
    assert response.status_code == 200
    assert _mock_fetch_informers.times_called == 1
    assert antifraud.times_discount_antifraud_called() == int(
        antifraud_enabled and not request_orders_count,
    )


@HIERARCHY_NAMES
@experiments.GROCERY_DISCOUNTS_LABELS
@pytest.mark.config(
    GROCERY_DISCOUNTS_LABELS_EXPERIMENTS=[
        {'name': 'grocery_discounts_labels', 'experiment_type': 'config'},
    ],
)
@pytest.mark.parametrize('has_parcels', [True, False, None])
async def test_discount_labels_by_exp(
        taxi_grocery_p13n, mockserver, experiments3, has_parcels,
):
    @mockserver.json_handler('/grocery-discounts/v3/fetch-informers')
    def _mock_fetch_informers(request):
        if has_parcels is None or not has_parcels:
            assert 'has_parcels_lable' not in request.json['experiments']
        else:
            assert request.json['experiments'] == ['has_parcels_label']
        return mockserver.make_response(json={'informers': []}, status=200)

    request_body = {'offer_time': '2020-10-16T17:15:00Z', 'depot': depot.DEPOT}

    if has_parcels is not None:
        request_body['has_parcels'] = has_parcels

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discounts-info',
        headers={'X-Yandex-UID': 'test_yuid'},
        json=request_body,
    )
    assert response.status_code == 200
    assert _mock_fetch_informers.times_called == 1


@HIERARCHY_NAMES
async def test_discounts_info_ya_plus_flag(taxi_grocery_p13n, mockserver):
    @mockserver.json_handler('/grocery-discounts/v3/fetch-informers')
    def _mock_fetch_informers(request):
        assert request.json['has_yaplus']
        return mockserver.make_response(json={'informers': []}, status=200)

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discounts-info',
        headers={'X-YaTaxi-Pass-Flags': 'ya-plus'},
        json={'offer_time': '2020-10-16T17:15:00Z', 'depot': depot.DEPOT},
    )
    assert response.status_code == 200
    assert _mock_fetch_informers.times_called == 1
