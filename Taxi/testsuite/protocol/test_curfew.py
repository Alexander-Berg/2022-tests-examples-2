import pytest

import curfew
from individual_tariffs_switch_parametrize import (
    PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS,
)

CLIENT_MESSAGES = {
    'order_block.message.country.kgz': {'ru': curfew.CURFEW_TEXT},
}


# see NOTE to weekdays in curfew module
WEDNESDAY = '19'
THURSDAY = '20'
FRIDAY = '21'
SATURDAY = '22'
SUNDAY = '23'


# NOTE: all tests are performed at curfew by default
pytestmark = [
    curfew.now('23:00'),
    pytest.mark.translations(client_messages=CLIENT_MESSAGES),
]


def _make_request(
        taxi_protocol,
        load_json,
        zone_name: str = None,
        due: str = None,
        classes=None,
):
    request = load_json('basic_request.json')
    zone_name = zone_name or curfew.DEFAULT_ZONE_NAME
    request['zone_name'] = zone_name
    if zone_name in curfew.GEOPOINTS:
        point_a = curfew.GEOPOINTS[zone_name]  # for timezone
        request['route'][0]['geopoint'] = point_a
    if due:
        request['due'] = due
    if classes:
        request['class'] = classes

    response = taxi_protocol.post('3.0/orderdraft', request)
    return response


def _process_response(response, expect_block: bool):
    if expect_block:
        assert response.status_code == 406
        response = response.json()
        assert response['error']['code'] == 'ORDER_BLOCKED_BY_CURFEW'
        assert response['error']['text'] == curfew.CURFEW_TEXT
    else:
        assert response.status_code == 200


@pytest.fixture(autouse=True)
def pickuppoints_zones_handlers(mockserver):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}


@pytest.mark.config(CURFEW_RULES=[])
def test_empty_rules(taxi_protocol, load_json):
    response = _make_request(taxi_protocol, load_json)
    _process_response(response, expect_block=False)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(countries=['kgz'], enabled=False)],
)
def test_rule_disabled(taxi_protocol, load_json):
    response = _make_request(taxi_protocol, load_json)
    _process_response(response, expect_block=False)


@pytest.mark.config(CURFEW_RULES=[curfew.make_rule(countries=['kgz', 'kaz'])])
@pytest.mark.parametrize(
    'zone_name, expect_block', [('bishkek', True), ('moscow', False)],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_countries(
        zone_name,
        expect_block,
        taxi_protocol,
        load_json,
        individual_tariffs_switch_on,
):
    response = _make_request(taxi_protocol, load_json, zone_name=zone_name)
    _process_response(response, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(zones=['bishkek', 'grozniy'])],
)
@pytest.mark.parametrize(
    'zone_name, expect_block', [('bishkek', True), ('moscow', False)],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_zones(
        zone_name,
        expect_block,
        taxi_protocol,
        load_json,
        individual_tariffs_switch_on,
):
    response = _make_request(taxi_protocol, load_json, zone_name=zone_name)
    _process_response(response, expect_block)


@pytest.mark.config(
    CURFEW_RULES=[curfew.make_rule(zones=['bishkek'], countries=['rus'])],
)
def test_incompatible_zone_and_country(taxi_protocol, load_json):
    response = _make_request(taxi_protocol, load_json)
    _process_response(response, expect_block=False)


BISHKEK_RULE = curfew.make_rule(zones=['bishkek'])


@pytest.mark.config(CURFEW_RULES=[BISHKEK_RULE])
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
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_now(
        expect_block, taxi_protocol, load_json, individual_tariffs_switch_on,
):
    response = _make_request(taxi_protocol, load_json)
    _process_response(response, expect_block)


@pytest.mark.config(CURFEW_RULES=[BISHKEK_RULE])
@pytest.mark.parametrize(
    'due, expect_block',
    [
        # curfew starts at 21:00 ends at 7:00
        # preorder next day, currently not in curfew
        pytest.param(
            curfew.time('15:00', day=SUNDAY), False, marks=curfew.now('20:00'),
        ),
        # preorder next day not in curfew, currently in curfew
        pytest.param(
            curfew.time('15:00', day=SUNDAY), False, marks=curfew.now('23:00'),
        ),
        # preorder, due at curfew, timezone not
        pytest.param(
            curfew.time('23:00', tz='+09'), False, marks=curfew.now('10:00'),
        ),
        # preorder, due not at curfew, but timezone moves it in curfew
        pytest.param(
            curfew.time('20:00', tz='+04'), True, marks=curfew.now('10:00'),
        ),
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_due(
        due,
        expect_block,
        taxi_protocol,
        load_json,
        individual_tariffs_switch_on,
):
    response = _make_request(taxi_protocol, load_json, due=due)
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
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_country_and_tariff(
        zone_name,
        tariff,
        expect_block,
        taxi_protocol,
        load_json,
        individual_tariffs_switch_on,
):
    response = _make_request(
        taxi_protocol, load_json, zone_name=zone_name, classes=[tariff],
    )
    _process_response(response, expect_block)


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
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_many_intervals(
        expect_block, taxi_protocol, load_json, individual_tariffs_switch_on,
):
    response = _make_request(taxi_protocol, load_json)
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
        pytest.param(False, marks=curfew.now('12:00', day=THURSDAY)),
        pytest.param(True, marks=curfew.now('17:00', day=THURSDAY)),
        pytest.param(True, marks=curfew.now('17:00', day=FRIDAY)),
        pytest.param(False, marks=curfew.now('17:00', day=SATURDAY)),
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_weekdays(
        expect_block, taxi_protocol, load_json, individual_tariffs_switch_on,
):
    response = _make_request(taxi_protocol, load_json)
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
    'day, time, expect_block',
    [
        pytest.param(
            THURSDAY, '23:00', True, marks=curfew.now('23:00', day=WEDNESDAY),
        ),
        pytest.param(
            THURSDAY, '23:00', True, marks=curfew.now('12:00', day=THURSDAY),
        ),
        pytest.param(
            FRIDAY, '23:00', True, marks=curfew.now('23:00', day=THURSDAY),
        ),
        pytest.param(
            SUNDAY, '12:00', False, marks=curfew.now('23:00', day=FRIDAY),
        ),
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_weekdays_with_due(
        day,
        time,
        expect_block,
        taxi_protocol,
        load_json,
        individual_tariffs_switch_on,
):
    due = curfew.time(time, day=day)
    response = _make_request(taxi_protocol, load_json, due=due)
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
        pytest.param(False, marks=curfew.now('10:00', day=SATURDAY)),
        pytest.param(True, marks=curfew.now('15:30', day=SATURDAY)),
        pytest.param(True, marks=curfew.now('00:00', day=SUNDAY)),
        pytest.param(True, marks=curfew.now('04:00', day='24')),
        pytest.param(False, marks=curfew.now('15:00', day='24')),
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_multiday_interval(
        expect_block, taxi_protocol, load_json, individual_tariffs_switch_on,
):
    response = _make_request(taxi_protocol, load_json)
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
        pytest.param(False, marks=curfew.now('04:00', day=THURSDAY)),
        pytest.param(False, marks=curfew.now('23:30', day=THURSDAY)),
        pytest.param(False, marks=curfew.now('04:00', day=FRIDAY)),
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_overnight_not_working_with_weekdays(
        expect_block, taxi_protocol, load_json, individual_tariffs_switch_on,
):
    response = _make_request(taxi_protocol, load_json)
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
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_many_rules(
        zone_name,
        tariff,
        expect_block,
        taxi_protocol,
        load_json,
        individual_tariffs_switch_on,
):
    response = _make_request(
        taxi_protocol, load_json, zone_name=zone_name, classes=[tariff],
    )
    _process_response(response, expect_block)


@pytest.mark.config(
    MULTICLASS_ENABLED=True,
    MULTICLASS_TARIFFS_BY_ZONE={
        '__default__': ['econom', 'business', 'comfortplus'],
    },
)
@pytest.mark.parametrize(
    'blocked_tariffs, expect_block',
    [
        # block order if any of classes satisfies rules
        (['business'], False),
        (['econom'], True),
        (['comfortplus'], True),
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_multiclass(
        blocked_tariffs,
        expect_block,
        taxi_protocol,
        config,
        load_json,
        individual_tariffs_switch_on,
):
    config.set_values(
        {'CURFEW_RULES': [curfew.make_rule(tariffs=blocked_tariffs)]},
    )

    response = _make_request(
        taxi_protocol, load_json, classes=['econom', 'comfortplus'],
    )
    _process_response(response, expect_block)
