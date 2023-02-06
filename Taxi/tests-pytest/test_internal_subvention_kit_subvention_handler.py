import datetime

import pytest

from taxi.internal import dbh
from taxi.internal.payment_kit import discounts
from taxi.internal.subvention_kit import rule_processors, calculation_context
from taxi.internal.subvention_kit import subvention_handler


@pytest.mark.filldb(
    config='for_get_min_ride_in_seconds_test',
)
@pytest.mark.parametrize('stamp,expected_value', [
    (datetime.datetime(2016, 12, 6, 12, 2, 13), 0),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), 60),
    (datetime.datetime(2016, 12, 6, 12, 3, 3), 60),
    (datetime.datetime(2016, 12, 6, 12, 3, 4), 20),
    (datetime.datetime(2099, 1, 1), 20),
])
@pytest.inline_callbacks
def test_get_min_ride_in_seconds(stamp, expected_value):
    actual_value = yield subvention_handler.get_min_ride_in_seconds(stamp)
    assert actual_value == expected_value


@pytest.mark.filldb(
    config='for_get_min_ride_in_meters_test',
)
@pytest.mark.parametrize('stamp,expected_value', [
    (datetime.datetime(2016, 12, 6, 12, 2, 13), 0),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), 6000),
    (datetime.datetime(2016, 12, 6, 12, 3, 3), 6000),
    (datetime.datetime(2016, 12, 6, 12, 3, 4), 2000),
    (datetime.datetime(2099, 1, 1), 2000),
])
@pytest.inline_callbacks
def test_get_min_ride_in_meters(stamp, expected_value):
    actual_value = yield subvention_handler.get_min_ride_in_meters(stamp)
    assert actual_value == expected_value


@pytest.mark.filldb(
    config='for_has_long_enough_ride_in_seconds_test',
)
@pytest.mark.parametrize('due,travel_time,expected_result', [
    (datetime.datetime(2016, 12, 1), None, True),
    (datetime.datetime(2016, 12, 1), 0, True),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), None, False),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), 59, False),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), 60, True),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), 61, True),
])
@pytest.inline_callbacks
def test_is_long_enough_ride_in_seconds(due, travel_time, expected_result):
    order = dbh.orders.Doc()
    order.request.due = due
    if travel_time is not None:
        order.statistics.travel_time = travel_time
    actual_result = yield subvention_handler.has_long_enough_ride_in_seconds(
        order
    )
    assert actual_result is expected_result


@pytest.mark.filldb(
    config='for_has_long_enough_ride_in_meters_test',
)
@pytest.mark.parametrize('due,travel_distance,expected_result', [
    (datetime.datetime(2016, 12, 1), None, True),
    (datetime.datetime(2016, 12, 1), 0, True),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), None, False),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), 5900, False),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), 6000, True),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), 6100, True),
])
@pytest.inline_callbacks
def test_is_long_enough_ride_in_meters(due, travel_distance, expected_result):
    order = dbh.orders.Doc()
    order.request.due = due
    if travel_distance is not None:
        order.statistics.travel_distance = travel_distance
    actual_result = yield subvention_handler.has_long_enough_ride_in_meters(
        order
    )
    assert actual_result is expected_result


@pytest.mark.filldb(
    config='for_has_long_enough_ride_test',
)
@pytest.mark.parametrize('due,travel_time,travel_distance,expected_result', [
    (datetime.datetime(2016, 12, 1), 90, None, True),
    (datetime.datetime(2016, 12, 1), 90, 0, True),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), 90, None, False),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), 90, 5900, False),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), 90, 6000, True),
    (datetime.datetime(2016, 12, 6, 12, 2, 14), 90, 6100, True),
])
@pytest.inline_callbacks
def test_has_long_enough_ride(
        due, travel_time, travel_distance, expected_result):
    order = dbh.orders.Doc()
    order.request.due = due
    if travel_time is not None:
        order.statistics.travel_time = travel_time
    if travel_distance is not None:
        order.statistics.travel_distance = travel_distance
    actual_result = yield subvention_handler.has_long_enough_ride(order)
    assert actual_result is expected_result


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('has_lightbox,has_sticker,expected_result', [
    (True, True, ['full_branding', 'lightbox', 'sticker']),
    (True, False, ['lightbox']),
    (False, True, ['sticker']),
    (False, False, []),
])
def test_get_subvention_branding(has_lightbox, has_sticker, expected_result):
    order = dbh.orders.Doc()
    order.performer.has_lightbox = has_lightbox
    order.performer.has_sticker = has_sticker
    proc = dbh.order_proc.Doc(order=order)
    actual_result = subvention_handler.get_subvention_brandings(proc)
    assert sorted(actual_result) == sorted(expected_result)


@pytest.mark.filldb(
    orders='for_get_all_subventions_with_matched_rules_test',
    subvention_reasons='for_get_all_subventions_with_matched_rules_test',
)
@pytest.mark.parametrize(
    'order_id,minimal_cost,expected_result', [
        (
            'no_bonus_rules_110_order_id',
            0,
            [
                rule_processors.MatchedRule(
                    subvention=discounts.SubventionCalc(40),
                    rule=rule_processors.CalcRule(
                        id='58243fd20779cf3c0c2bd1e2',
                        sum=150,
                        type='guarantee',
                        is_fake=False,
                        is_holded=False,
                        sub_commission=True,
                        is_bonus=False,
                        is_once=False,
                        decline_reasons=[],
                        display_in_taximeter=True,
                        rule_display_in_taximeter=True,
                        group_id=None,
                        clear_time=None,
                        driver_points=None,
                        geoareas=[],
                    )
                )
            ],
        ),
        (
            'empty_rules_110_order_id',
            0,
            [
                rule_processors.MatchedRule(
                    subvention=discounts.SubventionCalc(0),
                    rule=rule_processors.CalcRule(
                        id='virtual_rule_id',
                        sum=0,
                        type='add',
                        is_fake=False,
                        is_holded=False,
                        sub_commission=False,
                        is_bonus=False,
                        is_once=False,
                        decline_reasons=[],
                        display_in_taximeter=False,
                        rule_display_in_taximeter=False,
                        group_id=None,
                        clear_time=None,
                        driver_points=None,
                        geoareas=[],
                    )
                )
            ],
        ),
        (
            'no_rules_110_order_id',
            0,
            [
                rule_processors.MatchedRule(
                    subvention=discounts.SubventionCalc(0),
                    rule=rule_processors.CalcRule(
                        id='virtual_rule_id',
                        sum=0,
                        type='add',
                        is_fake=False,
                        is_holded=False,
                        sub_commission=False,
                        is_bonus=False,
                        is_once=False,
                        decline_reasons=[],
                        display_in_taximeter=False,
                        rule_display_in_taximeter=False,
                        group_id=None,
                        clear_time=None,
                        driver_points=None,
                        geoareas=[],
                    )
                )
            ],
        ),
        (
            'two_no_bonus_rules_110_order_id',
            0,
            [
                rule_processors.MatchedRule(
                    subvention=discounts.SubventionCalc(20),
                    rule=rule_processors.CalcRule(
                        id='first_id',
                        sum=130,
                        type='guarantee',
                        is_fake=False,
                        is_holded=False,
                        sub_commission=True,
                        is_bonus=False,
                        is_once=False,
                        decline_reasons=[],
                        display_in_taximeter=True,
                        rule_display_in_taximeter=True,
                        group_id=None,
                        clear_time=None,
                        driver_points=None,
                        geoareas=[],
                    )
                )
            ],
        ),
        (
            'one_bonus_two_not_bonus_rule_110_order_id',
            0,
            [
                rule_processors.MatchedRule(
                    subvention=discounts.SubventionCalc(20),
                    rule=rule_processors.CalcRule(
                        id='not_bonus_id',
                        sum=130,
                        type='guarantee',
                        is_fake=False,
                        is_holded=False,
                        sub_commission=True,
                        is_bonus=False,
                        is_once=False,
                        decline_reasons=[],
                        display_in_taximeter=True,
                        rule_display_in_taximeter=True,
                        group_id=None,
                        clear_time=None,
                        driver_points=None,
                        geoareas=[],
                    )
                ),
                rule_processors.MatchedRule(
                    subvention=discounts.SubventionCalc(500),
                    rule=rule_processors.CalcRule(
                        id='bonus_id',
                        sum=500,
                        type='add',
                        is_fake=False,
                        is_holded=False,
                        sub_commission=False,
                        is_bonus=True,
                        is_once=False,
                        decline_reasons=[],
                        display_in_taximeter=True,
                        rule_display_in_taximeter=True,
                        group_id=None,
                        clear_time=None,
                        driver_points=None,
                        geoareas=[],
                    )
                )
            ],
        ),
        (
            'one_discount_payback_one_guarantee_order_id',
            5,
            [
                rule_processors.MatchedRule(
                    subvention=discounts.SubventionCalc(20),
                    rule=rule_processors.CalcRule(
                        id='not_bonus_id',
                        sum=130,
                        type='guarantee',
                        is_fake=False,
                        is_holded=False,
                        sub_commission=True,
                        is_bonus=False,
                        is_once=False,
                        decline_reasons=[],
                        display_in_taximeter=True,
                        rule_display_in_taximeter=True,
                        group_id=None,
                        clear_time=None,
                        driver_points=None,
                        geoareas=[],
                    )
                ),
                rule_processors.MatchedRule(
                    subvention=discounts.SubventionCalc('23.75'),
                    rule=rule_processors.CalcRule(
                        id='payback_id',
                        sum=0,
                        type='discount_payback',
                        is_fake=False,
                        is_holded=False,
                        sub_commission=False,
                        is_bonus=True,
                        is_once=False,
                        decline_reasons=[],
                        display_in_taximeter=True,
                        rule_display_in_taximeter=True,
                        group_id=None,
                        clear_time=None,
                        driver_points=None,
                        geoareas=[],
                    )
                )
            ],
        ),
        (
            'one_once_bonus_one_guarantee_order_id',
            5,
            [
                rule_processors.MatchedRule(
                    subvention=discounts.SubventionCalc('500'),
                    rule=rule_processors.CalcRule(
                        id='once_bonus_id',
                        sum=500,
                        type='add',
                        is_fake=False,
                        is_holded=False,
                        sub_commission=False,
                        is_bonus=True,
                        is_once=True,
                        decline_reasons=[],
                        display_in_taximeter=True,
                        rule_display_in_taximeter=True,
                        group_id=None,
                        clear_time=None,
                        driver_points=None,
                        geoareas=[],
                    )
                )
            ],
        ),
        # we choose personal guarantee, even it's less than usual guarantee
        (
                'one_guarantee_one_personal_guarantee_order_id',
                5,
                [
                    rule_processors.MatchedRule(
                        subvention=discounts.SubventionCalc('120'),
                        rule=rule_processors.CalcRule(
                            id='p_guarantee_id',
                            sum=230,
                            type='guarantee',
                            is_fake=False,
                            is_holded=False,
                            sub_commission=False,
                            is_bonus=False,
                            is_once=False,
                            decline_reasons=[],
                            display_in_taximeter=True,
                            rule_display_in_taximeter=True,
                            group_id=None,
                            clear_time=None,
                            driver_points=None,
                            geoareas=[],
                        )
                    )
                ],
        ),
])
@pytest.inline_callbacks
def test_get_all_subventions_with_matched_rules(
        patch, order_id, minimal_cost, expected_result):
    @patch('taxi.internal.city_manager.get_city_tz')
    def get_city_tz(city_id):
        return 'Europe/Moscow'

    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    context = calculation_context.CalculationContext(
        {order.pk: minimal_cost}
    )
    try:
        subvention_reasons = (
            yield dbh.subvention_reasons.Doc.find_one_by_order_id(order.pk)
        )
    except dbh.subvention_reasons.NotFound:
        subvention_reasons = None

    embedded_reasons_by_id = {}
    if order.is_umbrella and order.embedded_orders:
        cls = dbh.subvention_reasons.Doc
        embedded_ids = {emb['id'] for emb in order.embedded_orders}
        embedded_reasons_by_id = cls.find_many_by_orders(
            [{'_id': emb['id']} for emb in embedded_ids]
        )

    actual_result = yield subvention_handler.get_all_subventions_with_matched_rules(
        order=order,
        context=context,
        subvention_reasons=subvention_reasons,
        embedded_reasons_by_order=embedded_reasons_by_id
    )
    actual_result = _sort_by_rule_id(actual_result)
    expected_result = _sort_by_rule_id(expected_result)
    assert len(actual_result) == len(expected_result)
    for index, actual_result in enumerate(actual_result):
        assert actual_result.rule == expected_result[index].rule
        assert subvention_calc_eq(actual_result.subvention,
                                  expected_result[index].subvention)


@pytest.mark.filldb(
    orders='for_get_all_subventions_with_matched_rules_test'
)
@pytest.mark.parametrize('order_id,min_price,deserves', [
    ('order_with_ya_plus', 99, True),
    ('order_without_ya_plus', 99, False),
])
@pytest.inline_callbacks
def test_deserves_subvention(patch, order_id, min_price, deserves):
    handler = 'taxi.internal.subvention_kit.subvention_handler'

    @patch('%s.has_long_enough_ride' % handler)
    def has_long_enough_ride(other):
        return True

    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    deserves_res = (
        yield subvention_handler.deserves_subvention(order, min_price)
    )

    assert deserves_res == deserves


def subvention_calc_eq(a, b):
    assert a.value == b.value
    assert len(a.declines) == len(b.declines)
    for index, decline in enumerate(a.declines):
        assert decline.value == b.declines[index].value
        assert decline.type == b.declines[index].type
    return True


def _sort_by_rule_id(matched_rules):
    return sorted(matched_rules, key=lambda mr: mr.rule.id)
