# pylint: disable=redefined-outer-name
import datetime
import decimal

import aiohttp
import pytest
import pytz

from taxi import config
from taxi import discovery
from taxi.billing import clients as billing_clients
from taxi.billing.clients.models import billing_commissions
import taxi.billing.clients.models.const as billing_clients_const


@pytest.fixture
async def client(loop):
    class Config(config.Config):
        BILLING_COMMISSIONS_CLIENT_QOS = {
            '__default__': {'attempts': 1, 'timeout-ms': 200},
        }

    session = aiohttp.ClientSession(loop=loop)
    yield billing_clients.BillingCommissionsApiClient(
        service=discovery.find_service('billing_docs'),
        session=session,
        config=Config(),
        api_token='secret',
    )
    await session.close()


@pytest.mark.parametrize(
    'response_json, actual_response',
    [
        (
            {
                'agreements': [
                    {
                        'contract_id': (
                            'some_asymptotic_formula_commission_contract_id'
                        ),
                        'kind': 'asymptotic',
                        'group': 'base',
                        'vat': '1.18',
                        'cancelation_settings': {
                            'pickup_location_radius': 300,
                            'park_billable_cancel_interval': ['420', '600'],
                            'user_billable_cancel_interval': ['120', '600'],
                        },
                        'cost_info': {
                            'kind': 'boundaries',
                            'max_cost': '6000',
                            'min_cost': '0',
                        },
                        'rate': {
                            'asymp': '16.2',
                            'cost_norm': '-39.399',
                            'kind': 'asymptotic',
                            'max_commission_percent': '0.163',
                            'numerator': '853.8',
                        },
                        'effective_billing_type': 'normal',
                    },
                    {
                        'cancelation_settings': {
                            'pickup_location_radius': 300,
                            'park_billable_cancel_interval': ['420', '600'],
                            'user_billable_cancel_interval': ['120', '600'],
                        },
                        'contract_id': (
                            'some_asymptotic_formula_commission_contract_id'
                        ),
                        'group': 'taximeter',
                        'kind': 'taximeter',
                        'rate': {'kind': 'flat', 'rate': '1'},
                        'vat': '1.18',
                        'effective_billing_type': 'normal',
                    },
                    {
                        'cancelation_settings': {
                            'pickup_location_radius': 300,
                            'park_billable_cancel_interval': ['420', '600'],
                            'user_billable_cancel_interval': ['120', '600'],
                        },
                        'contract_id': (
                            'some_asymptotic_formula_commission_contract_id'
                        ),
                        'group': 'voucher',
                        'kind': 'voucher',
                        'rate': {'kind': 'flat', 'rate': '0.01'},
                        'vat': '1.18',
                        'effective_billing_type': 'normal',
                    },
                    {
                        'cancelation_settings': {
                            'pickup_location_radius': 300,
                            'park_billable_cancel_interval': ['420', '600'],
                            'user_billable_cancel_interval': ['120', '600'],
                        },
                        'contract_id': (
                            'some_asymptotic_formula_commission_contract_id'
                        ),
                        'group': 'hiring',
                        'kind': 'hiring',
                        'rate': {'kind': 'flat', 'rate': '200'},
                        'vat': '1.18',
                        'effective_billing_type': 'normal',
                    },
                    {
                        'category': {
                            'accounts': [
                                {
                                    'agreement': 'taxi/yandex-ride',
                                    'currency': 'order_currency',
                                    'entity': 'entity',
                                    'sub_account': 'sub_account',
                                },
                                {
                                    'agreement': 'taxi/yandex-ride',
                                    'currency': 'contract_currency',
                                    'entity': 'entity',
                                    'sub_account': 'sub_account',
                                },
                            ],
                            'description': 'reposition',
                            'detailed_product': 'detailed_product',
                            'ends_at': '2119-01-01T21:00:00+00:00',
                            'fields': 'core',
                            'id': '2abf162a-b607-11ea-998e-07e60204cbcf',
                            'kind': 'reposition',
                            'name': 'reposition',
                            'product': 'product',
                            'starts_at': '2019-01-01T21:00:00+00:00',
                        },
                        'cancelation_settings': {
                            'pickup_location_radius': 300,
                            'park_billable_cancel_interval': ['420', '600'],
                            'user_billable_cancel_interval': ['120', '600'],
                        },
                        'contract_id': 'some_reposition_contract_id',
                        'group': 'reposition',
                        'kind': 'reposition',
                        'rate': {'kind': 'flat', 'rate': '200'},
                        'vat': '1.18',
                        'effective_billing_type': 'normal',
                    },
                    {
                        'category': {
                            'accounts': [
                                {
                                    'agreement': 'taxi/yandex-ride',
                                    'currency': 'order_currency',
                                    'entity': 'entity',
                                    'sub_account': 'sub_account',
                                },
                                {
                                    'agreement': 'taxi/yandex-ride+0',
                                    'currency': 'contract_currency',
                                    'entity': 'entity',
                                    'sub_account': 'sub_account',
                                },
                            ],
                            'description': 'fine',
                            'detailed_product': 'fine_product',
                            'ends_at': '2119-01-01T21:00:00+00:00',
                            'fields': 'fine',
                            'id': '2abf262a-b607-11ea-998e-07e60204cbcf',
                            'kind': 'fine',
                            'name': 'fine',
                            'product': 'fine_product',
                            'starts_at': '2019-01-01T21:00:00+00:00',
                        },
                        'cancelation_settings': {
                            'pickup_location_radius': 300,
                            'park_billable_cancel_interval': ['420', '600'],
                            'user_billable_cancel_interval': ['120', '600'],
                        },
                        'contract_id': 'some_fine_contract_id',
                        'group': 'fine',
                        'kind': 'fine',
                        'rate': {'kind': 'flat', 'rate': '8921734'},
                        'support_info': {'kind': 'fine', 'fine_code': 'code'},
                        'vat': '1.18',
                        'effective_billing_type': 'normal',
                    },
                ],
            },
            billing_commissions.CommissionsMatchResponse(
                agreements=[
                    billing_commissions.Agreement(
                        contract_id=(
                            'some_asymptotic_formula_commission_contract_id'
                        ),
                        kind='asymptotic',
                        group='base',
                        vat=decimal.Decimal('1.18'),
                        cancelation_settings=(
                            billing_commissions.CancellationSettings(
                                pickup_location_radius=300,
                                park_billable_cancel_interval=(
                                    billing_commissions.CancelInterval(
                                        min=decimal.Decimal('420'),
                                        max=decimal.Decimal('600'),
                                    )
                                ),
                                user_billable_cancel_interval=(
                                    billing_commissions.CancelInterval(
                                        min=decimal.Decimal('120'),
                                        max=decimal.Decimal('600'),
                                    )
                                ),
                            )
                        ),
                        cost_info=billing_commissions.CostInfoBoundaries(
                            kind='boundaries',
                            max_cost=decimal.Decimal('6000'),
                            min_cost=decimal.Decimal('0'),
                        ),
                        rate=billing_commissions.RateAsymptotic(
                            asymp=decimal.Decimal('16.2'),
                            cost_norm=decimal.Decimal('-39.399'),
                            kind='asymptotic',
                            max_commission_percent=decimal.Decimal('0.163'),
                            numerator=decimal.Decimal('853.8'),
                        ),
                        support_info=None,
                        effective_billing_type='normal',
                        settings=None,
                    ),
                    billing_commissions.Agreement(
                        contract_id=(
                            'some_asymptotic_formula_commission_contract_id'
                        ),
                        kind='taximeter',
                        group='taximeter',
                        vat=decimal.Decimal('1.18'),
                        cancelation_settings=(
                            billing_commissions.CancellationSettings(
                                pickup_location_radius=300,
                                park_billable_cancel_interval=(
                                    billing_commissions.CancelInterval(
                                        min=decimal.Decimal('420'),
                                        max=decimal.Decimal('600'),
                                    )
                                ),
                                user_billable_cancel_interval=(
                                    billing_commissions.CancelInterval(
                                        min=decimal.Decimal('120'),
                                        max=decimal.Decimal('600'),
                                    )
                                ),
                            )
                        ),
                        rate=billing_commissions.RateFlat(
                            kind='flat', rate=decimal.Decimal('1'),
                        ),
                        support_info=None,
                        effective_billing_type='normal',
                        settings=None,
                    ),
                    billing_commissions.Agreement(
                        contract_id=(
                            'some_asymptotic_formula_commission_contract_id'
                        ),
                        kind='voucher',
                        group='voucher',
                        vat=decimal.Decimal('1.18'),
                        cancelation_settings=(
                            billing_commissions.CancellationSettings(
                                pickup_location_radius=300,
                                park_billable_cancel_interval=(
                                    billing_commissions.CancelInterval(
                                        min=decimal.Decimal('420'),
                                        max=decimal.Decimal('600'),
                                    )
                                ),
                                user_billable_cancel_interval=(
                                    billing_commissions.CancelInterval(
                                        min=decimal.Decimal('120'),
                                        max=decimal.Decimal('600'),
                                    )
                                ),
                            )
                        ),
                        rate=billing_commissions.RateFlat(
                            kind='flat', rate=decimal.Decimal('0.01'),
                        ),
                        support_info=None,
                        effective_billing_type='normal',
                        settings=None,
                    ),
                    billing_commissions.Agreement(
                        contract_id=(
                            'some_asymptotic_formula_commission_contract_id'
                        ),
                        kind='hiring',
                        group='hiring',
                        vat=decimal.Decimal('1.18'),
                        cancelation_settings=(
                            billing_commissions.CancellationSettings(
                                pickup_location_radius=300,
                                park_billable_cancel_interval=(
                                    billing_commissions.CancelInterval(
                                        min=decimal.Decimal('420'),
                                        max=decimal.Decimal('600'),
                                    )
                                ),
                                user_billable_cancel_interval=(
                                    billing_commissions.CancelInterval(
                                        min=decimal.Decimal('120'),
                                        max=decimal.Decimal('600'),
                                    )
                                ),
                            )
                        ),
                        rate=billing_commissions.RateFlat(
                            kind='flat', rate=decimal.Decimal('200'),
                        ),
                        support_info=None,
                        effective_billing_type='normal',
                        settings=None,
                    ),
                    billing_commissions.Agreement(
                        contract_id='some_reposition_contract_id',
                        category=billing_commissions.Category(
                            description='reposition',
                            detailed_product='detailed_product',
                            fields='core',
                            name='reposition',
                            product='product',
                            accounts=[
                                billing_commissions.Account(
                                    agreement_id='taxi/yandex-ride',
                                    currency='order_currency',
                                    entity='entity',
                                    sub_account='sub_account',
                                ),
                                billing_commissions.Account(
                                    agreement_id='taxi/yandex-ride',
                                    currency='contract_currency',
                                    entity='entity',
                                    sub_account='sub_account',
                                ),
                            ],
                        ),
                        kind='reposition',
                        group='reposition',
                        vat=decimal.Decimal('1.18'),
                        cancelation_settings=(
                            billing_commissions.CancellationSettings(
                                pickup_location_radius=300,
                                park_billable_cancel_interval=(
                                    billing_commissions.CancelInterval(
                                        min=decimal.Decimal('420'),
                                        max=decimal.Decimal('600'),
                                    )
                                ),
                                user_billable_cancel_interval=(
                                    billing_commissions.CancelInterval(
                                        min=decimal.Decimal('120'),
                                        max=decimal.Decimal('600'),
                                    )
                                ),
                            )
                        ),
                        rate=billing_commissions.RateFlat(
                            kind='flat', rate=decimal.Decimal('200'),
                        ),
                        support_info=None,
                        effective_billing_type='normal',
                        settings=None,
                    ),
                    billing_commissions.Agreement(
                        contract_id='some_fine_contract_id',
                        category=billing_commissions.Category(
                            description='fine',
                            detailed_product='fine_product',
                            fields='fine',
                            name='fine',
                            product='fine_product',
                            accounts=[
                                billing_commissions.Account(
                                    agreement_id='taxi/yandex-ride',
                                    currency='order_currency',
                                    entity='entity',
                                    sub_account='sub_account',
                                ),
                                billing_commissions.Account(
                                    agreement_id='taxi/yandex-ride+0',
                                    currency='contract_currency',
                                    entity='entity',
                                    sub_account='sub_account',
                                ),
                            ],
                        ),
                        kind='fine',
                        group='fine',
                        vat=decimal.Decimal('1.18'),
                        cancelation_settings=(
                            billing_commissions.CancellationSettings(
                                pickup_location_radius=300,
                                park_billable_cancel_interval=(
                                    billing_commissions.CancelInterval(
                                        min=decimal.Decimal('420'),
                                        max=decimal.Decimal('600'),
                                    )
                                ),
                                user_billable_cancel_interval=(
                                    billing_commissions.CancelInterval(
                                        min=decimal.Decimal('120'),
                                        max=decimal.Decimal('600'),
                                    )
                                ),
                            )
                        ),
                        rate=billing_commissions.RateFlat(
                            kind='flat', rate=decimal.Decimal('8921734'),
                        ),
                        support_info=billing_commissions.SupportInfoFine(
                            kind=(
                                billing_clients_const.KIND_SUPPORT_INFO_FINE
                            ),
                            fine_code='code',
                        ),
                        effective_billing_type='normal',
                        settings=None,
                    ),
                ],
            ),
        ),
    ],
)
async def test_billing_commissions_client(
        client,
        patch_aiohttp_session,
        response_mock,
        response_json,
        actual_response,
):
    @patch_aiohttp_session(
        discovery.find_service('billing_commissions').url, 'POST',
    )
    def patch_request(method, url, headers, **kwargs):
        assert method == 'post'
        assert headers.get('YaTaxi-Api-Key') == 'secret'
        if '/v1/rules/match' in url:
            return response_mock(json=response_json)
        return None

    agreements = await client.match(
        billing_commissions.CommissionsMatchRequest(
            reference_time=datetime.datetime.now(tz=pytz.utc),
            zone='moscow',
            payment_type='cash',
            tariff_class='econom',
            tags=frozenset([]),
            billing_type='normal',
            hiring=billing_commissions.HiringRequest(
                hired_at=datetime.datetime.now(tz=pytz.utc), type='commercial',
            ),
            fleet_subscription_level='some_level',
        ),
    )
    assert len(patch_request.calls) == 1
    assert agreements == actual_response


def test_decimal_normalization():
    def _test(actual, expected):
        # pylint: disable=protected-access
        assert str(billing_commissions._to_decimal(actual)) == str(
            decimal.Decimal(expected),
        )

    _test('1.00', '1')
    _test('0', '0')
    _test('0.00', '0')
    _test('1.20', '1.2')


@pytest.mark.parametrize(
    'string_data, substitutions, lookup, expected, expected_exception',
    [
        ('{db_id}', {}, {}, '{db_id}', None),
        ('{db_id}', {'db_id': '42'}, [], '42', None),
        (
            '{replace[db_id]}',
            {'replace': {'42': 'matched', '44': 'unmatched'}},
            {'db_id': '42'},
            'matched',
            None,
        ),
        (
            '{replace[db_id]}_{db_id}',
            {'replace': {'42': 'matched', '44': 'unmatched'}},
            {'db_id': '42'},
            'matched_42',
            None,
        ),
        (
            '{replace[db_id]}_{db_id}',
            {'replace': {'44': 'unmatched'}},
            {'db_id': '42'},
            None,
            KeyError,
        ),
    ],
)
def test_replacement(
        string_data, substitutions, lookup, expected, expected_exception,
):
    if expected_exception:
        with pytest.raises(expected_exception) as excinfo:
            assert (
                billing_commissions.process_template(
                    string_data, substitutions=substitutions, lookup=lookup,
                )
                == expected
            )
        assert excinfo.errisinstance(expected_exception)
    else:
        assert (
            billing_commissions.process_template(
                string_data, substitutions=substitutions, lookup=lookup,
            )
            == expected
        )


@pytest.mark.parametrize(
    'response_json, actual_response',
    [
        (
            {
                'agreement': {
                    'cancellation_settings': {
                        'pickup_location_radius': 300,
                        'park_billable_cancel_interval': ['420', '600'],
                        'user_billable_cancel_interval': ['120', '600'],
                    },
                    'cost_info': {
                        'kind': 'boundaries',
                        'max_cost': '6000',
                        'min_cost': '0',
                    },
                    'id': 'some_rebate_contract_id',
                    'base_rule_id': 'some_rebate_base_contract_id',
                    'rate': {'kind': 'flat', 'rate': '8921734'},
                    'vat': '1.18',
                },
            },
            billing_commissions.RebateMatchResponse(
                agreement=billing_commissions.RebateAgreement(
                    id='some_rebate_contract_id',
                    base_rule_id='some_rebate_base_contract_id',
                    vat=decimal.Decimal('1.18'),
                    cancellation_settings=(
                        billing_commissions.CancellationSettings(
                            pickup_location_radius=300,
                            park_billable_cancel_interval=(
                                billing_commissions.CancelInterval(
                                    min=decimal.Decimal('420'),
                                    max=decimal.Decimal('600'),
                                )
                            ),
                            user_billable_cancel_interval=(
                                billing_commissions.CancelInterval(
                                    min=decimal.Decimal('120'),
                                    max=decimal.Decimal('600'),
                                )
                            ),
                        )
                    ),
                    rate=billing_commissions.RateFlat(
                        kind='flat', rate=decimal.Decimal('8921734'),
                    ),
                    cost_info=billing_commissions.CostInfoBoundaries(
                        kind=(
                            billing_commissions.const.KIND_COST_INFO_BOUNDARIES
                        ),
                        min_cost=decimal.Decimal(0),
                        max_cost=decimal.Decimal(6000),
                    ),
                ),
            ),
        ),
    ],
)
async def test_billing_commissions_rebate_client(
        client,
        patch_aiohttp_session,
        response_mock,
        response_json,
        actual_response,
):
    @patch_aiohttp_session(
        discovery.find_service('billing_commissions').url, 'POST',
    )
    def patch_request(method, url, headers, **kwargs):
        assert method == 'post'
        assert headers.get('YaTaxi-Api-Key') == 'secret'
        if '/v1/rebate/match' in url:
            return response_mock(json=response_json)
        return None

    agreements = await client.match_rebate(
        billing_commissions.RebateMatchRequest(
            reference_time=datetime.datetime.now(tz=pytz.utc),
            zone='moscow',
            tariff_class='econom',
        ),
    )
    assert len(patch_request.calls) == 1
    assert agreements == actual_response
