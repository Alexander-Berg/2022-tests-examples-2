import json

import pytest


@pytest.fixture
def routestats_local_server(
        mockserver, request, load_json, surge_values, unavailable_classes,
):
    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        retval = {}
        retval = load_json('driver_eta.json')
        data = json.loads(request.get_data())

        to_remove = set()
        for c in retval['classes']:
            if c not in data['classes']:
                to_remove.add(c)

        for c in to_remove:
            retval['classes'].pop(c)

        for c in unavailable_classes:
            if c not in retval['classes']:
                continue

            resp_class = retval['classes'][c]
            if 'estimated_distance' in resp_class:
                resp_class.pop('estimated_distance')
            if 'estimated_time' in resp_class:
                resp_class.pop('estimated_time')
            if 'candidates' in resp_class:
                resp_class.pop('candidates')
            resp_class['found'] = False

        assert len(retval['classes']) == len(data['classes'])
        return retval


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ROUTESTATS_PRICE_PROMO_SUGGEST_CLASSES={
        'econom': ['business', 'comfortplus'],
        'business': ['comfortplus'],
    },
)
@pytest.mark.user_experiments('fixed_price', 'routestats_fixed_price_time')
@pytest.mark.parametrize(
    'surge_values, is_cheaper_message, brandings, '
    'cheaper_class, unavailable_classes',
    [
        (
            {'econom': 2, 'business': 1, 'comfortplus': 1},
            'Try Comfort cheaper than Economy',
            'brandings_comfort.json',
            'business',
            [],
        ),
        (
            {'econom': 2, 'business': 1, 'comfortplus': 0.853},
            'Try Comfort+ cheaper than Economy',
            'brandings_comfortplus.json',
            'comfortplus',
            [],
        ),
        # comfortplus is_cheaper , although business is cheapest, but it
        # has no drivers found
        (
            {'econom': 2, 'business': 0.1, 'comfortplus': 0.853},
            'Try Comfort+ cheaper than Economy',
            'brandings_comfortplus.json',
            'comfortplus',
            ['business'],
        ),
    ],
)
def test_price_promo_has_cheaper_tariff(
        local_services_base,
        taxi_protocol,
        pricing_data_preparer,
        routestats_local_server,
        load_json,
        now,
        surge_values,
        is_cheaper_message,
        brandings,
        cheaper_class,
        unavailable_classes,
):
    base_prices = {
        'econom': 122,
        'comfort': 200,
        'comfortplus': 117,
        'business': 100,
    }

    for cls, price in base_prices.items():
        sv = surge_values.get(cls) or 1
        pricing_data_preparer.set_user_surge(sv, category=cls)
        pricing_data_preparer.set_cost(
            user_cost=price * sv, driver_cost=price * sv, category=cls,
        )

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_json = response.json()

    for service_level in response_json['service_levels']:
        sl = service_level
        if sl['class'] == 'econom':
            assert sl.get('brandings') == load_json(brandings)
        elif sl['class'] == cheaper_class:
            assert sl['is_cheaper']
            assert sl['is_cheaper_message'] == is_cheaper_message
        else:
            assert 'is_cheaper' not in sl


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ROUTESTATS_PRICE_PROMO_SUGGEST_CLASSES={
        'econom': ['business', 'comfortplus'],
        'business': ['comfortplus'],
    },
)
@pytest.mark.user_experiments('fixed_price', 'routestats_fixed_price_time')
@pytest.mark.parametrize(
    'surge_values, is_cheaper_message, brandings, '
    'cheaper_class, unavailable_classes',
    [
        ({'econom': 2, 'business': 2, 'comfortplus': 2}, '', '', '', []),
        (
            {'econom': 2, 'business': 1, 'comfortplus': 1},
            '',
            '',
            '',
            ['econom'],
        ),
        # no is_cheaper message because both business and comfortplus
        # have no drivers found
        (
            {'econom': 2, 'business': 1, 'comfortplus': 0.853},
            '',
            '',
            '',
            ['business', 'comfortplus'],
        ),
    ],
)
def test_price_promo_no_cheaper_tariff(
        local_services_base,
        taxi_protocol,
        pricing_data_preparer,
        routestats_local_server,
        load_json,
        now,
        surge_values,
        is_cheaper_message,
        brandings,
        cheaper_class,
        unavailable_classes,
):
    pricing_data_preparer.set_meta('min_price', 99, category='econom')
    pricing_data_preparer.set_tariff_info(
        price_per_minute=9,
        price_per_kilometer=9,
        included_minutes=5,
        included_kilometers=2,
        category='econom',
    )

    for cls, sp in surge_values.items():
        pricing_data_preparer.set_user_surge(sp=sp, category=cls)

    pricing_data_preparer.set_cost(user_cost=633, driver_cost=633)
    pricing_data_preparer.set_trip_information(time=1440, distance=1000)
    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_json = response.json()

    # make sure there is no branding in selected (econom) class
    no_brandings = load_json('no_brandings_response.json')
    econom_no_branding_expected = no_brandings['service_levels'][0]
    econom_service_level_actual = response_json['service_levels'][0]
    econom_service_level_actual.pop('offer')

    # for case where econom is selected class and it is unavailable, we
    # need to manually adjust our expectations
    if 'econom' in unavailable_classes:
        econom_no_branding_expected.pop('estimated_waiting')
        econom_service_level_actual.pop('tariff_unavailable')

    assert econom_service_level_actual == econom_no_branding_expected

    # make sure there are no is_cheaper hints in other classes
    for service_level in response_json['service_levels'][1:]:
        assert 'is_cheaper' not in service_level


def get_clauses_for_suggest(percent, comfort_flag):
    return [
        {
            'title': '',
            'value': {
                'price_percent': percent,
                'suggest_most_comfortable': comfort_flag,
                'available': True,
            },
            'predicate': {'type': 'true'},
        },
    ]


def check_suggested_class_in_branding(
        response,
        branding_type,
        suggested_class,
        current_class,
        branding_title,
):
    has_suggestion_brand = False
    for service_level in response['service_levels']:
        if service_level['class'] == current_class:
            assert 'brandings' in service_level
            for brand in service_level['brandings']:
                if brand['type'] == branding_type:
                    has_suggestion_brand = True
                    assert brand['redirect_class'] == suggested_class
                    assert brand['title'] == branding_title
    assert has_suggestion_brand


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='tariff_upgrade_suggestion',
    consumers=['protocol/routestats'],
    clauses=get_clauses_for_suggest(60, False),
)
@pytest.mark.config(
    ROUTESTATS_PRICE_PROMO_SUGGEST_CLASSES={
        'econom': ['business', 'comfortplus'],
        'business': ['comfortplus'],
    },
)
@pytest.mark.user_experiments('fixed_price', 'routestats_fixed_price_time')
@pytest.mark.parametrize(
    'surge_values, unavailable_classes',
    [({'econom': 1.5, 'business': 1, 'comfortplus': 1}, [])],
)
def test_tariff_upgrade_suggest_not_most_comfort(
        local_services_base,
        taxi_protocol,
        pricing_data_preparer,
        routestats_local_server,
        load_json,
        now,
        surge_values,
        unavailable_classes,
):
    base_prices = {
        'econom': 100,
        'comfort': 199,
        'comfortplus': 199,
        'business': 199,
    }

    for cls, price in base_prices.items():
        sv = surge_values.get(cls) or 1
        pricing_data_preparer.set_user_surge(sv, category=cls)
        pricing_data_preparer.set_cost(
            user_cost=price * sv, driver_cost=price * sv, category=cls,
        )

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200

    check_suggested_class_in_branding(
        response.json(),
        'tariff_upgrade_suggestion',
        'business',
        'econom',
        'Now Comfort is slightly more expensive for you than Economy',
    )


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='tariff_upgrade_suggestion',
    consumers=['protocol/routestats'],
    clauses=get_clauses_for_suggest(60, True),
)
@pytest.mark.config(
    ROUTESTATS_PRICE_PROMO_SUGGEST_CLASSES={
        'econom': ['business', 'comfortplus'],
        'business': ['comfortplus'],
    },
)
@pytest.mark.user_experiments('fixed_price', 'routestats_fixed_price_time')
@pytest.mark.parametrize(
    'surge_values, unavailable_classes',
    [({'econom': 1.5, 'business': 1, 'comfortplus': 1}, [])],
)
def test_tariff_upgrade_suggest_most_comfort(
        local_services_base,
        taxi_protocol,
        pricing_data_preparer,
        routestats_local_server,
        load_json,
        now,
        surge_values,
        unavailable_classes,
):
    base_prices = {
        'econom': 100,
        'comfort': 199,
        'comfortplus': 199,
        'business': 199,
    }

    for cls, price in base_prices.items():
        sv = surge_values.get(cls) or 1
        pricing_data_preparer.set_user_surge(sv, category=cls)
        pricing_data_preparer.set_cost(
            user_cost=price * sv, driver_cost=price * sv, category=cls,
        )
    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200

    check_suggested_class_in_branding(
        response.json(),
        'tariff_upgrade_suggestion',
        'comfortplus',
        'econom',
        'Now Comfort+ is slightly more expensive for you than Economy',
    )


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='tariff_upgrade_suggestion',
    consumers=['protocol/routestats'],
    clauses=get_clauses_for_suggest(10, True),
)
@pytest.mark.config(
    ROUTESTATS_PRICE_PROMO_SUGGEST_CLASSES={
        'econom': ['business', 'comfortplus'],
        'business': ['comfortplus'],
    },
)
@pytest.mark.user_experiments('fixed_price', 'routestats_fixed_price_time')
@pytest.mark.parametrize(
    'surge_values, unavailable_classes',
    [
        ({'econom': 3, 'business': 1, 'comfortplus': 1}, []),
        ({'econom': 1, 'business': 2, 'comfortplus': 2}, []),
    ],
    ids=['too_cheap', 'too_expensive'],
)
def test_tariff_upgrade_no_suggestion(
        local_services_base,
        taxi_protocol,
        pricing_data_preparer,
        routestats_local_server,
        load_json,
        now,
        surge_values,
        unavailable_classes,
):
    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_json = response.json()

    for service_level in response_json['service_levels']:
        if service_level['class'] == 'econom':
            if 'brandings' in service_level:
                for brand in service_level['brandings']:
                    assert brand['type'] != 'tariff_upgrade_suggestion'


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='tariff_promo',
    consumers=['protocol/routestats'],
    clauses=[
        {
            'title': '',
            'value': {
                'enabled': True,
                'tariffs_redirect': {
                    'vip': 'courier',
                    'econom': 'courier',
                    'business': 'courier',
                },
            },
            'predicate': {'type': 'true'},
        },
    ],
)
# surge values are needed for routestats mock
@pytest.mark.parametrize(
    'surge_values, unavailable_classes',
    [({'econom': 1, 'business': 1, 'comfortplus': 1}, [])],
)
def test_tariff_courier_promo(
        local_services_base,
        taxi_protocol,
        pricing_data_preparer,
        routestats_local_server,
        load_json,
        now,
        surge_values,
        unavailable_classes,
):
    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200

    branding_title = 'Try Courier tariff'
    check_suggested_class_in_branding(
        response.json(),
        'tariff_promotion',
        'courier',
        'econom',
        branding_title,
    )
    check_suggested_class_in_branding(
        response.json(),
        'tariff_promotion',
        'courier',
        'business',
        branding_title,
    )
    check_suggested_class_in_branding(
        response.json(), 'tariff_promotion', 'courier', 'vip', branding_title,
    )


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='tariff_promo',
    consumers=['protocol/routestats'],
    clauses=[
        {
            'title': '',
            'value': {
                'enabled': True,
                'tariffs_redirect': {'econom': 'courier'},
            },
            'predicate': {'type': 'true'},
        },
    ],
)
# surge values are needed for routestats mock
@pytest.mark.parametrize(
    'surge_values, unavailable_classes',
    [({'econom': 1, 'business': 1, 'comfortplus': 1}, [])],
)
@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        'moscow': {'courier': {'visible_by_default': False}},
    },
)
def test_tariff_promo_unvisible_class(
        local_services_base,
        taxi_protocol,
        pricing_data_preparer,
        routestats_local_server,
        load_json,
        now,
        surge_values,
        unavailable_classes,
):
    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200

    json = response.json()

    for service_level in json['service_levels']:
        if service_level['class'] == 'econom':
            assert 'brandings' not in service_level


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='tariff_promo',
    consumers=['protocol/routestats'],
    clauses=[
        {
            'title': '',
            'value': {
                'enabled': True,
                'tariffs_redirect': {'econom': 'cargo'},
            },
            'predicate': {'type': 'true'},
        },
    ],
)
# surge values are needed for routestats mock
@pytest.mark.parametrize(
    'surge_values, unavailable_classes',
    [({'econom': 1, 'business': 1, 'comfortplus': 1}, ['cargo'])],
)
def test_tariff_promo_unavailable_class(
        local_services_base,
        taxi_protocol,
        pricing_data_preparer,
        routestats_local_server,
        load_json,
        now,
        surge_values,
        unavailable_classes,
):
    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200

    json = response.json()

    for service_level in json['service_levels']:
        if service_level['class'] == 'econom':
            assert 'brandings' not in service_level
