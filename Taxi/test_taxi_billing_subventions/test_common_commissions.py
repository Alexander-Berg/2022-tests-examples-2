import decimal
import logging

import pytest

from taxi.billing.clients.models import billing_commissions

from taxi_billing_subventions import config
from taxi_billing_subventions.common import commissions as commissions_service
from taxi_billing_subventions.common import models
from taxi_billing_subventions.common.db import commission
from taxi_billing_subventions.process_doc import _commission


MESSAGE_LOGGER = 'taxi_billing_subventions'


class BillingCommissionsApiClient:
    def __init__(self, response):
        self.response = response

    async def match(
            self,
            data: billing_commissions.CommissionsMatchRequest,
            log_extra=None,
    ) -> billing_commissions.CommissionsMatchResponse:
        return self.response


@pytest.mark.parametrize(
    'order_json, expected_conditions, remote_agreements, log_count',
    [
        (
            'order.json',
            {'p': 'cash', 'tariff_class': 'econom', 'z': 'moscow'},
            [
                billing_commissions.Agreement(
                    contract_id='commission_contract_1',
                    kind='fixed_rate',
                    group='base',
                    vat=decimal.Decimal('0'),
                    effective_billing_type='normal',
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
                        max_cost=decimal.Decimal('0'),
                        min_cost=decimal.Decimal('0'),
                    ),
                    rate=billing_commissions.RateFlat(
                        rate=decimal.Decimal(0), kind='flat',
                    ),
                    support_info=None,
                    settings=None,
                ),
                billing_commissions.Agreement(
                    contract_id='commission_contract_1',
                    kind='call_center',
                    group='call_center',
                    vat=decimal.Decimal('0'),
                    effective_billing_type='normal',
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
                        kind='flat', rate=decimal.Decimal('0.0001'),
                    ),
                    support_info=None,
                    settings=None,
                ),
                billing_commissions.Agreement(
                    contract_id='commission_contract_1',
                    kind='voucher',
                    group='voucher',
                    vat=decimal.Decimal('0'),
                    effective_billing_type='normal',
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
                        kind='flat', rate=decimal.Decimal('0.2'),
                    ),
                    support_info=None,
                    settings=None,
                ),
            ],
            0,
        ),
        (
            'order_with_hiring.json',
            {'p': 'cash', 'tariff_class': 'econom', 'z': 'moscow'},
            [
                billing_commissions.Agreement(
                    contract_id='commission_contract_1',
                    kind='fixed_rate',
                    group='base',
                    vat=decimal.Decimal('0'),
                    effective_billing_type='normal',
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
                        max_cost=decimal.Decimal('0'),
                        min_cost=decimal.Decimal('0'),
                    ),
                    rate=billing_commissions.RateFlat(
                        rate=decimal.Decimal(0), kind='flat',
                    ),
                    support_info=None,
                    settings=None,
                ),
                billing_commissions.Agreement(
                    contract_id='commission_contract_1',
                    kind='call_center',
                    group='call_center',
                    vat=decimal.Decimal('0'),
                    effective_billing_type='normal',
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
                        kind='flat', rate=decimal.Decimal('0.0001'),
                    ),
                    support_info=None,
                    settings=None,
                ),
                billing_commissions.Agreement(
                    contract_id='commission_contract_1',
                    kind='voucher',
                    group='voucher',
                    vat=decimal.Decimal('0'),
                    effective_billing_type='normal',
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
                        kind='flat', rate=decimal.Decimal('0.2'),
                    ),
                    support_info=None,
                    settings=None,
                ),
                billing_commissions.Agreement(
                    contract_id='commission_contract_1',
                    kind='hiring',
                    group='hiring',
                    vat=decimal.Decimal('0'),
                    effective_billing_type='normal',
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
                        kind='flat', rate=decimal.Decimal('0.04'),
                    ),
                    support_info=None,
                    settings=None,
                ),
            ],
            0,
        ),
        (
            'kazan_order_without_tag.json',
            {'p': 'cash', 'tariff_class': 'econom', 'z': 'kazan'},
            [],
            1,
        ),
        (
            'kazan_order_with_tag.json',
            {
                'p': 'cash',
                'tariff_class': 'econom',
                'z': 'kazan',
                'tag': 'reposition_home',
            },
            [
                billing_commissions.Agreement(
                    contract_id='commission_contract_with_tag',
                    kind='asymptotic',
                    group='base',
                    vat=decimal.Decimal('1.18'),
                    effective_billing_type='normal',
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
                        max_cost=decimal.Decimal('0'),
                        min_cost=decimal.Decimal('0'),
                    ),
                    rate=billing_commissions.RateAsymptotic(
                        numerator=decimal.Decimal(2000),
                        cost_norm=decimal.Decimal(50),
                        max_commission_percent=decimal.Decimal(30),
                        asymp=decimal.Decimal(20),
                        kind='asymptotic',
                    ),
                    support_info=None,
                    settings=None,
                ),
            ],
            0,
        ),
        (
            'kazan_order_with_irrelevant_tag.json',
            {'p': 'cash', 'tariff_class': 'econom', 'z': 'kazan'},
            [],
            1,
        ),
        (
            'abakan_order_with_conflicting_commission_tags.json',
            {
                'p': 'cash',
                'tariff_class': 'econom',
                'z': 'abakan',
                'tag': 'conflicting_tag_1',
            },
            [],
            1,
        ),
        (
            'ryazan_order_with_conflicting_tag_and_nontag_rules.json',
            {'p': 'cash', 'z': 'ryazan', 'tag': 'some_ryazan_tag'},
            [
                billing_commissions.Agreement(
                    contract_id='ryazan_contract_with_tag',
                    kind='absolute_value',
                    group='base',
                    vat=decimal.Decimal('0'),
                    effective_billing_type='normal',
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
                        max_cost=decimal.Decimal('0'),
                        min_cost=decimal.Decimal('0'),
                    ),
                    rate=billing_commissions.RateAbsolute(
                        commission=decimal.Decimal('5.5'),
                        kind='absolute_value',
                    ),
                    support_info=None,
                    settings=None,
                ),
                billing_commissions.Agreement(
                    contract_id='ryazan_contract_with_tag',
                    kind='call_center',
                    group='call_center',
                    vat=decimal.Decimal('0'),
                    effective_billing_type='normal',
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
                        kind='flat', rate=decimal.Decimal('0.0001'),
                    ),
                    support_info=None,
                    settings=None,
                ),
                billing_commissions.Agreement(
                    contract_id='ryazan_contract_with_tag',
                    kind='voucher',
                    group='voucher',
                    vat=decimal.Decimal('0'),
                    effective_billing_type='normal',
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
                        kind='flat', rate=decimal.Decimal('0.002'),
                    ),
                    support_info=None,
                    settings=None,
                ),
            ],
            0,
        ),
    ],
)
@pytest.mark.filldb(commission_contracts='for_test_compare_commissions')
async def test_compare_commissions(
        caplog,
        order_json,
        expected_conditions,
        db,
        load_py_json_dir,
        remote_agreements,
        log_count,
):
    conf = config.Config()
    conf.BILLING_SUBVENTIONS_USE_BILLING_COMMISSIONS = {
        'default_for_all': (
            commissions_service.const.BILLING_COMMISSIONS_FULL_USAGE
        ),
    }
    caplog.set_level(logging.WARNING, logger=MESSAGE_LOGGER)
    order: models.doc.Order = load_py_json_dir(
        'test_compare_commissions', order_json,
    )
    search_params = _commission.build_commission_search_params(order, conf)
    agreements = await commission.find_commission_agreements(db, search_params)
    ids = {agreement.contract_id for agreement in agreements}
    assert len(ids) == 1
    actual_conditions = agreements[0].conditions
    assert actual_conditions == expected_conditions
    service_agreements = await commissions_service.fetch_service_agreements(
        commissions_client=BillingCommissionsApiClient(
            billing_commissions.CommissionsMatchResponse(
                agreements=remote_agreements,
            ),
        ),
        search_params=search_params,
        log_extra=None,
        config=conf,
    )
    remote_has_hiring = [
        remote_data
        for remote_data in remote_agreements
        if remote_data.group == 'hiring'
    ]
    if remote_agreements:
        assert len(service_agreements) == len(remote_agreements) + 2 - len(
            remote_has_hiring,
        )
    lines = [x.getMessage() for x in caplog.records]
    assert len(lines) == log_count
