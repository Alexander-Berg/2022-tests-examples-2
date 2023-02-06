import base64
import collections
import json

import pytest

from order_offers_switch_parametrize import ORDER_OFFERS_SAVE_SWITCH
from protocol.routestats import utils

SurchargeParams = collections.namedtuple(
    'SurchargeParams', ['alpha', 'beta', 'surcharge'],
)

UNAVAILBLE_FOR_TIME_REQUESTED_MSG = 'Preorder unavailable'
UNAVAILBLE_FOR_TARIFF_REQUESTED_MSG = 'Preorder is unavailable for this tariff'
UNAVAILBLE_FOR_PAYMENT_TYPE_REQUESTED_MSG = (
    'Preorder is unavailable for this payment type'
)
UNAVAILBLE_FOR_MULTICLASS_MSG = 'Multiclass is unavailable with preorder'
UNAVAILBLE_FOR_REQUIREMENTS_REQUESTED_MSG = (
    'Preorder is unavailable with this requirements'
)

pytestmark = [
    pytest.mark.experiments3(filename='preorder_experiments3.json'),
    pytest.mark.now('2017-05-25T11:30:00+0300'),
    pytest.mark.translations(
        client_messages={
            'routestats.tariff_unavailable.preorder_unavailable_for_due': {
                'ru': UNAVAILBLE_FOR_TIME_REQUESTED_MSG,
            },
            'routestats.tariff_unavailable.preorder_unavailable_for_tariff': {
                'ru': UNAVAILBLE_FOR_TARIFF_REQUESTED_MSG,
            },
            (
                'routestats.tariff_unavailable.'
                'preorder_unavailable_for_payment_type'
            ): {'ru': UNAVAILBLE_FOR_PAYMENT_TYPE_REQUESTED_MSG},
            'routestats.tariff_unavailable.multiclass_preorder_unavailable': {
                'ru': UNAVAILBLE_FOR_MULTICLASS_MSG,
            },
            'routestats.tariff_unavailable.'
            'preorder_unavailable_for_requirements': {
                'ru': UNAVAILBLE_FOR_REQUIREMENTS_REQUESTED_MSG,
            },
            'multiclass.min_selected_count.text': {
                'ru': 'Выберите %(min_count)s и более классов',
            },
            'multiclass.popup.text': {'ru': 'Кто быстрей'},
        },
        tariff={
            'routestats.multiclass.name': {'ru': 'Fast'},
            'routestats.multiclass.details.not_fixed_price': {
                'ru': 'more than %(price)s',
            },
            'routestats.multiclass.details.description': {
                'ru': 'description of multiclass',
            },
            'routestats.multiclass.search_screen.title': {'ru': 'Searching'},
            'routestats.multiclass.search_screen.subtitle': {
                'ru': 'fastest car',
            },
        },
    ),
]

UNAVAILBLE_FOR_TIME_REQUESTED = {
    'code': 'preorder_unavailable_for_due',
    'message': UNAVAILBLE_FOR_TIME_REQUESTED_MSG,
}
UNAVAILBLE_FOR_TARIFF_REQUESTED = {
    'code': 'preorder_unavailable_for_tariff',
    'message': UNAVAILBLE_FOR_TARIFF_REQUESTED_MSG,
}
UNAVAILBLE_FOR_PAYMENT_TYPE_REQUESTED = {
    'code': 'preorder_unavailable_for_payment_type',
    'message': UNAVAILBLE_FOR_PAYMENT_TYPE_REQUESTED_MSG,
}
UNAVAILBLE_FOR_MULTICLASS = {
    'code': 'multiclass_preorder_unavailable',
    'message': UNAVAILBLE_FOR_MULTICLASS_MSG,
}
UNAVAILBLE_FOR_REQUIREMENTS_REQUESTED = {
    'code': 'preorder_unavailable_for_requirements',
    'message': UNAVAILBLE_FOR_REQUIREMENTS_REQUESTED_MSG,
}


@pytest.fixture
def assert_preorder_available(
        local_services, taxi_protocol, pricing_data_preparer,
):
    def check(
            request,
            is_available,
            unavailable_reason=UNAVAILBLE_FOR_TIME_REQUESTED,
    ):
        response = taxi_protocol.post('3.0/routestats', request)
        assert response.status_code == 200
        json = response.json()
        service_level = json['service_levels'][0]

        if is_available:
            assert 'tariff_unavailable' not in service_level
        else:
            assert 'tariff_unavailable' in service_level
            assert service_level['tariff_unavailable'] == unavailable_reason

    return check


@pytest.mark.parametrize(
    ('preorder_request_id', 'is_available'),
    ((None, True), ('test_id', False)),
)
def test_preorder_request_id_check(
        assert_preorder_available,
        load_json,
        preorder_request_id,
        is_available,
):
    request = load_json('request.json')
    if preorder_request_id:
        request['preorder_request_id'] = preorder_request_id
    else:
        if 'preorder_request_id' in request:
            request.pop('preorder_request_id')

    assert_preorder_available(
        request, is_available, UNAVAILBLE_FOR_PAYMENT_TYPE_REQUESTED,
    )


@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'],  # payment type in request.json
    PREORDER_CLASSES=['vip'],
)
@pytest.mark.parametrize(
    ('selected_class', 'is_available'), (('econom', False), ('vip', True)),
)
def test_class_check(
        assert_preorder_available,
        load_json,
        selected_class,
        is_available,
        mock_preorder,
):
    request = load_json('request.json')
    request['selected_class'] = selected_class
    assert_preorder_available(
        request, is_available, UNAVAILBLE_FOR_TARIFF_REQUESTED,
    )


@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['cash'],
    PREORDER_CLASSES=['econom'],  # selected class in request.json
)
@pytest.mark.parametrize(
    ('payment', 'is_available'),
    (
        ({'type': 'card', 'payment_method_id': 'card-x7698'}, False),
        ({'type': 'cash', 'payment_method_id': None}, True),
    ),
)
def test_payment_type_check(
        assert_preorder_available,
        load_json,
        payment,
        is_available,
        mock_preorder,
):
    request = load_json('request.json')
    request['payment'] = payment

    assert_preorder_available(
        request, is_available, UNAVAILBLE_FOR_PAYMENT_TYPE_REQUESTED,
    )


@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'],
    PREORDER_CLASSES=['econom'],
    PREORDER_ALLOW_DUE_CHECK_FAIL=False,
)
def test_fail_by_config(assert_preorder_available, load_json, mock_preorder):
    request = load_json('request.json')

    assert_preorder_available(request, False)


@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'],
    PREORDER_CLASSES=['econom'],
    PREORDER_ALLOW_DUE_CHECK_FAIL=False,
)
@pytest.mark.parametrize(
    ('selected_due', 'allowed_time_info', 'is_available'),
    (
        ('2017-05-25T12:30:00+0300', [], False),
        (
            '2017-05-25T12:30:00+0300',
            [
                {
                    'class': 'vip',
                    'interval_minutes': 15,
                    'allowed_time_ranges': [
                        {
                            'from': '2017-05-25T12:00:00+0300',
                            'to': '2017-05-25T13:00:00+0300',
                        },
                    ],
                },
            ],
            False,
        ),
        (
            '2017-05-25T12:30:00+0300',
            [
                {
                    'class': 'econom',
                    'interval_minutes': 15,
                    'allowed_time_ranges': [
                        {
                            'from': '2017-05-25T12:45:00+0300',
                            'to': '2017-05-25T13:00:00+0300',
                        },
                    ],
                },
            ],
            False,
        ),
        (
            '2017-05-25T12:30:00+0300',
            [
                {
                    'class': 'econom',
                    'interval_minutes': 15,
                    'allowed_time_ranges': [
                        {
                            'from': '2017-05-25T12:00:00+0300',
                            'to': '2017-05-25T13:00:00+0300',
                        },
                    ],
                },
            ],
            True,
        ),
    ),
)
def test_due_check(
        mockserver,
        assert_preorder_available,
        load_json,
        selected_due,
        allowed_time_info,
        is_available,
):
    @mockserver.json_handler('/preorder/4.0/preorder/v1/availability')
    def coop_account(request):
        return {
            'preorder_request_id': 'test_id',
            'allowed_time_info': allowed_time_info,
        }

    request = load_json('request.json')
    request['due'] = selected_due

    assert_preorder_available(request, is_available)


@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'], PREORDER_CLASSES=['econom'],
)
@pytest.mark.parametrize(
    ('is_preorder', 'jams_expected'), ((True, False), (False, True)),
)
def test_jams(
        local_services,
        taxi_protocol,
        load_json,
        is_preorder,
        jams_expected,
        mock_preorder,
        pricing_data_preparer,
):
    request = load_json('request.json')
    if not is_preorder:
        request.pop('preorder_request_id')

    response = taxi_protocol.post('3.0/routestats', request)
    json = response.json()

    assert json['jams'] == jams_expected


@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'], PREORDER_CLASSES=['econom'],
)
@pytest.mark.parametrize(
    ('is_preorder', 'description'),
    (
        (True, '~149 $SIGN$$CURRENCY$, ~10 min'),
        (False, '~140 $SIGN$$CURRENCY$, ~10 min'),
    ),
)
def test_price_description(
        local_services,
        taxi_protocol,
        load_json,
        is_preorder,
        description,
        mock_preorder,
        pricing_data_preparer,
):
    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=600, distance=100)
    if is_preorder:
        pricing_data_preparer.set_cost(user_cost=149, driver_cost=149)
    else:
        pricing_data_preparer.set_cost(user_cost=140, driver_cost=140)

    request = load_json('request.json')
    if not is_preorder:
        request.pop('preorder_request_id')

    response = taxi_protocol.post('3.0/routestats', request)
    json = response.json()

    assert json['service_levels'][0]['description'] == description


@pytest.mark.user_experiments('fixed_price')
@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'], PREORDER_CLASSES=['econom'],
)
@pytest.mark.parametrize(
    ('preorder_fixprice', 'is_preorder', 'is_fixed_price'),
    [
        (False, True, False),
        (False, False, True),
        (True, True, True),
        (True, False, True),
    ],
    ids=[
        'preorder is not fixprice',
        'order is fixprice',
        'preorder is fixprice under experiment',
        'order is fixprice under experiment',
    ],
)
@ORDER_OFFERS_SAVE_SWITCH
def test_fix_price(
        local_services_fixed_price,
        taxi_protocol,
        load_json,
        mockserver,
        db,
        mock_order_offers,
        order_offers_save_enabled,
        load_binary,
        mock_preorder,
        experiments3,
        preorder_fixprice,
        is_preorder,
        is_fixed_price,
        pricing_data_preparer,
):
    pricing_data_preparer.set_fixed_price(enable=is_fixed_price)

    if preorder_fixprice:
        experiments3.add_experiment(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='preorder_fixprice',
            consumers=['protocol/routestats'],
            clauses=[
                {
                    'title': '',
                    'value': {'enabled': True},
                    'predicate': {'type': 'true'},
                },
            ],
        )
        taxi_protocol.invalidate_caches()

    @mockserver.json_handler('/maps-router/route', prefix=True)
    def route_jams(request):
        return mockserver.make_response(
            load_binary('route_jams.protobuf'),
            content_type='application/x-protobuf',
        )

    request = load_json('request.json')
    if not is_preorder:
        request.pop('preorder_request_id')

    response = taxi_protocol.post('3.0/routestats', request)
    offer_id = response.json()['offer']

    offer = utils.get_offer(
        offer_id, db, mock_order_offers, order_offers_save_enabled,
    )
    if order_offers_save_enabled:
        assert mock_order_offers.mock_save_offer.times_called == 1

    assert offer['is_fixed_price'] == is_fixed_price
    for price in offer['prices']:
        assert price['is_fixed_price'] == is_fixed_price


@pytest.mark.user_experiments('fixed_price')
@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'], PREORDER_CLASSES=['econom'],
)
@pytest.mark.parametrize(
    ('show_labels', 'price_description'),
    [
        (False, 'Ride cost ~244\xa0$SIGN$$CURRENCY$'),
        (True, 'Ride cost 244\xa0$SIGN$$CURRENCY$'),
    ],
    ids=['hide fixprice labels', 'show fixprice labels'],
)
def test_fix_price_labels(
        local_services_fixed_price,
        taxi_protocol,
        load_json,
        mockserver,
        db,
        load_binary,
        mock_preorder,
        experiments3,
        show_labels,
        price_description,
        pricing_data_preparer,
):
    pricing_data_preparer.set_cost(user_cost=244, driver_cost=244)

    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='preorder_fixprice',
        consumers=['protocol/routestats'],
        clauses=[
            {
                'title': '',
                'value': {'enabled': True, 'show_labels': show_labels},
                'predicate': {'type': 'true'},
            },
        ],
    )
    taxi_protocol.invalidate_caches()

    @mockserver.json_handler('/maps-router/route', prefix=True)
    def route_jams(request):
        return mockserver.make_response(
            load_binary('route_jams.protobuf'),
            content_type='application/x-protobuf',
        )

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)
    assert (
        price_description
        == response.json()['service_levels'][0]['description']
    )


@pytest.mark.user_experiments('multiclass')
@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card', 'cash'],
    PREORDER_CLASSES=['econom'],
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=[
        'econom',
        'comfortplus',
        'vip',
        'minivan',
        'pool',
        'child_tariff',
    ],
    MULTICLASS_ENABLED=True,
    MULTICLASS_TARIFFS_BY_ZONE={'__default__': ['econom', 'comfortplus']},
    MULTICLASS_SELECTOR_ICON='',
)
@pytest.mark.parametrize(
    ('is_preorder', 'unavailable_reason'),
    ((True, UNAVAILBLE_FOR_MULTICLASS), (False, None)),
)
def test_with_multiclass(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        is_preorder,
        unavailable_reason,
):
    pricing_data_preparer.set_fixed_price(enable=False)

    request = load_json('multiclass_request.json')
    if not is_preorder:
        request.pop('preorder_request_id')

    response = taxi_protocol.post('3.0/routestats', request)
    json = response.json()

    multiclass_option = json['alternatives']['options'][0]
    if unavailable_reason is not None:
        assert multiclass_option['tariff_unavailable'] == unavailable_reason
    else:
        assert 'tariff_unavailable' not in multiclass_option


@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'], PREORDER_CLASSES=['econom'],
)
@pytest.mark.parametrize(
    ('is_preorder', 'value', 'display_card_icon', 'color_button'),
    ((False, 2, True, True), (True, 1, False, False)),
)
def test_surge_paid_options(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        is_preorder,
        mockserver,
        value,
        display_card_icon,
        color_button,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def _mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 2)

    request = load_json('request.json')
    if not is_preorder:
        request.pop('preorder_request_id')

    response = taxi_protocol.post('3.0/routestats', request)
    response_json = response.json()
    paid_options = response_json.get('paid_options', {})
    if paid_options and len(paid_options) > 0:
        assert paid_options['value'] == value
        assert paid_options['display_card_icon'] == display_card_icon
        assert paid_options['color_button'] == color_button


@pytest.fixture
def mock_preorder(mockserver):
    @mockserver.handler('/preorder/4.0/preorder/v1/availability')
    def return_500(response):
        return mockserver.make_response(status=500)


@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'],
    ALL_CATEGORIES=[
        'econom',
        'comfortplus',
        'vip',
        'minivan',
        'pool',
        'child_tariff',
    ],
    PREORDER_CLASSES=['econom', 'vip'],
)
@pytest.mark.parametrize(
    ('requirement', 'is_available', 'check_reqs'),
    (
        pytest.param(
            {
                'class': 'econom',
                'requirements': {'childchair_for_child_tariff': [3, 7]},
            },
            False,
            True,
            id='2_bad_requirements_max_options',
        ),
        pytest.param(
            {
                'class': 'econom',
                'requirements': {'childchair_for_child_tariff': 7},
            },
            False,
            True,
            id='1_bad_requirement_max_options',
        ),
        pytest.param(
            {'class': 'econom', 'requirements': {'bicycle': True}},
            True,
            True,
            id='ok_requirement',
        ),
        pytest.param(
            {
                'class': 'econom',
                'requirements': {'childchair_for_child_tariff': [7, 7]},
            },
            True,
            False,
            id='no_default_bl',
        ),
        pytest.param(
            {
                'class': 'vip',
                'requirements': {'childchair_for_child_tariff': [7, 3]},
            },
            False,
            True,
            id='2_bad_requirements_max_options_default',
        ),
        pytest.param(
            {
                'class': 'vip',
                'requirements': {'childchair_for_child_tariff': 3},
            },
            True,
            True,
            id='1_ok_requirement_max_options_default',
        ),
        pytest.param(
            {'class': 'econom', 'requirements': {'cargo_loaders': 1}},
            False,
            True,
            id='bad_requirement_list',
        ),
        pytest.param(
            {'class': 'vip', 'requirements': {'cargo_loaders': 1}},
            True,
            True,
            id='Ok_requirement_list_default',
        ),
        pytest.param(
            {'class': 'vip', 'requirements': {'cargo_loaders': 2}},
            False,
            True,
            id='bad_requirement_list_default',
        ),
        pytest.param(
            {'class': 'vip', 'requirements': {'cargo_loaders': 2}},
            True,
            False,
            id='disable_black_list',
        ),
    ),
)
def test_preorder_requirements(
        local_services,
        assert_preorder_available,
        taxi_protocol,
        load_json,
        db,
        mockserver,
        requirement,
        check_reqs,
        is_available,
):
    @mockserver.json_handler('/v1/configs/updates')
    def experiments3_proxy(*args, **kwargs):
        if check_reqs:
            return load_json('requirements_black_list.json')
        else:
            return load_json('black_list2.json')

    request = load_json('request_with_reqs.json')
    request['tariff_requirements'].append(requirement)

    request['selected_class'] = requirement['class']

    assert_preorder_available(
        request, is_available, UNAVAILBLE_FOR_REQUIREMENTS_REQUESTED,
    )


@pytest.mark.config(
    ALTPIN_MONEY_ZONES={
        '__default__': {
            'price_gain_absolute': 10,
            'price_gain_absolute_minorder': 0,
            'price_gain_ratio': 0,
            'route_gain_ratio': 0,
            'time_gain_ratio': 0,
        },
    },
    ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=-0.03,
    PREORDER_PAYMENT_METHODS=['card'],
    ALL_CATEGORIES=['econom', 'vip'],
    PREORDER_CLASSES=['econom', 'vip'],
    ALTPIN_MONEY_THRESHOLD_DEST_TIME=10,
)
@pytest.mark.parametrize(
    'is_preorder',
    (
        pytest.param(True, id='preorder_without_alts'),
        pytest.param(False, id='altpins_for_commons_order'),
    ),
)
@pytest.mark.experiments3(filename='exp3_alt_point_switcher.json')
def test_preorder_disable_altpin(
        tigraph,
        local_services_fixed_price,
        local_services_base,
        taxi_protocol,
        load_json,
        mockserver,
        db,
        is_preorder,
        pricing_data_preparer,
):
    pricing_data_preparer.push()
    pricing_data_preparer.set_cost(user_cost=500, driver_cost=500)

    @mockserver.json_handler('/v1/configs/updates')
    def experiments3_proxy(*args, **kwargs):
        return load_json('predict_surge.json')

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 5.0)

    request = load_json('request_altpin.json')

    if is_preorder:
        request['preorder_request_id'] = 'test_id'

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    if is_preorder:
        assert 'alternatives' not in response.json()
    else:
        assert 'alternatives' in response.json()


@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'],
    ALL_CATEGORIES=['econom'],
    PREORDER_CLASSES=['econom'],
)
@pytest.mark.parametrize(
    'is_preorder',
    (
        pytest.param(True, id='preorder_without_eta'),
        pytest.param(False, id='eta_for_common_order'),
    ),
)
def test_preorder_disable_eta(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        is_preorder,
):
    request = load_json('request_eta.json')
    if is_preorder:
        request['preorder_request_id'] = 'test_id'

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()

    expected = ['econom']
    for service_level in data['service_levels']:
        if service_level['class'] not in expected:
            continue
        if is_preorder:
            assert 'estimated_waiting' not in service_level
        else:
            assert 'estimated_waiting' in service_level


@pytest.mark.parametrize(
    'send_stats',
    (pytest.param(False, id='no_stats'), pytest.param(True, id='with_stats')),
)
def test_statistics_sending(
        db,
        taxi_protocol,
        local_services,
        mockserver,
        testpoint,
        load_json,
        send_stats,
        pricing_data_preparer,
):
    @mockserver.json_handler('/v1/configs/updates')
    def experiments3_proxy(*args, **kwargs):
        if send_stats:
            return load_json('preorder_configs3.json')
        else:
            return {'another': 'experiment'}

    @testpoint('yt_uploads::preorder_stats_info')
    def yt_upload(data):
        assert send_stats

        yt_data = base64.b64decode(data['base64'])
        arr = yt_data.decode('utf8').split('\t')
        info = {x.split('=')[0]: x.split('=')[1] for x in arr}

        offer = utils.get_saved_offer(db)
        assert offer['_id'] == info['offer_id']
        # distance rounded in routestats to 6th digit
        assert offer['distance'] == pytest.approx(
            float(info['distance']), 0.00001,
        )
        # time rounded  to minutes
        assert offer['time'] == pytest.approx(float(info['route_time']), 60)
        assert offer['route'] == json.loads(info['route'][:-2])['route']
        assert info['predict_surge'] == 'false'
        assert 'surges' in info
        assert (
            offer['prices'][0]['price']
            == json.loads(info['prices'][:-3])['econom']
        )

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    if send_stats:
        yt_upload.wait_call()
    assert response.status_code == 200
