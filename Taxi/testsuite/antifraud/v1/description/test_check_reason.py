import pytest


def _make_input(rule_id):
    return {'reason': {'id': rule_id}}


def _check_output(output, key):
    message = output['message']
    assert message['key'] == key
    assert message['keyset'] == 'antifraud'


@pytest.mark.parametrize(
    'rule_id,key',
    [
        ('rule_1', 'rule_1_desc'),
        ('not_found_rule', 'default_rule_description'),
    ],
)
@pytest.mark.config(
    AFS_RULES_DESCRIPTIONS={
        '__DEFAULT__': 'default_rule_description',
        'rule_1': 'rule_1_desc',
    },
)
def test_limit_base(taxi_antifraud, rule_id, key):
    response = taxi_antifraud.post(
        'v1/description/check_reason', json=_make_input(rule_id),
    )
    assert response.status_code == 200
    _check_output(response.json(), key)
