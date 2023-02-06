import pytest

from billing_functions.functions.core.subventions import agreement_ref


@pytest.mark.parametrize(
    'rule_id, scope, id_type, expected',
    [
        (
            'id',
            agreement_ref.Scope.DEFAULT,
            agreement_ref.IdType.GROUP,
            'subvention_agreement/1/default/group_id/id',
        ),
        (
            'id',
            agreement_ref.Scope.PERSONAL,
            agreement_ref.IdType.PRIMARY,
            'subvention_agreement/1/personal/_id/id',
        ),
    ],
)
def test_make(rule_id, scope, id_type, expected):
    assert agreement_ref.make(rule_id, scope, id_type) == expected


@pytest.mark.parametrize(
    'ref, expected',
    [
        ('subvention_agreement/1/default/group_id/id', 'group_id/id'),
        ('subvention_agreement/1/default/_id/id', '_id/id'),
    ],
)
def test_parse_id(ref, expected):
    assert agreement_ref.parse_rule_id(ref) == expected


def test_parse_raw_rule_id():
    ref = 'subvention_agreement/1/default/group_id/id'
    assert agreement_ref.parse_raw_rule_id(ref) == 'id'
