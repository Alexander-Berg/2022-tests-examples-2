import dataclasses
import datetime
import decimal
from unittest import mock

import aiohttp
import pytest

from taxi import billing
from taxi.clients import billing_replication
from taxi.clients import tvm

from taxi_billing_subventions import caches
from taxi_billing_subventions import process_doc
from taxi_billing_subventions.common import intervals
from taxi_billing_subventions.common import models
from taxi_billing_subventions.process_doc._payouts import (
    _driver_fix_b2b as b2b,
)
from taxi_billing_subventions.process_doc._payouts import _payments


@pytest.mark.parametrize(
    'agency_cc, rate',
    (
        ('RUB', decimal.Decimal(1)),
        ('BYN', decimal.Decimal(1) / 30),
        ('RSD', decimal.Decimal('1.4782')),
    ),
)
async def test_commission_calculator(
        context, goal_fulfilled, agency_cc, rate, active_contracts,
):
    currency_data = models.CurrencyData(
        for_contract=models.RatedCurrency(
            currency=agency_cc, rate_from_local=rate,
        ),
        for_offer_contract=None,
    )
    calculator = b2b.DriverFixCommissionCalculator(
        context=context,
        contracts=b2b.Contracts(
            active_contracts=active_contracts,
            tlog_service_ids=context.context.config.BILLING_TLOG_SERVICE_IDS,
            default_currency='RUB',
            currency_data=currency_data,
        ),
        currencies=b2b.FixedCurrencies(value=rate),
    )
    payment = await calculator(goal_fulfilled, datetime.date(2020, 10, 9))

    expected_domestic_payout = decimal.Decimal('100.0000000000000037007434154')
    expected = _payments.Payment(
        kind=_payments.PaymentKind.DRIVER_FIX_COMMISSION,
        billing_client_id=context.b2b_park_id,
        contract_id='123456',
        payout=billing.Money(expected_domestic_payout, 'RUB'),
        payout_cc=billing.Money(rate * expected_domestic_payout, agency_cc),
        cc_rate=rate,
        vat=decimal.Decimal('19.9999999999999962992565846'),
        is_payable=True,
        detailed_product='driver_fix_commission',
    )

    assert dataclasses.asdict(payment) == dataclasses.asdict(expected)


@pytest.mark.parametrize(
    'agency_cc, rate',
    (
        ('RUB', decimal.Decimal(1)),
        ('BYN', decimal.Decimal(1) / 30),
        ('RSD', decimal.Decimal('1.4782')),
    ),
)
async def test_fraud_commission_calculator(
        decimal_prec_8,
        context,
        goal_fulfilled,
        agency_cc,
        rate,
        active_contracts,
):
    currency_data = models.CurrencyData(
        for_contract=models.RatedCurrency(
            currency=agency_cc, rate_from_local=rate,
        ),
        for_offer_contract=None,
    )
    calculator = b2b.DriverFixFraudCommissionCalculator(
        context=context,
        contracts=b2b.Contracts(
            active_contracts=active_contracts,
            tlog_service_ids=context.context.config.BILLING_TLOG_SERVICE_IDS,
            default_currency='RUB',
            currency_data=currency_data,
        ),
        currencies=b2b.FixedCurrencies(value=rate),
    )
    payment = await calculator(goal_fulfilled, datetime.date(2020, 10, 9))
    payout = decimal.Decimal('141.66667')
    expected = _payments.Payment(
        kind=_payments.PaymentKind.DRIVER_FIX_COMMISSION,
        billing_client_id=context.b2b_park_id,
        contract_id='123456',
        payout=billing.Money(payout, 'RUB'),
        payout_cc=billing.Money(rate * payout, agency_cc),
        cc_rate=rate,
        vat=decimal.Decimal('28.33333'),
        is_payable=True,
        detailed_product='driver_fix_commission_for_fraud',
    )

    assert dataclasses.asdict(payment) == dataclasses.asdict(expected)


@pytest.mark.parametrize(
    'ctype,expected',
    (
        (b2b.ContractType.B2B_CLIENT, 'USD'),
        (b2b.ContractType.B2B_PARTNER, 'EUR'),
    ),
)
async def test_contracts_currencies(active_contracts, ctype, expected):
    contracts = b2b.Contracts(
        active_contracts=active_contracts,
        tlog_service_ids={},
        default_currency='RUB',
    )
    currency = await contracts.get_contract_currency(ctype)
    assert currency == expected


async def test_b2b_contracts_fetcher(
        context, load_json, mockserver, active_contracts,
):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _wrapper(_):
        return load_json('b2b_contracts.json')

    fetcher = b2b.B2BContractsFetcher(context.context)
    fetched = await fetcher.get_contracts(
        context.b2b_client_id, context.invoice_date,
    )
    assert fetched == active_contracts


@pytest.fixture(name='session')
async def make_session():
    session = aiohttp.client.ClientSession()
    yield session
    await session.close()


@pytest.fixture(name='context')
def make_context(db, session):
    tvm_client = tvm.TVMClient(
        service_name='test_taxi_billing_subventions',
        secdist={},
        config=mock.Mock(TVM_RULES={}),
        session=session,
    )
    replication_client = billing_replication.BillingReplicationClient(
        session=session, tvm_client=tvm_client,
    )
    vat = models.Vat([(intervals.unbounded(), decimal.Decimal(1.2))], None)
    zones_cache = mock.Mock(spec=caches.ZonesCache)
    zones_cache.get_zone.return_value = models.Zone(
        'moscow', 'city', datetime.timezone.utc, 'RUB', 'ru', vat, 'rus',
    )
    context = mock.Mock(
        spec=process_doc.ContextData,
        billing_replication_client=replication_client,
        zones_cache=zones_cache,
    )
    context.config.BILLING_REPLICATION_EXT_REQUEST_TIMEOUT_MS = 500
    context.config.BILLING_TLOG_SERVICE_IDS = {
        'client_b2b_trip_payment': 650,
        'commission/driver_fix': 128,
        'park_b2b_trip_payment': 651,
    }
    rule = mock.Mock(
        spec=models.DriverFixRule,
        data=mock.Mock(
            spec=models.DriverFixRuleData,
            commission_rate_if_fraud=decimal.Decimal(0.1),
        ),
    )
    return b2b.DriverFixB2BPayoutContext(
        agglomeration=None,
        b2b_client_id='client_id',
        b2b_park_id='park_id',
        context=context,
        database=db,
        driver_work_mode='driver_fix',
        invoice_date=datetime.datetime.now(tz=datetime.timezone.utc),
        park=mock.Mock(spec=models.Park),
        rule=rule,
        subventions_input=mock.Mock(
            spec=models.subventions.Input, zone_name='moscow',
        ),
        journal_entries_by_sub_account={},
    )


@pytest.fixture(name='goal_fulfilled')
def make_goal_fulfilled():
    return models.DriverFixGoalFulfilled(
        is_fulfilled=True,
        agreement_id='aid',
        bonus=billing.Money.zero('RUB'),
        guarantee=billing.Money(decimal.Decimal(100), 'RUB'),
        guarantee_on_order=billing.Money(decimal.Decimal(50), 'RUB'),
        income=billing.Money(decimal.Decimal(219), 'RUB'),
        on_order_minutes=decimal.Decimal(50),
        free_minutes=decimal.Decimal(50),
        identity=models.rule.Identity('id_'),
        cash_income=billing.Money.zero('RUB'),
        cash_commission=billing.Money.zero('RUB'),
        discounts=billing.Money.zero('RUB'),
        promocodes_marketing=billing.Money.zero('RUB'),
        promocodes_support=billing.Money.zero('RUB'),
    )


@pytest.fixture(name='active_contracts')
def make_active_contracts(load_json):
    raw_contracts = load_json('b2b_contracts.json')
    return [
        models.BillingReplicationContract.from_replication_data(data)
        for data in raw_contracts
    ]
