import datetime as dt
from typing import Optional

import pytest

from billing.docs import service as docs
from billing_models.generated import models
from billing_models.generated.models import park_commission
from taxi.billing.util import dates

from billing_functions.functions import calculate_subventions
from billing_functions.repositories import commission_agreements
from billing_functions.repositories import migration_mode
from billing_functions.repositories import subvention_rules
from billing_functions.stq import events
from test_billing_functions import equatable
from test_billing_functions import mocks


@pytest.mark.parametrize(
    'test_data_json',
    [
        'no_marketing_contract.json',
        'no_matching_rules.json',
        'no_filtered_rules.json',
        'instant_payment_paid.json',
        'instant_payment_netted.json',
        'instant_payment_partly_netted.json',
        'shifts.json',
        'shifts_batched_cargo_order.json',
        'disabled_shift_ended.json',
        'cargo_instant_payment_paid.json',
        'cargo_instant_payment_netted.json',
        'cargo_shifts.json',
        'geo_booking.json',
        'shuttle.json',
    ],
)
@pytest.mark.json_obj_hook(
    Query=calculate_subventions.Query,
    Contract=calculate_subventions.Query.Contract,
    Driver=calculate_subventions.Query.Driver,
    Order=calculate_subventions.Query.Order,
    Commission=calculate_subventions.Query.Commission,
    ShiftsConfig=calculate_subventions.Query.ShiftsConfig,
    Subventions=equatable.codegen(models.Subventions),
    SubventionPayment=models.SubventionPayment,
    SubventionPaymentItem=models.SubventionPaymentItem,
    AntifraudPrecheck=models.AntifraudPrecheck,
    SubventionShift=models.SubventionShift,
    GoalRuleShift=models.GoalRuleShift,
    NmfgRuleShift=models.NmfgRuleShift,
    GeoBookingRuleShift=models.GeoBookingRuleShift,
    DoXGetYShift=models.DoXGetYRuleShift,
    SubventionCommission=models.SubventionCommission,
    SingleRideRule=subvention_rules.SingleRideRule,
    SingleOnTopRule=subvention_rules.SingleOnTopRule,
    GoalRule=subvention_rules.GoalRule,
    GoalRuleStep=subvention_rules.GoalRule.Step,
    GoalRuleWindow=subvention_rules.GoalRule.Window,
    NmfgRule=subvention_rules.NmfgRule,
    GeoBookingRule=subvention_rules.GeoBookingRule,
    DoXGetYRule=subvention_rules.DoXGetYRule,
    Doc=docs.Doc,
    ParkCommissionRule=park_commission.BaseParkCommissionRule,
    # raw agreement
    HiringInfo=commission_agreements.Query.HiringInfo,
    Agreement=commission_agreements.Agreement,
    RateFlat=commission_agreements.RateFlat,
    RateAbsolute=commission_agreements.RateAbsolute,
    RateAsymptotic=commission_agreements.RateAsymptotic,
    CancellationSettings=commission_agreements.CancellationSettings,
    CancellationInterval=commission_agreements.CancellationInterval,
    BrandingDiscount=commission_agreements.BrandingDiscount,
    CostInfoBoundaries=commission_agreements.CostInfoBoundaries,
    CostInfoAbsolute=commission_agreements.CostInfoAbsolute,
    MigrationMode=migration_mode.Mode,
)
@pytest.mark.config(
    BILLING_TLOG_SERVICE_IDS={
        'subvention/paid': 137,
        'subvention/netted': 111,
        'cargo_subvention/paid': 1164,
        'cargo_subvention/netted': 1161,
    },
)
@pytest.mark.now('2021-01-01T00:00:00+00:00')
async def test_calculate_subventions(
        test_data_json,
        *,
        load_py_json,
        stq3_context,
        do_mock_billing_docs,
        mock_open_nmfg_shift,
        patched_stq_queue,
):
    test_data = load_py_json(test_data_json)
    billing_docs = do_mock_billing_docs()

    scheduler = events.Scheduler(
        stq3_context.docs,
        stq3_context.stq,
        no_jitter,
        dates.utc_now_with_tz,
        enabled=True,
    )
    results = await calculate_subventions.execute(
        mocks.Antifraud.always_allowing(),
        stq3_context.service_ids,
        mocks.CurrencyRates(test_data['currency_rates']),
        mocks.Cities(test_data['cities'], {}),
        Migration(goal_mode=test_data.get('goal_migration', 'disabled')),
        stq3_context.clients.billing_subventions,
        scheduler,
        test_data['query'],
    )

    assert results.serialize() == test_data['expected_results'].serialize()
    assert billing_docs.created_docs == test_data['expected_docs']
    assert patched_stq_queue.pop_calls() == test_data['expected_stq_calls']
    assert mock_open_nmfg_shift == test_data['expected_open_shift_requests']


class Migration(migration_mode.Repository):
    def __init__(self, *, goal_mode: str = 'disabled'):
        self._goal_mode = migration_mode.Mode(goal_mode)

    def match_for_taxi_order(
            self, zone: str, as_of: dt.datetime,
    ) -> migration_mode.Mode:
        return migration_mode.Mode.ENABLED

    def match_for_taxi_gb_shift(
            self, zone: str, as_of: dt.datetime,
    ) -> migration_mode.Mode:
        raise NotImplementedError

    def match_for_goal_payment_split(
            self, zone: str, as_of: dt.datetime,
    ) -> migration_mode.Mode:
        return self._goal_mode

    def match_for_fin_payouts_via_oebs(
            self,
            firm_id: Optional[int],
            billing_client_id: Optional[str],
            as_of: dt.datetime,
    ) -> migration_mode.Mode:
        raise NotImplementedError


def no_jitter(seed: str) -> dt.timedelta:
    del seed  # unused
    return dt.timedelta()


@pytest.fixture(name='mock_open_nmfg_shift')
def _mock_open_shift(mockserver):
    requests = []

    def _gen_id():
        seed = 11111
        while True:
            yield seed
            seed += 11111

    gen_id = _gen_id()

    @mockserver.json_handler('/billing_subventions/v1/shifts/open_nmfg')
    def _mock_open_nmfg_shift(request):
        requests.append(request.json)
        return {'doc_id': next(gen_id)}

    @mockserver.json_handler('/billing_subventions/v1/shifts/open_geo_booking')
    def _mock_open_geo_booking_shift(request):
        requests.append(request.json)
        return {'doc_id': next(gen_id)}

    @mockserver.json_handler('/billing_subventions/v1/shifts/open_goal')
    def _mock_open_goal_shift(request):
        requests.append(request.json)
        return {'doc_id': next(gen_id)}

    return requests


@pytest.mark.parametrize(
    'target_dt, delay, single_ride_af_decisions_end, depends_on_income, '
    'expected',
    [
        (
            dt.datetime(2022, 1, 1, tzinfo=dates.TZ_MSK),
            dt.timedelta(hours=1),
            dt.time(0),
            False,
            dt.datetime(2022, 1, 1, 1, tzinfo=dates.TZ_MSK),
        ),
        (
            dt.datetime(2022, 1, 1, tzinfo=dates.TZ_MSK),
            dt.timedelta(hours=2),
            dt.time(1),
            True,
            dt.datetime(2022, 1, 1, 2, tzinfo=dates.TZ_MSK),
        ),
        (
            dt.datetime(2022, 1, 1, tzinfo=dates.TZ_MSK),
            dt.timedelta(hours=1),
            dt.time(2),
            True,
            dt.datetime(2022, 1, 1, 2, tzinfo=dates.TZ_MSK),
        ),
        (
            dt.datetime(2022, 1, 1, 1, tzinfo=dates.TZ_MSK),
            dt.timedelta(hours=0),
            dt.time(2),
            True,
            dt.datetime(2022, 1, 2, 2, tzinfo=dates.TZ_MSK),
        ),
        (
            dt.datetime(2022, 1, 1, 3, tzinfo=dates.TZ_MSK),
            dt.timedelta(hours=0),
            dt.time(2),
            True,
            dt.datetime(2022, 1, 2, 2, tzinfo=dates.TZ_MSK),
        ),
    ],
)
def test_adjust_shift_process_at(
        target_dt,
        delay,
        single_ride_af_decisions_end,
        depends_on_income,
        expected,
):
    actual = calculate_subventions.adjust_shift_process_at(
        target_dt, delay, single_ride_af_decisions_end, depends_on_income,
    )
    assert actual == expected
