import pytest

import curfew
from protocol.routestats import utils

CLIENT_MESSAGES = {
    'integration.orders_estimate.unavailable_search': {
        'ru': 'Мало свободных машин',
    },
    'integration.orders_estimate.description': {
        'ru': 'Поездка %(price)s, ~%(duration)d мин',
    },
    'order_block.message.country.kgz': {'ru': curfew.CURFEW_TEXT},
}

# set of sources that wouldn't raise an error on curfew, instead they add
# `alert` field to response.
SOURCES_WITH_ALERT_IN_CONFIG = {'corp_cabinet', 'turboapp', 'light_business'}

# NOTE: all tests are performed at curfew by default
pytestmark = [
    curfew.now('23:00'),
    pytest.mark.translations(client_messages=CLIENT_MESSAGES),
    pytest.mark.config(
        INTEGRATION_API_SOURCES_WITH_ESTIMATE_ALERT_SUPPORT=list(
            SOURCES_WITH_ALERT_IN_CONFIG,
        ),
        INTEGRATION_USER_CONSISTENCY_CHECK=False,
        SMART_PRICING_FALLBACK_SETTINGS={
            'enabled': True,
            'forced_enabled': True,
        },
    ),
]


@pytest.fixture(
    scope='module',  # this groups tests together for one source
    params=[
        'call_center',
        'corp_cabinet',
        'turboapp',  # is not throwing errors
        'alice',
        'maps_app',
        'light_business',
    ],
)
def source(request):
    """Executes all tests in the module for every param of this fixture."""
    return request.param


def _prepare_request(
        source_id: str,
        selected_class: str = 'econom',
        zone_name: str = curfew.DEFAULT_ZONE_NAME,
        all_classes: bool = None,
):
    body = {
        'user': {
            'phone': '+79061112255',
            'personal_phone_id': 'p00000000000000000000005',
            'user_id': 'e4707fc6e79e4562b4f0af20a8e877a3',
            'yandex_uid': '480301451',  # for alice
        },
        'payment': {'type': 'cash'},
        'route': [[74.6, 42.866667], [74.589999, 42.8664]],
    }
    if source_id == 'call_center':
        headers = {'User-Agent': 'call_center'}
    else:
        headers = {}
        body['sourceid'] = source_id

    if zone_name in curfew.GEOPOINTS:
        point_a = curfew.GEOPOINTS[zone_name]  # for timezone
        body['route'] = [point_a, [74.589999, 42.8664]]

    if all_classes:
        body['all_classes'] = all_classes
        body['selected_class'] = ''  # same as in turboapp request
    else:
        body['selected_class'] = selected_class

    return body, headers


@pytest.fixture(name='make_request')
def _make_estimate_request(taxi_integration, pricing_data_preparer_fallback):
    pricing_data_preparer_fallback.set_strikeout(100)

    def _make_request(body: dict, headers: dict):
        return taxi_integration.post(
            'v1/orders/estimate', json=body, headers=headers,
        )

    return _make_request


def _alert_expected(source: str):
    return source == 'call_center' or source in SOURCES_WITH_ALERT_IN_CONFIG


def _process_response(response, source: str, expect_block: bool):
    """
    `source` is name of source as defined in
    `backend-cpp/common/src/models/user_sourceid.cpp`
    `expect_block` defines would we check `alert` field in response or not.
    """
    if not expect_block:
        assert response.status_code == 200, response.text
        assert 'alert' not in response.json()
        return

    response_data = response.json()

    if _alert_expected(source):
        assert response.status_code == 200, response.text
        assert 'alert' in response_data
        alert = {'code': 'CURFEW', 'description': curfew.CURFEW_TEXT}
        assert response_data['alert'] == alert
    else:
        assert response.status_code == 400
        assert 'error' in response_data
        assert response_data['error'] == {'text': curfew.CURFEW_TEXT}


@pytest.fixture(autouse=True)
def mocks(mockserver):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)

    @mockserver.json_handler('/tracker/1.0/nearest-drivers')
    def mock_nearest_drivers(request):
        return {'result': []}

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_zones(request):
        return {}


@pytest.mark.config(CURFEW_RULES=[], INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True)
def test_empty_rules(source, make_request):
    body, headers = _prepare_request(source)
    response = make_request(body, headers)
    _process_response(response, source, expect_block=False)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(countries=['kgz'], enabled=False)],
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
)
def test_rule_disabled(source, make_request):
    body, headers = _prepare_request(source)
    response = make_request(body, headers)
    _process_response(response, source, expect_block=False)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(countries=['kgz', 'kaz'])],
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
)
@pytest.mark.parametrize(
    'zone_name, expect_block', [('bishkek', True), ('moscow', False)],
)
def test_countries(zone_name, expect_block, source, make_request):
    body, headers = _prepare_request(source, zone_name=zone_name)
    response = make_request(body, headers)
    _process_response(response, source, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(zones=['bishkek', 'grozniy'])],
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
)
@pytest.mark.parametrize(
    'zone_name, expect_block', [('bishkek', True), ('moscow', False)],
)
def test_zones(zone_name, expect_block, source, make_request):
    body, headers = _prepare_request(source, zone_name=zone_name)
    response = make_request(body, headers)
    _process_response(response, source, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(zones=['bishkek'], countries=['rus'])],
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
)
def test_incompatible_zone_and_country(source, make_request):
    body, headers = _prepare_request(source)
    response = make_request(body, headers)
    _process_response(response, source, expect_block=False)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(zones=['bishkek'])],
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
)
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
def test_now(expect_block, source, make_request):
    body, headers = _prepare_request(source)
    response = make_request(body, headers)
    _process_response(response, source, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(countries=['kgz'], tariffs=['econom'])],
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
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
        zone_name, tariff, expect_block, source, make_request,
):
    body, headers = _prepare_request(
        source, zone_name=zone_name, selected_class=tariff,
    )
    response = make_request(body, headers)
    _process_response(response, source, expect_block)


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
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
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
def test_many_intervals(expect_block, source, make_request):
    body, headers = _prepare_request(source)
    response = make_request(body, headers)
    _process_response(response, source, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[
        curfew.make_rule(
            zones=['bishkek'],
            intervals=[
                {'from': '16:00', 'to': '23:59', 'weekdays': ['thu', 'fri']},
            ],
        ),
    ],
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
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
def test_weekdays(expect_block, source, make_request):
    body, headers = _prepare_request(source)
    response = make_request(body, headers)
    _process_response(response, source, expect_block)


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
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
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
def test_multiday_interval(expect_block, source, make_request):
    body, headers = _prepare_request(source)
    response = make_request(body, headers)
    _process_response(response, source, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[
        curfew.make_rule(
            zones=['bishkek'],
            intervals=[{'from': '23:00', 'to': '07:00', 'weekdays': ['thu']}],
        ),
    ],
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
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
        expect_block, source, make_request,
):
    body, headers = _prepare_request(source)
    response = make_request(body, headers)
    _process_response(response, source, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[
        curfew.make_rule(zones=['some_zone']),
        curfew.make_rule(zones=['some_other_zone'], tariffs=['comfortplus']),
        curfew.make_rule(countries=['kgz'], tariffs=['econom']),
        curfew.make_rule(zones=['bishkek']),
        curfew.make_rule(countries=['kaz']),
    ],
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
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
def test_many_rules(zone_name, tariff, expect_block, source, make_request):
    body, headers = _prepare_request(
        source, zone_name=zone_name, selected_class=tariff,
    )
    response = make_request(body, headers)
    _process_response(response, source, expect_block)


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business'],
    CURFEW_RULES=[
        curfew.make_rule(
            zones=['bishkek'], intervals=[{'from': '23:00', 'to': '07:00'}],
        ),
    ],
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
)
def test_all_classes(make_request):
    body, headers = _prepare_request(source_id='turboapp', all_classes=True)
    response = make_request(body, headers)
    _process_response(response, source='turboapp', expect_block=True)
