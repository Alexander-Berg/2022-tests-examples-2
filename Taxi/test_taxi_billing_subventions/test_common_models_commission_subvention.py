import typing as tp

import pytest

from taxi_billing_subventions.common import converters
from taxi_billing_subventions.common import models
from taxi_billing_subventions.common.models import commission


@pytest.mark.parametrize(
    'commission_contract_json,ready_for_billing_doc_json,journal_doc_json,'
    'expected_journal_doc_json',
    [
        (
            'commission_contract.json',
            'ready_for_billing_doc.json',
            'journal_doc.json',
            'expected_journal_doc.json',
        ),
        (
            'commission_contract.json',
            'driver_workshift/ready_for_billing_doc.json',
            'journal_doc.json',
            'driver_workshift/expected_journal_doc.json',
        ),
        (
            'commission_contract.json',
            'driver_promocode/ready_for_billing_doc.json',
            'journal_doc.json',
            'driver_promocode/expected_journal_doc.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_get_commission_details(
        commission_contract_json,
        ready_for_billing_doc_json,
        journal_doc_json,
        expected_journal_doc_json,
        load_py_json_dir,
):

    agreements: tp.List[models.commission.Agreement]
    agreements, doc_dict, journal_doc, expected_journal_doc = load_py_json_dir(
        '',
        commission_contract_json,
        ready_for_billing_doc_json,
        journal_doc_json,
        expected_journal_doc_json,
    )

    doc = converters.convert_to_order_ready_for_billing_doc(doc_dict['data'])

    has_commission_by_agreement_id = {
        'subvention_agreement/extra_30_rubles_rule_id': True,
    }
    commission_order = commission.build_subvention_commission_input(doc)
    with_commission = commission.get_subvention_with_commission(
        agreements=agreements,
        commission_input=commission_order,
        journal_doc=journal_doc,
        has_commission_by_agreement_id=has_commission_by_agreement_id,
        commission_modificator=lambda x: x,
    )

    assert with_commission.journal == expected_journal_doc
