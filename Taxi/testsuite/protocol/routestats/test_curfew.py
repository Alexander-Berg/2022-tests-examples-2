import pytest

import curfew
from protocol.routestats import utils

MULTICLASS_CLIENT_MESSAGES = {
    'multiclass.min_selected_count.text': {
        'ru': 'Выберите %(min_count)s и более классов',
    },
    'multiclass.popup.text': {'ru': 'Кто быстрей'},
}
MULTICLASS_TARIFF_MESSAGES = {
    'routestats.multiclass.name': {'ru': 'Fast'},
    'routestats.multiclass.details.not_fixed_price': {
        'ru': 'more than %(price)s',
    },
    'routestats.multiclass.details.description': {
        'ru': 'description of multiclass',
    },
    'routestats.multiclass.search_screen.title': {'ru': 'Searching'},
    'routestats.multiclass.search_screen.subtitle': {'ru': 'fastest car'},
}

CLIENT_MESSAGES = {
    'routestats.tariff_unavailable.curfew': {'ru': curfew.CURFEW_SHORT_TEXT},
    'routestats.tariff_unavailable.unsupported_payment_method': {
        'ru': 'Payment method is not supported',
    },
    **MULTICLASS_CLIENT_MESSAGES,
}


# NOTE: all tests are performed at curfew by default
pytestmark = [
    curfew.now('23:00'),
    pytest.mark.translations(client_messages=CLIENT_MESSAGES),
]


def _make_request(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        zone_name: str = None,
        classes=None,
):
    request = load_json('simple_request.json')
    zone_name = zone_name or curfew.DEFAULT_ZONE_NAME
    request['zone_name'] = zone_name
    if zone_name in curfew.GEOPOINTS:
        request['route'][0] = curfew.GEOPOINTS[zone_name]  # for timezone
    if classes:
        if len(classes) == 1:
            request['selected_class'] = classes[0]
        else:
            del request['selected_class']
            request['supports_multiclass'] = True
            request['multiclass_options'] = {
                'class': classes,
                'selected': False,
            }

    response = taxi_protocol.post('3.0/routestats', request)
    return response


def _process_response(response, expect_block: bool, blocked_classes=None):
    assert response.status_code == 200
    response = response.json()
    if expect_block or blocked_classes:
        for sl in response['service_levels']:
            if blocked_classes is None or sl['class'] in blocked_classes:
                assert 'tariff_unavailable' in sl
                info = sl['tariff_unavailable']
                assert info['code'] == 'curfew'
                assert info['message'] == curfew.CURFEW_SHORT_TEXT
    else:
        for sl in response['service_levels']:
            info = sl.get('tariff_unavailable')
            if info:
                assert info['code'] != 'curfew'


@pytest.fixture(autouse=True)
def mocks(mockserver):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_zones(request):
        return {}


@pytest.mark.config(CURFEW_RULES=[])
def test_empty_rules(taxi_protocol, pricing_data_preparer, load_json):
    response = _make_request(taxi_protocol, pricing_data_preparer, load_json)
    _process_response(response, expect_block=False)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(countries=['kgz'], enabled=False)],
)
def test_rule_disabled(taxi_protocol, pricing_data_preparer, load_json):
    response = _make_request(taxi_protocol, pricing_data_preparer, load_json)
    _process_response(response, expect_block=False)


@pytest.mark.config(CURFEW_RULES=[curfew.make_rule(countries=['kgz', 'kaz'])])
@pytest.mark.parametrize(
    'zone_name, expect_block', [('bishkek', True), ('moscow', False)],
)
def test_countries(
        zone_name,
        expect_block,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
):
    response = _make_request(
        taxi_protocol, pricing_data_preparer, load_json, zone_name=zone_name,
    )
    _process_response(response, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(zones=['bishkek', 'grozniy'])],
)
@pytest.mark.parametrize(
    'zone_name, expect_block', [('bishkek', True), ('moscow', False)],
)
def test_zones(
        zone_name,
        expect_block,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
):
    response = _make_request(
        taxi_protocol, pricing_data_preparer, load_json, zone_name=zone_name,
    )
    _process_response(response, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(zones=['bishkek'], countries=['rus'])],
)
def test_incompatible_zone_and_country(
        taxi_protocol, pricing_data_preparer, load_json,
):
    response = _make_request(taxi_protocol, pricing_data_preparer, load_json)
    _process_response(response, expect_block=False)


@pytest.mark.config(CURFEW_RULES=[curfew.make_rule(zones=['bishkek'])])
@pytest.mark.parametrize(
    'expect_block',
    [
        # curfew starts at 21:00 ends at 7:00
        pytest.param(True, marks=curfew.now('23:00')),
        pytest.param(False, marks=curfew.now('20:00')),
        # time after midnight in curfew interval (works only without weekdays)
        pytest.param(True, marks=curfew.now('05:00')),
        # current time not in curfew, but timezone moves it in curfew
        pytest.param(True, marks=curfew.now('20:00', tz='+04')),
        # time in curfew, but timezone not
        pytest.param(False, marks=curfew.now('23:00', tz='+09')),
    ],
)
def test_now(expect_block, taxi_protocol, pricing_data_preparer, load_json):
    response = _make_request(taxi_protocol, pricing_data_preparer, load_json)
    _process_response(response, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(countries=['kgz'], tariffs=['econom'])],
)
@pytest.mark.parametrize(
    'zone_name, tariff, expect_block',
    [
        ('bishkek', 'econom', True),
        ('moscow', 'econom', False),
        ('bishkek', 'business', False),
    ],
)
def test_country_and_tariff(
        zone_name,
        tariff,
        expect_block,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
):
    blocked_classes = None
    if zone_name == 'bishkek':
        blocked_classes = 'econom'
    response = _make_request(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        zone_name=zone_name,
        classes=[tariff],
    )
    _process_response(response, expect_block, blocked_classes=blocked_classes)


@pytest.mark.config(
    CURFEW_RULES=[
        curfew.make_rule(
            zones=['bishkek'],
            intervals=[
                # incorrect order
                {'from': '22:00', 'to': '23:00'},
                {'from': '10:00', 'to': '12:00'},
                {'from': '15:00', 'to': '16:00'},
                {'from': '15:00', 'to': '18:00'},
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'expect_block',
    [
        pytest.param(False, marks=curfew.now('05:00')),
        pytest.param(True, marks=curfew.now('11:30')),
        pytest.param(False, marks=curfew.now('12:30')),
        pytest.param(True, marks=curfew.now('17:59')),
        pytest.param(False, marks=curfew.now('21:00')),
        pytest.param(True, marks=curfew.now('22:10')),
    ],
)
def test_many_intervals(
        expect_block, taxi_protocol, pricing_data_preparer, load_json,
):
    response = _make_request(taxi_protocol, pricing_data_preparer, load_json)
    _process_response(response, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[
        curfew.make_rule(
            zones=['bishkek'],
            intervals=[
                {'from': '16:00', 'to': '23:59', 'weekdays': ['thu', 'fri']},
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'expect_block',
    [
        pytest.param(False, marks=curfew.now('12:00', day=curfew.THURSDAY)),
        pytest.param(True, marks=curfew.now('17:00', day=curfew.THURSDAY)),
        pytest.param(True, marks=curfew.now('17:00', day=curfew.FRIDAY)),
        pytest.param(False, marks=curfew.now('17:00', day=curfew.SATURDAY)),
    ],
)
def test_weekdays(
        expect_block, taxi_protocol, pricing_data_preparer, load_json,
):
    response = _make_request(taxi_protocol, pricing_data_preparer, load_json)
    _process_response(response, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[
        curfew.make_rule(
            zones=['bishkek'],
            intervals=[
                # from saturday to monday
                {'from': '13:00', 'to': '23:59', 'weekdays': ['sat']},
                {'from': '00:00', 'to': '23:59', 'weekdays': ['sun']},
                {'from': '00:00', 'to': '13:00', 'weekdays': ['mon']},
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'expect_block',
    [
        pytest.param(False, marks=curfew.now('10:00', day=curfew.SATURDAY)),
        pytest.param(True, marks=curfew.now('15:30', day=curfew.SATURDAY)),
        pytest.param(True, marks=curfew.now('00:00', day=curfew.SUNDAY)),
        pytest.param(True, marks=curfew.now('04:00', day='24')),
        pytest.param(False, marks=curfew.now('15:00', day='24')),
    ],
)
def test_multiday_interval(
        expect_block, taxi_protocol, pricing_data_preparer, load_json,
):
    response = _make_request(taxi_protocol, pricing_data_preparer, load_json)
    _process_response(response, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[
        curfew.make_rule(
            zones=['bishkek'],
            intervals=[{'from': '23:00', 'to': '07:00', 'weekdays': ['thu']}],
        ),
    ],
)
@pytest.mark.parametrize(
    'expect_block',
    [
        pytest.param(False, marks=curfew.now('04:00', day=curfew.THURSDAY)),
        pytest.param(False, marks=curfew.now('23:30', day=curfew.THURSDAY)),
        pytest.param(False, marks=curfew.now('04:00', day=curfew.FRIDAY)),
    ],
)
def test_overnight_not_working_with_weekdays(
        expect_block, taxi_protocol, pricing_data_preparer, load_json,
):
    response = _make_request(taxi_protocol, pricing_data_preparer, load_json)
    _process_response(response, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[
        curfew.make_rule(zones=['some_zone']),
        curfew.make_rule(zones=['some_other_zone'], tariffs=['comfortplus']),
        curfew.make_rule(countries=['kgz'], tariffs=['econom']),
        curfew.make_rule(zones=['bishkek']),
        curfew.make_rule(countries=['kaz']),
    ],
)
@pytest.mark.parametrize(
    'zone_name, tariff, expect_block',
    [
        ('bishkek', 'business', True),
        ('bishkek', 'econom', True),
        ('moscow', 'econom', False),
        # ('almaty', 'comfortplus', True),
    ],
)
def test_many_rules(
        zone_name,
        tariff,
        expect_block,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
):
    response = _make_request(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        zone_name=zone_name,
        classes=[tariff],
    )
    _process_response(response, expect_block)


@pytest.mark.user_experiments('multiclass')
@pytest.mark.config(
    MULTICLASS_ENABLED=True,
    MULTICLASS_TARIFFS_BY_ZONE={
        '__default__': ['econom', 'business', 'comfortplus'],
    },
)
@pytest.mark.translations(tariff=MULTICLASS_TARIFF_MESSAGES)
@pytest.mark.parametrize(
    'blocked_tariffs, expect_block',
    [
        # block order if any of classes satisfies rules
        (['business'], False),
        (['econom'], True),
        (['comfortplus'], True),
    ],
)
def test_multiclass(
        blocked_tariffs,
        expect_block,
        taxi_protocol,
        pricing_data_preparer,
        config,
        load_json,
):
    config.set_values(
        {'CURFEW_RULES': [curfew.make_rule(tariffs=blocked_tariffs)]},
    )

    response = _make_request(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        classes=['econom', 'comfortplus'],
    )
    _process_response(response, expect_block, blocked_classes=blocked_tariffs)
