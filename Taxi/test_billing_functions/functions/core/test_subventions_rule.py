import datetime as dt
import decimal
from typing import Collection
from typing import Optional

import more_itertools
import pytest

from billing_models.generated import models
from billing_models.generated.models import goal_shift
from billing_models.generated.models import taxi_goal_shift

from billing_functions import consts
from billing_functions.functions.core.subventions import do_x_get_y
from billing_functions.functions.core.subventions import geo_booking
from billing_functions.functions.core.subventions import goal
from billing_functions.functions.core.subventions import nmfg
from billing_functions.functions.core.subventions import rule as rules
from billing_functions.functions.core.subventions import rule_visitors
from billing_functions.functions.core.subventions import single_on_top
from billing_functions.functions.core.subventions import single_ride
from billing_functions.repositories import subvention_rules
from test_billing_functions import equatable

_TEN = decimal.Decimal('10')
_ONE = decimal.Decimal('1')


def match_req(
        is_single_ride_allowed: bool = True,
        is_single_on_top_allowed: bool = True,
        is_goal_allowed: bool = True,
        closed_without_accept: bool = False,
        need_dispatcher_acceptance: bool = False,
        order_status: str = 'finished',
        order_taxi_status: str = 'complete',
        payment_type: consts.PaymentType = consts.PaymentType.CARD,
        park_corp_vat: Optional[decimal.Decimal] = None,
        driver_activity_points: Optional[float] = 100,
) -> rules.MatchRequest:
    return rules.MatchRequest(
        is_single_ride_allowed=is_single_ride_allowed,
        is_single_on_top_allowed=is_single_on_top_allowed,
        is_goal_allowed=is_goal_allowed,
        closed_without_accept=closed_without_accept,
        need_dispatcher_acceptance=need_dispatcher_acceptance,
        status=order_status,
        taxi_status=order_taxi_status,
        payment_type=payment_type,
        park_corp_vat=park_corp_vat,
        driver_activity_points=driver_activity_points,
    )


def arbitrary_goal_rule() -> subvention_rules.GoalRule:
    return subvention_rules.GoalRule(
        id='id',
        budget_id='budget_id',
        currency='RUB',
        window=subvention_rules.GoalRule.Window(
            number=1,
            size=1,
            start=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
            end=dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc),
        ),
        counter='counter',
        steps=[],
        is_personal=False,
    )


def arbitrary_nmfg_rule(is_net: bool = True) -> subvention_rules.NmfgRule:
    return subvention_rules.NmfgRule(
        id='id',
        activity_points=100,
        budget_id='budget_id',
        group_id='group_id',
        is_net=is_net,
    )


def arbitrary_geo_booking_rule(
        id: str = 'geo_booking_rule_id',
        tariff_zone: str = 'moscow',
        start: dt.datetime = dt.datetime(2020, 6, 20, tzinfo=dt.timezone.utc),
        end: dt.datetime = dt.datetime(2022, 6, 20, tzinfo=dt.timezone.utc),
        rate_on_order_per_minute: Optional[decimal.Decimal] = None,
        rate_free_per_minute: Optional[decimal.Decimal] = None,
        budget_id: str = 'some_budget_id',
        is_relaxed_order_time_matching: bool = True,
        is_relaxed_income_matching: bool = True,
        local_days_of_week: Collection[consts.ISOWeekDay] = (
            consts.ISOWeekDay(2),
        ),
        workshift_start: dt.time = dt.time(10, 0),
        workshift_duration: dt.timedelta = dt.timedelta(hours=10),
        # driver constraints
        activity_points: Optional[float] = None,
        profile_payment_type_rule: Optional[
            consts.ProfilePaymentTypeRule
        ] = None,
        tariff_classes: Collection[str] = ('econom',),
        rule_type: str = 'add',
        min_online_minutes: int = 0,
) -> subvention_rules.GeoBookingRule:
    # pylint: disable=invalid-name, redefined-builtin
    return subvention_rules.GeoBookingRule(**locals())


def arbitrary_do_x_get_y_rule(
        id: str = 'id',
        group_id: str = 'group_id',
        activity_points: Optional[float] = None,
        is_personal: bool = False,
) -> subvention_rules.DoXGetYRule:
    # pylint: disable=invalid-name, redefined-builtin
    return subvention_rules.DoXGetYRule(**locals())


def arbitrary_single_ride_rule() -> subvention_rules.SingleRideRule:
    return subvention_rules.SingleRideRule(
        id='id', budget_id='budget_id', amount=decimal.Decimal(), is_geo=False,
    )


def arbitrary_single_on_top_rule() -> subvention_rules.SingleOnTopRule:
    return subvention_rules.SingleOnTopRule(
        id='id', budget_id='budget_id', amount=decimal.Decimal(), is_geo=False,
    )


def allowing_single_ride_req() -> rules.MatchRequest:
    return match_req()


@pytest.mark.parametrize(
    'match_request, expected_result',
    [
        (allowing_single_ride_req(), True),
        (match_req(need_dispatcher_acceptance=True), False),
        (match_req(is_single_ride_allowed=False), False),
        (match_req(order_status='cancelled'), False),
        (match_req(order_taxi_status='driving'), False),
        (match_req(closed_without_accept=True), False),
    ],
)
def test_single_ride_matching(match_request, expected_result):
    rule_data = arbitrary_single_ride_rule()
    rule = single_ride.SingleRideRule(rule_data)
    actual_result = rule.match(match_request)
    assert actual_result == expected_result


def allowing_single_on_top_req() -> rules.MatchRequest:
    return match_req()


@pytest.mark.parametrize(
    'match_request, expected_result',
    [
        (allowing_single_on_top_req(), True),
        (match_req(need_dispatcher_acceptance=True), False),
        (match_req(closed_without_accept=True), False),
        (match_req(is_single_on_top_allowed=False), False),
        (match_req(order_status='cancelled'), False),
        (match_req(order_taxi_status='driving'), False),
    ],
)
def test_single_on_top_matching(match_request, expected_result):
    rule_data = arbitrary_single_on_top_rule()
    rule = single_on_top.SingleOnTopRule(rule_data)
    actual_result = rule.match(match_request)
    assert actual_result == expected_result


def allowing_goal_req() -> rules.MatchRequest:
    return match_req()


def allowing_nmfg_req() -> rules.MatchRequest:
    return match_req()


def allowing_geo_booking_req() -> rules.MatchRequest:
    return match_req()


def allowing_do_x_get_y_req() -> rules.MatchRequest:
    return match_req()


@pytest.mark.parametrize(
    'match_request, expected_result',
    [
        (allowing_goal_req(), True),
        (match_req(need_dispatcher_acceptance=True), True),
        (match_req(is_goal_allowed=False), False),
        (match_req(order_status='cancelled'), False),
        (match_req(order_taxi_status='driving'), False),
    ],
)
def test_goal_matching(match_request, expected_result):
    rule_data = arbitrary_goal_rule()
    rule = goal.GoalRule(rule_data)
    actual_result = rule.match(match_request)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'match_request, expected_result',
    [
        (allowing_nmfg_req(), True),
        (match_req(need_dispatcher_acceptance=True), False),
        (match_req(closed_without_accept=True), False),
        (
            match_req(
                payment_type=consts.PaymentType.CORP, park_corp_vat=None,
            ),
            False,
        ),
    ],
)
def test_nmfg_matching(match_request, expected_result):
    rule_data = arbitrary_nmfg_rule()
    rule = nmfg.Rule(rule_data)
    actual = rule.match(match_request)
    assert actual == expected_result


@pytest.mark.parametrize(
    'match_request, expected_result',
    [
        (allowing_nmfg_req(), True),
        (match_req(need_dispatcher_acceptance=True), False),
        (match_req(closed_without_accept=True), False),
    ],
)
def test_geo_booking_matching(match_request, expected_result):
    rule_data = arbitrary_geo_booking_rule()
    rule = geo_booking.Rule(rule_data)
    actual = rule.match(match_request)
    assert actual == expected_result


@pytest.mark.parametrize(
    'match_request, expected_result',
    [
        (allowing_do_x_get_y_req(), True),
        (match_req(order_status='cancelled'), False),
        (match_req(order_taxi_status='transporting'), False),
        (match_req(need_dispatcher_acceptance=True), False),
        (match_req(closed_without_accept=True), False),
        (match_req(driver_activity_points=78), False),
    ],
)
def test_do_x_get_y_matching(match_request, expected_result):
    rule_data = arbitrary_do_x_get_y_rule(activity_points=79)
    rule = do_x_get_y.Rule(rule_data)
    actual = rule.match(match_request)
    assert actual == expected_result


def test_rule_maker_visitor():
    maker = rule_visitors.MakeFromRepoRule()
    goal_rule = arbitrary_goal_rule()
    nmfg_rule = arbitrary_nmfg_rule()
    single_ride_rule = arbitrary_single_ride_rule()
    single_on_top_rule = arbitrary_single_on_top_rule()
    geo_booking_rule = arbitrary_geo_booking_rule()
    do_x_get_y_rule = arbitrary_do_x_get_y_rule()
    maker.visit_goal(goal_rule)
    assert isinstance(maker.result, goal.GoalRule)
    maker.visit_single_ride(single_ride_rule)
    assert isinstance(maker.result, single_ride.SingleRideRule)
    maker.visit_single_on_top(single_on_top_rule)
    assert isinstance(maker.result, single_on_top.SingleOnTopRule)
    maker.visit_nmfg(nmfg_rule)
    assert isinstance(maker.result, nmfg.Rule)
    maker.visit_geo_booking(geo_booking_rule)
    assert isinstance(maker.result, geo_booking.Rule)
    maker.visit_do_x_get_y(do_x_get_y_rule)
    assert isinstance(maker.result, do_x_get_y.Rule)

    one = rule_visitors.MakeFromRepoRule.one(goal_rule)
    assert isinstance(one, goal.GoalRule)

    many = rule_visitors.MakeFromRepoRule.many(
        [
            goal_rule,
            single_ride_rule,
            single_on_top_rule,
            nmfg_rule,
            geo_booking_rule,
            do_x_get_y_rule,
        ],
    )
    assert isinstance(many[0], goal.GoalRule)
    assert isinstance(many[1], single_ride.SingleRideRule)
    assert isinstance(many[2], single_on_top.SingleOnTopRule)
    assert isinstance(many[3], nmfg.Rule)
    assert isinstance(many[4], geo_booking.Rule)
    assert isinstance(many[5], do_x_get_y.Rule)


def payment(
        kind: str,
        amount: str,
        should_charge_commission: bool,
        budget_id: str = 'budget_id',
        rule_db_id: str = 'id',
) -> rules.InstantPayment:
    return rules.InstantPayment(
        kind,
        decimal.Decimal(amount),
        budget_id,
        rule_db_id,
        should_charge_commission,
    )


@pytest.mark.parametrize(
    'order_cost, is_geo, amount, expected_result',
    [
        ('0', False, '0', payment('on_top', '0', False)),
        ('0', False, '100', payment('on_top', '100', False)),
        ('50', False, '100', payment('on_top', '100', False)),
        ('100', True, '100', payment('on_top_geo', '100', False)),
        ('200', False, '100', payment('on_top', '100', False)),
    ],
)
def test_single_on_top_instant_payments(
        order_cost, is_geo, amount, expected_result,
):
    rule_data = subvention_rules.SingleOnTopRule(
        id='id',
        budget_id='budget_id',
        amount=decimal.Decimal(amount),
        is_geo=is_geo,
    )
    rule = single_on_top.SingleOnTopRule(rule_data)
    actual_result = rule.get_instant_payment(decimal.Decimal(order_cost), 1)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'order_cost, is_geo, guarantee, expected_result',
    [
        ('0', False, '0', payment('mfg', '0', True)),
        ('0', False, '100', payment('mfg', '100', True)),
        ('50', False, '100', payment('mfg', '50', True)),
        ('100', True, '100', payment('mfg_geo', '0', True)),
        ('200', False, '100', payment('mfg', '0', True)),
    ],
)
def test_single_ride_instant_payments(
        order_cost, is_geo, guarantee, expected_result,
):
    rule_data = subvention_rules.SingleRideRule(
        id='id',
        budget_id='budget_id',
        amount=decimal.Decimal(guarantee),
        is_geo=is_geo,
    )
    rule = single_ride.SingleRideRule(rule_data)
    actual_result = rule.get_instant_payment(decimal.Decimal(order_cost), 1)
    assert actual_result == expected_result


def test_goal_instant_payments():
    rule_data = arbitrary_goal_rule()
    rule = goal.GoalRule(rule_data)
    actual_result = rule.get_instant_payment(decimal.Decimal(), 1)
    assert actual_result is None


def test_nmfg_instant_payments():
    rule_data = arbitrary_nmfg_rule()
    rule = nmfg.Rule(rule_data)
    actual_result = rule.get_instant_payment(decimal.Decimal(), 1)
    assert actual_result is None


def test_geo_booking_instant_payments():
    rule_data = arbitrary_geo_booking_rule()
    rule = geo_booking.Rule(rule_data)
    actual_result = rule.get_instant_payment(decimal.Decimal(), 1)
    assert actual_result is None


def test_single_ride_shifts():
    rule_data = arbitrary_single_ride_rule()
    rule = single_ride.SingleRideRule(rule_data)
    assert rule.get_shifts(make_get_shifts_request()) == []


def test_single_on_top_shifts():
    rule_data = arbitrary_single_on_top_rule()
    rule = single_on_top.SingleOnTopRule(rule_data)
    assert rule.get_shifts(make_get_shifts_request()) == []


def make_get_shifts_request_order(
        accepted_by_driver_at: dt.datetime = dt.datetime(
            2021, 7, 20, 15, tzinfo=dt.timezone.utc,
        ),
        completed_at: dt.datetime = dt.datetime(
            2021, 7, 20, 16, tzinfo=dt.timezone.utc,
        ),
        cost: decimal.Decimal = decimal.Decimal('100'),
        driver_with_promocode: bool = False,
        driver_with_workshift: bool = False,
        payment_type: consts.PaymentType = consts.PaymentType.CARD,
        status: str = 'finished',
        tariff_zone: str = 'kursk',
        taxi_status: str = 'complete',
        time_zone: str = 'Europe/Oslo',
        cost_for_driver: Optional[decimal.Decimal] = None,
        park_corp_vat: Optional[decimal.Decimal] = None,
        commission_limit_if_promocode: decimal.Decimal = decimal.Decimal('1'),
        counter_multiplier: int = 1,
        currency: str = 'RUB',
) -> rules.GetShiftsRequest.Order:
    # pylint: disable=invalid-name
    return rules.GetShiftsRequest.Order(**locals())


def make_get_shifts_request_driver(
        activity_points: Optional[float] = None,
        available_tariff_classes: Collection[str] = tuple(),
        profile_payment_type_restrictions: Optional[str] = None,
        unique_driver_id: str = 'udid',
        tariff_zone: str = 'kursk',
) -> rules.GetShiftsRequest.Driver:
    # pylint: disable=invalid-name
    return rules.GetShiftsRequest.Driver(**locals())


def make_get_shifts_request_contract(
        id_: int = 1, service_id: int = 111, firm_id: int = 42,
) -> rules.GetShiftsRequest.Contract:
    # pylint: disable=invalid-name
    return rules.GetShiftsRequest.Contract(id_, service_id, firm_id)


def make_get_shifts_request(
        order: rules.GetShiftsRequest.Order = (
            make_get_shifts_request_order()
        ),
        driver: rules.GetShiftsRequest.Driver = (
            make_get_shifts_request_driver()
        ),
        call_center_surcharge_inc_vat: Optional[decimal.Decimal] = None,
        subvention: decimal.Decimal = decimal.Decimal('0'),
        subvention_commission: decimal.Decimal = decimal.Decimal('0'),
        commissions: Collection[rules.GetShiftsRequest.Commission] = tuple(),
        discount: decimal.Decimal = decimal.Decimal('0'),
        contract: rules.GetShiftsRequest.Contract = (
            make_get_shifts_request_contract()
        ),
        ignore_order_income: bool = False,
        ignore_on_order_time: bool = False,
) -> rules.GetShiftsRequest:
    # pylint: disable=invalid-name
    return rules.GetShiftsRequest(**locals())


@pytest.mark.json_obj_hook(
    GoalRule=subvention_rules.GoalRule,
    GoalRuleStep=subvention_rules.GoalRule.Step,
    GoalRuleWindow=subvention_rules.GoalRule.Window,
    ActiveContract=models.ActiveContract,
    ShiftContract=models.ShiftContract,
    ShiftDriver=models.ShiftDriver,
    ShiftPaymentMeta=models.ShiftPaymentMeta,
    GoalRuleShift=equatable.codegen(models.GoalRuleShift),
    ServiceToContract=models.ServiceToContract,
    TaxiGoalShift=equatable.codegen(taxi_goal_shift.TaxiGoalShift),
    Shift=goal_shift.GoalShift,
    Agreement=goal_shift.GoalAgreement,
    GoalRuleData=goal_shift.GoalRuleData,
    GoalStepsItem=goal_shift.GoalStepsItem,
)
@pytest.mark.parametrize('test_data_json', ['test_goal_shift.json'])
def test_goal_shifts(test_data_json, *, load_py_json):
    test_data = load_py_json(test_data_json)
    rule_data = test_data['rule']
    rule = goal.GoalRule(rule_data)
    shifts = rule.get_shifts(make_get_shifts_request())
    assert len(shifts) == len(test_data['expected_shifts'])
    for shift, expected_shift in zip(shifts, test_data['expected_shifts']):
        expected_shift_properties = expected_shift['shift_properties']
        assert shift.shift_id == expected_shift_properties['shift_id']
        assert shift.version == expected_shift_properties['version']
        assert shift.topic == expected_shift_properties['topic']
        assert shift.kind == expected_shift_properties['kind']
        assert shift.process_at == expected_shift_properties['process_at']
        assert shift.stq_name == expected_shift_properties['stq_name']
        assert (
            shift.get_tags('Europe/Moscow')
            == expected_shift_properties['tags']
        )
        assert shift.get_taxi_order_data() == expected_shift['shift_data']

        payment_meta = test_data['payment_meta']
        driver = test_data['driver']
        assert (
            shift.get_taxi_shift(
                [models.ActiveContract(id=1, currency='RUB', firm_id=42)],
                driver,
                payment_meta,
            )
            == expected_shift['taxi_shift']
        )


_CommissionGroup = consts.CommissionGroup
_Commission = rules.GetShiftsRequest.Commission


@pytest.mark.parametrize(
    'query, rule_data, expected_result',
    [
        (
            make_get_shifts_request(),
            arbitrary_nmfg_rule(),
            models.NmfgRuleShift(
                kind='nmfg',
                income='100.0000',
                num_orders=1,
                rule_group_id='group_id',
            ),
        ),
        (
            make_get_shifts_request(
                order=make_get_shifts_request_order(
                    status='cancelled', payment_type=consts.PaymentType.CASH,
                ),
            ),
            arbitrary_nmfg_rule(),
            None,
        ),
        (
            make_get_shifts_request(
                order=make_get_shifts_request_order(taxi_status='finished'),
            ),
            arbitrary_nmfg_rule(),
            models.NmfgRuleShift(
                kind='nmfg', rule_group_id='group_id', income='100.0000',
            ),
        ),
        (
            make_get_shifts_request(
                order=make_get_shifts_request_order(
                    driver_with_promocode=True,
                ),
            ),
            arbitrary_nmfg_rule(),
            models.NmfgRuleShift(
                kind='nmfg',
                rule_group_id='group_id',
                income='100.0000',
                num_orders=1,
                num_orders_per_promocode=1,
                promocode_commission='1.0000',
            ),
        ),
        (
            make_get_shifts_request(
                order=make_get_shifts_request_order(
                    driver_with_workshift=True,
                ),
            ),
            arbitrary_nmfg_rule(),
            models.NmfgRuleShift(
                kind='nmfg',
                rule_group_id='group_id',
                income='100.0000',
                num_orders=1,
                num_orders_per_workshift=1,
            ),
        ),
        (
            make_get_shifts_request(
                order=make_get_shifts_request_order(
                    driver_with_promocode=True, driver_with_workshift=True,
                ),
            ),
            arbitrary_nmfg_rule(),
            models.NmfgRuleShift(
                kind='nmfg',
                rule_group_id='group_id',
                income='100.0000',
                num_orders=1,
                num_orders_per_workshift=1,
            ),
        ),
        (
            make_get_shifts_request(subvention=decimal.Decimal('10')),
            arbitrary_nmfg_rule(),
            models.NmfgRuleShift(
                kind='nmfg',
                rule_group_id='group_id',
                income='100.0000',
                subvention_income='10.0000',
                num_orders=1,
            ),
        ),
        (
            make_get_shifts_request(
                subvention=decimal.Decimal('10'),
                subvention_commission=decimal.Decimal('1'),
            ),
            arbitrary_nmfg_rule(),
            models.NmfgRuleShift(
                kind='nmfg',
                rule_group_id='group_id',
                income='100.0000',
                subvention_income='10.0000',
                subvention_commission='1.0000',
                num_orders=1,
            ),
        ),
        (
            make_get_shifts_request(
                commissions=[
                    _Commission(_TEN, _ONE, _CommissionGroup.ACQUIRING),
                    _Commission(_TEN, _ONE, _CommissionGroup.BASE),
                    _Commission(_TEN, _ONE, _CommissionGroup.TAXIMETER),
                    _Commission(_TEN, _ONE, _CommissionGroup.CALL_CENTER),
                ],
            ),
            arbitrary_nmfg_rule(is_net=True),
            models.NmfgRuleShift(
                kind='nmfg',
                rule_group_id='group_id',
                commission='44.0000',
                income='100.0000',
                num_orders=1,
            ),
        ),
        (
            make_get_shifts_request(
                commissions=[
                    _Commission(
                        _TEN, _ONE, _CommissionGroup.SOFTWARE_SUBSCRIPTION,
                    ),
                ],
                call_center_surcharge_inc_vat=decimal.Decimal(10),
            ),
            arbitrary_nmfg_rule(is_net=True),
            models.NmfgRuleShift(
                kind='nmfg',
                rule_group_id='group_id',
                income='100.0000',
                num_orders=1,
            ),
        ),
        pytest.param(
            make_get_shifts_request(
                commissions=[_Commission(_TEN, _ONE, _CommissionGroup.BASE)],
                call_center_surcharge_inc_vat=decimal.Decimal(10),
            ),
            arbitrary_nmfg_rule(is_net=False),
            models.NmfgRuleShift(
                kind='nmfg',
                rule_group_id='group_id',
                income='90.0000',
                num_orders=1,
            ),
            id='ignore commission for not `NET` rules',
        ),
        (
            make_get_shifts_request(discount=_TEN),
            arbitrary_nmfg_rule(is_net=False),
            models.NmfgRuleShift(
                kind='nmfg',
                rule_group_id='group_id',
                income='100.0000',
                subvention_income='10.0000',
                num_orders=1,
            ),
        ),
    ],
)
def test_nmfg_shift_get_taxi_order_data_with_commissions(
        query, rule_data, expected_result,
):
    rule = nmfg.Rule(rule_data)
    shift = more_itertools.only(rule.get_shifts(query))
    actual = shift.get_taxi_order_data() if shift else None
    if actual and expected_result:
        assert actual.serialize() == expected_result.serialize()
    else:
        assert not actual and not expected_result


@pytest.mark.parametrize(
    'rule_data, query, expected',
    [
        (
            arbitrary_geo_booking_rule(),
            make_get_shifts_request(),
            models.GeoBookingRuleShift(
                kind='geo_booking',
                income='100.0000',
                rule_id='geo_booking_rule_id',
            ),
        ),
        # income
        (
            arbitrary_geo_booking_rule(),
            make_get_shifts_request(
                order=make_get_shifts_request_order(
                    payment_type=consts.PaymentType.CASH, status='cancelled',
                ),
            ),
            None,
        ),
        (
            arbitrary_geo_booking_rule(is_relaxed_income_matching=True),
            make_get_shifts_request(),
            models.GeoBookingRuleShift(
                kind='geo_booking',
                income='100.0000',
                rule_id='geo_booking_rule_id',
            ),
        ),
        (
            arbitrary_geo_booking_rule(
                is_relaxed_income_matching=False, tariff_classes=('econom',),
            ),
            make_get_shifts_request(
                driver=make_get_shifts_request_driver(
                    available_tariff_classes=('business',),
                ),
            ),
            None,
        ),
        (
            arbitrary_geo_booking_rule(
                is_relaxed_income_matching=False, tariff_classes=('econom',),
            ),
            make_get_shifts_request(
                driver=make_get_shifts_request_driver(
                    available_tariff_classes=('business', 'econom'),
                ),
            ),
            models.GeoBookingRuleShift(
                kind='geo_booking',
                income='100.0000',
                rule_id='geo_booking_rule_id',
            ),
        ),
        (
            arbitrary_geo_booking_rule(
                is_relaxed_income_matching=False, activity_points=80,
            ),
            make_get_shifts_request(
                driver=make_get_shifts_request_driver(activity_points=79),
            ),
            None,
        ),
        (
            arbitrary_geo_booking_rule(
                is_relaxed_income_matching=False,
                profile_payment_type_rule=consts.ProfilePaymentTypeRule.CASH,
            ),
            make_get_shifts_request(
                driver=make_get_shifts_request_driver(
                    profile_payment_type_restrictions='online',
                ),
            ),
            None,
        ),
        # on order time
        (
            arbitrary_geo_booking_rule(rate_on_order_per_minute=_TEN),
            make_get_shifts_request(),
            models.GeoBookingRuleShift(
                kind='geo_booking',
                income='100.0000',
                on_order_time='60.0000',
                rule_id='geo_booking_rule_id',
            ),
        ),
        pytest.param(
            arbitrary_geo_booking_rule(
                rate_on_order_per_minute=_TEN,
                is_relaxed_income_matching=False,
                is_relaxed_order_time_matching=False,
                activity_points=80,
            ),
            make_get_shifts_request(
                driver=make_get_shifts_request_driver(activity_points=79),
            ),
            None,
            id='Score nothing due to strict matching',
        ),
        pytest.param(
            arbitrary_geo_booking_rule(
                rate_on_order_per_minute=_TEN,
                is_relaxed_income_matching=True,
                is_relaxed_order_time_matching=False,
                activity_points=80,
            ),
            make_get_shifts_request(
                driver=make_get_shifts_request_driver(activity_points=79),
            ),
            models.GeoBookingRuleShift(
                kind='geo_booking',
                income='100.0000',
                on_order_time='60.0000',
                rule_id='geo_booking_rule_id',
            ),
            id='Score time because of income matching',
        ),
        pytest.param(
            arbitrary_geo_booking_rule(
                rate_on_order_per_minute=_TEN,
                start=dt.datetime(2021, 7, 20, 15, 15, tzinfo=dt.timezone.utc),
                end=dt.datetime(2021, 7, 20, 15, 45, tzinfo=dt.timezone.utc),
            ),
            make_get_shifts_request(
                order=make_get_shifts_request_order(
                    accepted_by_driver_at=dt.datetime(
                        2021, 7, 20, 15, tzinfo=dt.timezone.utc,
                    ),
                    completed_at=dt.datetime(
                        2021, 7, 20, 16, tzinfo=dt.timezone.utc,
                    ),
                ),
            ),
            models.GeoBookingRuleShift(
                kind='geo_booking',
                income='100.0000',
                on_order_time='30.0000',
                rule_id='geo_booking_rule_id',
            ),
            id='rule bounds reduces scored time',
        ),
        pytest.param(
            arbitrary_geo_booking_rule(
                rate_on_order_per_minute=_TEN,
                start=dt.datetime(2021, 7, 20, 15, 15, tzinfo=dt.timezone.utc),
                end=dt.datetime(2021, 7, 20, 15, 45, tzinfo=dt.timezone.utc),
            ),
            make_get_shifts_request(
                order=make_get_shifts_request_order(
                    accepted_by_driver_at=dt.datetime(
                        2021, 7, 20, 15, tzinfo=dt.timezone.utc,
                    ),
                    completed_at=dt.datetime(
                        2021, 7, 20, 16, tzinfo=dt.timezone.utc,
                    ),
                ),
                ignore_on_order_time=False,
                ignore_order_income=True,
            ),
            models.GeoBookingRuleShift(
                kind='geo_booking',
                on_order_time='30.0000',
                rule_id='geo_booking_rule_id',
            ),
            id='rule bounds reduces scored time',
        ),
        pytest.param(
            arbitrary_geo_booking_rule(
                rate_on_order_per_minute=_TEN,
                start=dt.datetime(2021, 7, 20, 15, 15, tzinfo=dt.timezone.utc),
                end=dt.datetime(2021, 7, 20, 15, 45, tzinfo=dt.timezone.utc),
            ),
            make_get_shifts_request(
                order=make_get_shifts_request_order(
                    accepted_by_driver_at=dt.datetime(
                        2021, 7, 20, 15, tzinfo=dt.timezone.utc,
                    ),
                    completed_at=dt.datetime(
                        2021, 7, 20, 16, tzinfo=dt.timezone.utc,
                    ),
                ),
                ignore_on_order_time=True,
                ignore_order_income=False,
            ),
            models.GeoBookingRuleShift(
                kind='geo_booking',
                income='100.0000',
                rule_id='geo_booking_rule_id',
            ),
            id='rule bounds reduces scored time',
        ),
        pytest.param(
            arbitrary_geo_booking_rule(
                rate_on_order_per_minute=_TEN,
                workshift_start=dt.time(17, 15),
                workshift_duration=dt.timedelta(minutes=30),
            ),
            make_get_shifts_request(
                order=make_get_shifts_request_order(
                    accepted_by_driver_at=dt.datetime(
                        2021, 7, 20, 1, tzinfo=dt.timezone.utc,
                    ),
                    completed_at=dt.datetime(
                        2021, 7, 20, 16, tzinfo=dt.timezone.utc,
                    ),
                ),
            ),
            models.GeoBookingRuleShift(
                kind='geo_booking',
                income='100.0000',
                on_order_time='30.0000',
                rule_id='geo_booking_rule_id',
            ),
            id='workshift reduces scored time',
        ),
        pytest.param(
            arbitrary_geo_booking_rule(
                rate_on_order_per_minute=_TEN,
                local_days_of_week=(consts.ISOWeekDay(1),),
            ),
            make_get_shifts_request(),
            models.GeoBookingRuleShift(
                kind='geo_booking',
                income='100.0000',
                rule_id='geo_booking_rule_id',
            ),
            id='active day does not match',
        ),
        pytest.param(
            arbitrary_geo_booking_rule(),
            make_get_shifts_request(subvention=decimal.Decimal('10')),
            models.GeoBookingRuleShift(
                kind='geo_booking',
                income='100.0000',
                subvention_income='10.0000',
                rule_id='geo_booking_rule_id',
            ),
            id='with instant payments',
        ),
        pytest.param(
            arbitrary_geo_booking_rule(),
            make_get_shifts_request(discount=decimal.Decimal('10')),
            models.GeoBookingRuleShift(
                kind='geo_booking',
                income='100.0000',
                subvention_income='10.0000',
                rule_id='geo_booking_rule_id',
            ),
            id='with discount',
        ),
    ],
)
def test_geo_booking_shift_get_taxi_order_data(rule_data, query, expected):
    rule = geo_booking.Rule(rule_data)
    shift = more_itertools.only(rule.get_shifts(query))
    actual = shift.get_taxi_order_data() if shift else None

    actual_to_compare = actual.serialize() if actual else None
    expected_to_compare = expected.serialize() if expected else None
    assert actual_to_compare == expected_to_compare


def test_do_x_get_y_shift_get_taxi_order_data():
    rule_data = arbitrary_do_x_get_y_rule()
    query = make_get_shifts_request()

    rule = do_x_get_y.Rule(rule_data)
    shift = more_itertools.one(rule.get_shifts(query))
    actual = shift.get_taxi_order_data()
    expected = models.DoXGetYRuleShift(
        kind='do_x_get_y',
        num_orders=1,
        rule_group_id='group_id',
        is_personal=False,
    )
    assert actual.serialize() == expected.serialize()
