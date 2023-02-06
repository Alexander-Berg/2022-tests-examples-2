import dataclasses
import datetime as dt
import decimal

import attr
from dateutil import tz
import pytest

from taxi import billing
from taxi.billing.util import dates

from taxi_billing_subventions.common import intervals
from taxi_billing_subventions.common import models
from test_taxi_billing_subventions import factories
from test_taxi_billing_subventions import helpers


def _parse_interval(interval: dict) -> models.DriverFixRateInterval:
    return models.DriverFixRateInterval(
        starts_at=factories.make_df_rate_interval_endpoint(
            interval['starts_at'],
        ),
        rate_per_minute=decimal.Decimal(interval['rate_per_minute']),
    )


@pytest.mark.parametrize(
    'start, end, rate_intervals, tz_id, shift_start,'
    'shift_end, expected_paid_intervals',
    [
        (
            '2019-11-01T00:00:00+00:00',
            '2019-11-30T00:00:00+00:00',
            {1: {'starts_at': 'Mon 01:00', 'rate_per_minute': '1'}},
            'Europe/Moscow',
            '2019-11-10T00:00:00+00:00',
            '2019-11-11T00:00:00+00:00',
            [
                {
                    'start': '2019-11-10T00:00:00+00:00',
                    'end': '2019-11-11T01:00:00+03:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2019-11-11T01:00:00+03:00',
                    'end': '2019-11-11T00:00:00+00:00',
                    'rate_interval': 1,
                },
            ],
        ),
        pytest.param(
            '2019-11-01T00:00:00+00:00',
            '2019-11-30T00:00:00+00:00',
            {
                1: {'starts_at': 'Mon 01:00', 'rate_per_minute': '1'},
                2: {'starts_at': 'Tue 02:00', 'rate_per_minute': '2'},
                3: {'starts_at': 'Wed 03:00', 'rate_per_minute': '3'},
                4: {'starts_at': 'Thu 04:00', 'rate_per_minute': '4'},
                5: {'starts_at': 'Fri 05:00', 'rate_per_minute': '5'},
                6: {'starts_at': 'Sat 06:00', 'rate_per_minute': '6'},
                7: {'starts_at': 'Sun 07:00', 'rate_per_minute': '7'},
            },
            'Europe/Moscow',
            '2019-11-10T00:00:00+03:00',
            '2019-11-20T00:00:00+03:00',
            [
                {
                    'start': '2019-11-10T00:00:00+03:00',
                    'end': '2019-11-10T07:00:00+03:00',
                    'rate_interval': 6,
                },
                {
                    'start': '2019-11-10T07:00:00+03:00',
                    'end': '2019-11-11T01:00:00+03:00',
                    'rate_interval': 7,
                },
                {
                    'start': '2019-11-11T01:00:00+03:00',
                    'end': '2019-11-12T02:00:00+03:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2019-11-12T02:00:00+03:00',
                    'end': '2019-11-13T03:00:00+03:00',
                    'rate_interval': 2,
                },
                {
                    'start': '2019-11-13T03:00:00+03:00',
                    'end': '2019-11-14T04:00:00+03:00',
                    'rate_interval': 3,
                },
                {
                    'start': '2019-11-14T04:00:00+03:00',
                    'end': '2019-11-15T05:00:00+03:00',
                    'rate_interval': 4,
                },
                {
                    'start': '2019-11-15T05:00:00+03:00',
                    'end': '2019-11-16T06:00:00+03:00',
                    'rate_interval': 5,
                },
                {
                    'start': '2019-11-16T06:00:00+03:00',
                    'end': '2019-11-17T07:00:00+03:00',
                    'rate_interval': 6,
                },
                {
                    'start': '2019-11-17T07:00:00+03:00',
                    'end': '2019-11-18T01:00:00+03:00',
                    'rate_interval': 7,
                },
                {
                    'start': '2019-11-18T01:00:00+03:00',
                    'end': '2019-11-19T02:00:00+03:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2019-11-19T02:00:00+03:00',
                    'end': '2019-11-20T00:00:00+03:00',
                    'rate_interval': 2,
                },
            ],
            id='Every weekday',
        ),
        pytest.param(
            '2019-11-02T00:00:00+00:00',
            '2019-11-03T00:00:00+00:00',
            {1: {'starts_at': 'Fri 03:01', 'rate_per_minute': '1'}},
            'Europe/Moscow',
            '2019-11-01T00:00:00+00:00',
            '2019-11-02T00:00:00+00:00',
            [],
            id='Shift just before rule',
        ),
        pytest.param(
            '2019-11-01T00:00:00+00:00',
            '2019-11-02T00:00:00+00:00',
            {1: {'starts_at': 'Fri 03:01', 'rate_per_minute': '1'}},
            'Europe/Moscow',
            '2019-11-02T00:00:00+00:00',
            '2019-11-03T00:00:00+00:00',
            [],
            id='Shift just after rule',
        ),
        pytest.param(
            '2019-11-01T00:00:00+00:00',
            '2019-11-02T00:00:00+00:00',
            {
                1: {'starts_at': 'Fri 04:00', 'rate_per_minute': '1'},
                2: {'starts_at': 'Fri 05:00', 'rate_per_minute': '2'},
            },
            'Europe/Moscow',
            '2019-11-01T04:00:00+03:00',
            '2019-11-01T05:00:00+03:00',
            [
                {
                    'start': '2019-11-01T04:00:00+03:00',
                    'end': '2019-11-01T05:00:00+03:00',
                    'rate_interval': 1,
                },
            ],
            id='Shift covers whole interval',
        ),
        pytest.param(
            '2019-11-01T04:00:00+03:00',
            '2019-11-10T00:00:00+03:00',
            {1: {'starts_at': 'Fri 04:01', 'rate_per_minute': '1'}},
            'Europe/Moscow',
            '2019-11-01T04:00:00+03:00',
            '2019-11-01T04:01:00+03:00',
            [
                {
                    'start': '2019-11-01T04:00:00+03:00',
                    'end': '2019-11-01T04:01:00+03:00',
                    'rate_interval': 1,
                },
            ],
            id='Shift is before first interval of the week',
        ),
        pytest.param(
            '2019-03-31T00:00:00+00:00',
            '2019-04-01T00:00:00+01:00',
            {
                1: {'starts_at': 'Sun 00:00', 'rate_per_minute': '1'},
                2: {'starts_at': 'Sun 01:00', 'rate_per_minute': '2'},
                3: {'starts_at': 'Sun 01:30', 'rate_per_minute': '3'},
                4: {'starts_at': 'Sun 01:59', 'rate_per_minute': '4'},
                5: {'starts_at': 'Sun 03:00', 'rate_per_minute': '5'},
            },
            'Europe/London',
            '2019-03-31T00:30:00+00:00',
            '2019-03-31T02:30:00+01:00',
            [
                {
                    'start': '2019-03-31T00:30:00+00:00',
                    'end': '2019-03-31T02:00:00+01:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2019-03-31T02:00:00+01:00',
                    'end': '2019-03-31T02:30:00+01:00',
                    'rate_interval': 4,
                },
            ],
            id='Shift covers non-existent time period',
            marks=[pytest.mark.skip(reason='Not implemented')],
        ),
        pytest.param(
            '2019-10-27T00:00:00+01:00',
            '2019-10-28T00:00:00+00:00',
            {
                1: {'starts_at': 'Sun 00:00', 'rate_per_minute': '1'},
                2: {'starts_at': 'Sun 01:00', 'rate_per_minute': '2'},
                3: {'starts_at': 'Sun 01:30', 'rate_per_minute': '3'},
                4: {'starts_at': 'Sun 02:00', 'rate_per_minute': '4'},
                5: {'starts_at': 'Sun 03:00', 'rate_per_minute': '5'},
            },
            'Europe/London',
            '2019-10-27T00:30:00+01:00',
            '2019-10-27T02:30:00+00:00',
            [
                {
                    'start': '2019-10-27T00:30:00+01:00',
                    'end': '2019-10-27T01:00:00+01:00',
                    'rate_interval': 1,
                },
                {
                    'start': '2019-10-27T01:00:00+01:00',
                    'end': '2019-10-27T01:30:00+01:00',
                    'rate_interval': 2,
                },
                {
                    'start': '2019-10-27T01:30:00+01:00',
                    'end': '2019-10-27T01:00:00+00:00',
                    'rate_interval': 3,
                },
                {
                    'start': '2019-10-27T01:00:00+00:00',
                    'end': '2019-10-27T01:30:00+00:00',
                    'rate_interval': 2,
                },
                {
                    'start': '2019-10-27T01:30:00+00:00',
                    'end': '2019-10-27T02:00:00+00:00',
                    'rate_interval': 3,
                },
                {
                    'start': '2019-10-27T02:00:00+00:00',
                    'end': '2019-10-27T02:30:00+00:00',
                    'rate_interval': 4,
                },
            ],
            id='Shift covers ambiguous time period',
            marks=[pytest.mark.skip(reason='Not implemented')],
        ),
    ],
)
@pytest.mark.nofilldb()
def test_rate_schedule(
        start,
        end,
        rate_intervals,
        tz_id,
        shift_start,
        shift_end,
        expected_paid_intervals,
):
    start = dates.parse_datetime(start)
    end = dates.parse_datetime(end)
    rate_intervals = {
        id_: _parse_interval(interval)
        for id_, interval in rate_intervals.items()
    }
    tzinfo = tz.gettz(tz_id)
    rates = models.DriverFixRates(
        start, end, list(rate_intervals.values()), tzinfo,
    )
    shift_start = dates.parse_datetime(shift_start)
    shift_end = dates.parse_datetime(shift_end)
    paid_intervals = rates.get_paid_intervals(shift_start, shift_end)

    expected_paid_intervals = [
        models.DriverFixPaidInterval(
            start=dates.parse_datetime(interval['start']),
            end=dates.parse_datetime(interval['end']),
            rate_interval=rate_intervals[interval['rate_interval']],
        )
        for interval in expected_paid_intervals
    ]

    assert paid_intervals == expected_paid_intervals


@pytest.mark.parametrize(
    'test_data_json',
    [
        'partial_time_fit.json',
        'unfit_geoareas.json',
        'unfit_event_start.json',
        'unfit_profile_tariff_classes.json',
        'unfit_profile_payment_type_restrictions.json',
    ],
)
@pytest.mark.nofilldb()
def test_on_driver_geoarea_activity(test_data_json, load_py_json_dir):
    test_data: dict = load_py_json_dir(
        'test_on_driver_geoarea_activity', test_data_json,
    )
    rule = test_data['rule']
    event = test_data['event']
    driver_mode_context = test_data['driver_mode_context']
    expected_event_handled = test_data['expected_event_handled']
    actual_event_handled = rule.on_driver_geoarea_activity(
        doc=event, driver_mode=driver_mode_context, log_extra=None,
    )
    assert actual_event_handled == expected_event_handled


@pytest.mark.parametrize(
    'test_data_json',
    [
        'partial_time_fit.json',
        'unfit_event_start.json',
        'unfit_cancelled_by_cash.json',
        'unfit_closed_without_accept.json',
        'unfit_completed_by_dispatcher.json',
    ],
)
@pytest.mark.nofilldb()
def test_on_order_ready_for_billing(test_data_json, load_py_json_dir):
    test_data = load_py_json_dir(
        'test_on_order_ready_for_billing', test_data_json,
    )
    rule = test_data['rule']
    event = test_data['event']
    expected_event_handled = test_data['expected_event_handled']
    actual_event_handled = rule.on_order_ready_for_billing(
        doc=event,
        level=models.PaymentLevel.zero(event.order.currency),
        balances=[],
        driver_mode=models.DriverModeContext(None),
        log_extra=None,
    )
    assert attr.asdict(actual_event_handled.journal) == attr.asdict(
        expected_event_handled.journal,
    )
    assert actual_event_handled == expected_event_handled


@pytest.mark.parametrize(
    'rule_json, balances_json, expected_json',
    [
        (
            'rule.json',
            'empty_balances.json',
            'expected_no_fulfilled_goal_fulfilled.json',
        ),
        (
            'rule.json',
            'balances_for_commission.json',
            'expected_goal_fulfilled_with_commission.json',
        ),
        (
            'rule.json',
            'balances_for_subvention.json',
            'expected_goal_fulfilled_with_subvention.json',
        ),
        (
            'rule.json',
            'balances_with_discounts_and_promocodes.json',
            'expected_goal_fulfilled_with_discounts_and_promocodes.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_goal_fulfilled(
        rule_json, balances_json, expected_json, load_py_json_dir,
):
    rule, balances, expected = load_py_json_dir(
        'test_goal_fulfilled', rule_json, balances_json, expected_json,
    )
    actual_goal_fulfilled = rule.get_goal_fulfilled(balances)
    assert dataclasses.asdict(actual_goal_fulfilled) == dataclasses.asdict(
        expected,
    )


@pytest.mark.parametrize(
    'rule_json, event_at_str, shift_close_time_str, expected_interval_str',
    [
        (
            'rule.json',
            '2019-12-04T00:00:00+03:00',
            '00:00:00+03:00',
            ['2019-12-04T00:00:00+03:00', '2019-12-05T00:00:00+03:00'],
        ),
        (
            'rule.json',
            '2019-12-04T23:59:00+03:00',
            '00:00:00+03:00',
            ['2019-12-04T00:00:00+03:00', '2019-12-05T00:00:00+03:00'],
        ),
        (
            'rule.json',
            '2019-12-04T12:00:00+03:00',
            '00:00:00+03:00',
            ['2019-12-04T00:00:00+03:00', '2019-12-05T00:00:00+03:00'],
        ),
        (
            'rule.json',
            '2019-12-04T00:00:00+03:00',
            '00:00:00+02:00',
            ['2019-12-03T00:00:00+02:00', '2019-12-04T00:00:00+02:00'],
        ),
        (
            'rule.json',
            '2019-12-04T23:59:00+03:00',
            '00:00:00+02:00',
            ['2019-12-04T00:00:00+02:00', '2019-12-05T00:00:00+02:00'],
        ),
        (
            'rule.json',
            '2019-12-04T12:00:00+03:00',
            '00:00:00+02:00',
            ['2019-12-04T00:00:00+02:00', '2019-12-05T00:00:00+02:00'],
        ),
        (
            'rule.json',
            '2019-12-04T12:00:00+00:00',
            '13:00:00+00:00',
            ['2019-12-03T13:00:00+00:00', '2019-12-04T13:00:00+00:00'],
        ),
        (
            'rule.json',
            '2019-12-04T12:00:00+00:00',
            '11:00:00+00:00',
            ['2019-12-04T11:00:00+00:00', '2019-12-05T11:00:00+00:00'],
        ),
        (
            'rule.json',
            '2019-12-04T12:00:00+00:00',
            '12:00:00+00:00',
            ['2019-12-04T12:00:00+00:00', '2019-12-05T12:00:00+00:00'],
        ),
        (
            'rule.json',
            '2019-12-04T12:00:00+00:00',
            None,
            ['2019-12-04T00:00:00+03:00', '2019-12-05T00:00:00+03:00'],
        ),
        (
            'rule.json',
            '2019-12-04T12:00:00+00:00',
            None,
            ['2019-12-04T00:00:00+03:00', '2019-12-05T00:00:00+03:00'],
        ),
        (
            'rule.json',
            '2019-12-04T23:00:00+03:00',
            '00:00:00+04:00',
            ['2019-12-05T00:00:00+04:00', '2019-12-06T00:00:00+04:00'],
        ),
    ],
)
@pytest.mark.nofilldb()
def test_get_shift_interval(
        load_py_json_dir,
        rule_json,
        event_at_str,
        shift_close_time_str,
        expected_interval_str,
):
    rule: models.DriverFixRule = load_py_json_dir(
        'test_get_shift_interval', rule_json,
    )
    shift_close_time = (
        None
        if not shift_close_time_str
        else dt.datetime.strptime(shift_close_time_str, '%H:%M:%S%z').timetz()
    )
    event_at = dates.parse_datetime(event_at_str)
    interval = rule.get_shift_interval(event_at, shift_close_time)
    start_str, end_str = expected_interval_str
    start = dates.parse_datetime(start_str)
    end = dates.parse_datetime(end_str)
    expected_interval = intervals.closed_open(start, end)
    assert interval == expected_interval


@pytest.mark.parametrize(
    'rule_json, event_at_str, shift_close_time_str, expected_datetime_str',
    [
        (
            'rule.json',
            '2019-12-04T12:00:00+00:00',
            '13:00:00+00:00',
            '2019-12-04T17:00:00+00:00',
        ),
        (
            'rule.json',
            '2019-12-04T12:00:00+00:00',
            '11:00:00+00:00',
            '2019-12-05T15:00:00+00:00',
        ),
        (
            'rule.json',
            '2019-12-04T12:00:00+00:00',
            None,
            '2019-12-05T04:00:00+03:00',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_get_payment_time(
        load_py_json_dir,
        rule_json,
        event_at_str,
        shift_close_time_str,
        expected_datetime_str,
):
    rule: models.DriverFixRule = load_py_json_dir(
        'test_get_payment_time', rule_json,
    )
    shift_close_time = (
        None
        if not shift_close_time_str
        else dt.datetime.strptime(shift_close_time_str, '%H:%M:%S%z').timetz()
    )
    event_at = dates.parse_datetime(event_at_str)
    actual = rule.get_payment_time(event_at, shift_close_time)
    expected = dates.parse_datetime(expected_datetime_str)
    assert actual == expected


@pytest.mark.parametrize(
    'rule_json, event_at_str, shift_close_time_str, expected_date_str',
    [
        (
            'rule.json',
            '2019-12-04T12:00:00+00:00',
            '13:00:00+00:00',
            '2019-12-04',
        ),
        (
            'rule.json',
            '2019-12-04T10:00:00+03:00',
            '11:00:00+03:00',
            '2019-12-03',
        ),
        (
            'rule.json',
            '2019-12-04T12:00:00+03:00',
            '11:00:00+03:00',
            '2019-12-04',
        ),
        ('rule.json', '2019-12-04T12:00:00+03:00', None, '2019-12-04'),
    ],
)
@pytest.mark.nofilldb()
def test_get_antifraud_shift_date(
        load_py_json_dir,
        rule_json,
        event_at_str,
        shift_close_time_str,
        expected_date_str,
):
    rule: models.DriverFixRule = load_py_json_dir(
        'test_get_antifraud_shift_date', rule_json,
    )
    shift_close_time = (
        None
        if not shift_close_time_str
        else dt.datetime.strptime(shift_close_time_str, '%H:%M:%S%z').timetz()
    )
    event_at = dates.parse_datetime(event_at_str)
    actual = rule.get_antifraud_shift_date(event_at, shift_close_time)
    expected = dates.parse_date(expected_date_str)
    assert actual == expected


@dataclasses.dataclass(frozen=True)
class CommissionIfFraudInput:
    currency: str
    guarantee_on_order: decimal.Decimal
    income: decimal.Decimal
    vat_rate: decimal.Decimal
    commission_rate_if_fraud: decimal.Decimal


def make_goal_fulfilled_if_fraud(
        commission_input: CommissionIfFraudInput,
) -> models.DriverFixGoalFulfilled:
    zero = billing.Money.zero(commission_input.currency)
    return models.DriverFixGoalFulfilled(
        is_fulfilled=True,
        agreement_id='agreement_id',
        bonus=zero,
        guarantee=zero,
        guarantee_on_order=billing.Money(
            commission_input.guarantee_on_order, commission_input.currency,
        ),
        income=billing.Money(
            commission_input.income, commission_input.currency,
        ),
        on_order_minutes=decimal.Decimal(0),
        free_minutes=decimal.Decimal(0),
        identity=models.rule.Identity('identity'),
        cash_income=zero,
        cash_commission=zero,
        discounts=zero,
        promocodes_marketing=zero,
        promocodes_support=zero,
    )


@pytest.mark.parametrize(
    'commission_input, expected',
    [
        pytest.param(
            CommissionIfFraudInput(
                currency='RUB',
                guarantee_on_order=decimal.Decimal('13'),
                income=decimal.Decimal('20'),
                vat_rate=decimal.Decimal('1.2'),
                commission_rate_if_fraud=decimal.Decimal('0.3'),
            ),
            models.DriverFixGoalFulfilled.Commission(
                value=helpers.money('6.8333333 RUB'),
                vat=helpers.money('1.3666667 RUB'),
                income_for_park_commission=helpers.money('20 RUB'),
            ),
            id='Use income commission '
            'if it\'s greater than guarantee commission',
        ),
        pytest.param(
            CommissionIfFraudInput(
                currency='RUB',
                guarantee_on_order=decimal.Decimal('4'),
                income=decimal.Decimal('15'),
                vat_rate=decimal.Decimal('1'),
                commission_rate_if_fraud=decimal.Decimal('0.5'),
            ),
            models.DriverFixGoalFulfilled.Commission(
                value=helpers.money('12 RUB'),
                vat=helpers.money('0 RUB'),
                income_for_park_commission=helpers.money('4 RUB'),
            ),
            id='Use guarantee commission if '
            'it\'s greater than income commission',
        ),
    ],
)
def test_get_commission_if_fraud(
        decimal_prec_8,
        *,
        commission_input: CommissionIfFraudInput,
        expected: models.DriverFixGoalFulfilled.Commission,
):
    goal_fulfilled = make_goal_fulfilled_if_fraud(commission_input)
    commission = goal_fulfilled.get_commission_if_fraud(
        vat_rate=commission_input.vat_rate,
        commission_rate=commission_input.commission_rate_if_fraud,
    )
    assert commission == expected
