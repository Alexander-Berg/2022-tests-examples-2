import pytest

from taxi.internal import dbh
from taxi.internal.subvention_kit import rule_processors


NO_GROUP = ''
NO_GROUP_RULE_1 = {
    'sum': 10,
    'is_fake': False
}
NO_GROUP_RULE_2 = {
    'sum': 20,
    'is_fake': True
}
NO_GROUP_RULE_3 = {
    'sum': 30,
    'is_fake': True
}

GROUP_1 = 'group_1'
GROUP_1_RULE_1 = {
    'sum': 100,
    'group_id': GROUP_1,
    'is_fake': False
}
GROUP_1_RULE_2 = {
    'sum': 200,
    'group_id': GROUP_1,
    'is_fake': True
}
GROUP_1_RULE_3 = {
    'sum': 300,
    'group_id': GROUP_1,
    'is_fake': True
}

GROUP_2 = 'group_2'
GROUP_2_RULE_1 = {
    'sum': 1000,
    'group_id': GROUP_2,
    'is_fake': False
}
GROUP_2_RULE_2 = {
    'sum': 2000,
    'group_id': GROUP_2,
    'is_fake': True
}
GROUP_2_RULE_3 = {
    'sum': 3000,
    'group_id': GROUP_2,
    'is_fake': True
}


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'rules,expected_filtered_rules', [
        # simple grouping
        (
            [
                GROUP_1_RULE_1,
            ],
            [
                GROUP_1_RULE_1,
            ]
        ),
        # makes no_group
        (
            [
                NO_GROUP_RULE_1,
                NO_GROUP_RULE_3,
                NO_GROUP_RULE_2,
            ],
            [
                NO_GROUP_RULE_1,
                NO_GROUP_RULE_2,
                NO_GROUP_RULE_3,
            ]
        ),
        # single group
        (
            [
                GROUP_1_RULE_2,
                GROUP_1_RULE_1,
                GROUP_1_RULE_3
            ],
            [
                GROUP_1_RULE_1,
                GROUP_1_RULE_2,
            ]
        ),
        # multiple groups
        (
            [
                GROUP_1_RULE_1,
                GROUP_2_RULE_2,
                GROUP_1_RULE_3,
                GROUP_1_RULE_2,
                GROUP_2_RULE_1,
                GROUP_1_RULE_3
            ],
            [
                GROUP_1_RULE_1,
                GROUP_1_RULE_2,
                GROUP_2_RULE_1,
                GROUP_2_RULE_2,
            ]
        ),
        # combo groups+no_group
        (
            [
                GROUP_2_RULE_3,
                NO_GROUP_RULE_1,
                GROUP_1_RULE_3,
                GROUP_1_RULE_2,
                GROUP_1_RULE_1,
                GROUP_2_RULE_1,
                NO_GROUP_RULE_3,
                NO_GROUP_RULE_2,
            ],
            [
                NO_GROUP_RULE_1,
                NO_GROUP_RULE_2,
                NO_GROUP_RULE_3,
                GROUP_1_RULE_1,
                GROUP_1_RULE_2,
                GROUP_2_RULE_1,
                GROUP_2_RULE_3,
            ]
        ),
    ])
def test_filter_leveled_subvention_rules(rules, expected_filtered_rules):
    filtered_rules = rule_processors.filter_leveled_subvention_rules(rules)
    assert sorted(filtered_rules) == sorted(expected_filtered_rules)


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('type_,is_bonus,is_once,expected', [
    (
            'add', True, True,
            True,
    ),
    (
            'add', False, False,
            False,
    ),
    (
            'guarantee', True, True,
            False,
    ),
    (
            'guarantee', False, False,
            False,
    ),
])
def test_rule_supports_notifying(type_, is_bonus, is_once, expected):
    rule = dbh.personal_subvention_rules.Doc()
    rule.type = type_
    rule.is_bonus = is_bonus
    rule.is_once = is_once
    assert rule_processors.rule_supports_notifying(rule) is expected
