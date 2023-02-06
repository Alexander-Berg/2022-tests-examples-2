import typing as tp

import pytest

from taxi_billing_subventions import config
from taxi_billing_subventions.common import converters
from taxi_billing_subventions.common import models
from taxi_billing_subventions.common.db import commission as db_commission
from taxi_billing_subventions.common.models import commission


@pytest.mark.now('2019-02-07T15:00:00')
@pytest.mark.parametrize(
    'commission_contract_json,ready_for_billing_doc_json,'
    'expected_journal_doc_json',
    [
        (
            'commission_contract.json',
            'ready_for_billing_doc.json',
            'expected_journal_doc.json',
        ),
        (
            'commission_contract.json',
            'driver_workshift/ready_for_billing_doc.json',
            'driver_workshift/expected_journal_doc.json',
        ),
        (
            'commission_contract.json',
            'driver_promocode/ready_for_billing_doc.json',
            'driver_promocode/expected_journal_doc.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_get_commission_details(
        commission_contract_json,
        ready_for_billing_doc_json,
        expected_journal_doc_json,
        load_py_json_dir,
):

    agreements: tp.List[models.commission.Agreement]
    agreements, doc_dict, expected_journal_doc = load_py_json_dir(
        '',
        commission_contract_json,
        ready_for_billing_doc_json,
        expected_journal_doc_json,
    )

    doc = converters.convert_to_order_ready_for_billing_doc(doc_dict['data'])

    order = doc.order
    search_params = models.commission.SearchParams(
        due=order.due,
        zone_name=order.zone_name,
        tariff_class=order.tariff.class_,
        payment_type=order.payment_type,
        tags=order.performer.tags,
    )
    commission_doc = commission.get_commission_journal_doc(
        agreements=agreements,
        doc=doc,
        commission_input=commission.build_commission_input(
            doc,
            doc.order.cost_details,
            models.commission.OrderStatusCalculationConfig.from_config(
                config.Config(),
            ),
        ),
        search_params=search_params,
    )

    assert commission_doc == expected_journal_doc


@pytest.mark.parametrize(
    'ready_for_billing_doc_json, expected_commission_transactions_json',
    [
        (
            'ready_for_billing_doc.json',
            'expected_commission_transactions.json',
        ),
        (
            'cancelled_ready_for_billing_doc.json',
            'cancelled_expected_commission_transactions.json',
        ),
        (
            'ready_for_billing_doc_absolute_commission.json',
            'expected_commission_transactions_absolute_commission.json',
        ),
        (
            'ready_for_billing_doc_workshift_and_discount.json',
            'expected_commission_transactions_workshift_and_discount.json',
        ),
        (
            'ready_for_billing_doc_workshift_and_no_discount.json',
            'expected_commission_transactions_workshift_and_no_discount.json',
        ),
        (
            'ready_for_billing_doc_discount_and_no_workshift.json',
            'expected_commission_transactions_discount_and_no_workshift.json',
        ),
        (
            'ready_for_billing_doc_rebate.json',
            'expected_commission_transactions_rebate.json',
        ),
    ],
)
@pytest.mark.filldb(
    commission_contracts='for_test_get_commission_transactions_doc',
)
async def test_get_commission_transactions_doc(
        ready_for_billing_doc_json,
        expected_commission_transactions_json,
        db,
        load_py_json_dir,
):
    # pylint: disable=invalid-name
    expected_commission_transactions = load_py_json_dir(
        'commission_transactions', expected_commission_transactions_json,
    )
    doc_dict = load_py_json_dir('', ready_for_billing_doc_json)
    doc = converters.convert_to_order_ready_for_billing_doc(doc_dict['data'])
    order = doc.order
    search_params = models.commission.SearchParams(
        due=order.due,
        zone_name=order.zone_name,
        tariff_class=order.tariff.class_,
        payment_type=models.commission.get_contract_payment_type(
            order.payment_type,
        ),
        tags=frozenset(),
    )
    agreements = await db_commission.find_commission_agreements(
        db, search_params,
    )
    commission_transactions_doc = commission.get_commission_transactions_doc(
        doc,
        agreements,
        commission_input=commission.build_commission_input(
            doc,
            doc.order.cost_details,
            models.commission.OrderStatusCalculationConfig.from_config(
                config.Config(),
            ),
        ),
        prefer_payout_flow=False,
    )
    commission_transactions = (
        models.doc.convert_commission_transactions_to_json(
            commission_transactions_doc,
        )
    )
    assert commission_transactions == expected_commission_transactions
