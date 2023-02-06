import dataclasses

import pytest

from taxi_billing_subventions.common.commissions import _helpers as helpers


@pytest.mark.parametrize('use_cost', (False, True))
@pytest.mark.parametrize(
    'data_json', ('not_call_center_order.json', 'call_center_order.json'),
)
def test_call_center_agreement(load_py_json, use_cost, data_json):
    data = load_py_json(data_json)
    agreements = {a.kind: a for a in data['agreements']}
    agreement = helpers.make_call_center_agreement(
        agreements_by_kind=agreements,
        base_agreement=agreements['base'],
        use_call_center_cost=use_cost,
    )
    details = agreement.get_commission_details(
        input_=data['commission_input'],
        commission_when_promocode_applies=None,
    )
    expected = data['from_order' if use_cost else 'from_agreement']
    assert dataclasses.asdict(details) == expected
