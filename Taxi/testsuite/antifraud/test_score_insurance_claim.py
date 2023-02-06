from copy import deepcopy
import datetime

import pytest


HANDLER_URL = '/score_insurance_claim'

NOW = datetime.datetime(2018, 3, 20, 18, 0, 0)

DEFAULT_REQUEST_BODY = {
    'client': {
        'rides_count': 1,
        'registration_date': '2018-03-17T18:00:00+0000',
        'total_claims_count': 10,
        'recent_claims_count': 3,
        'is_loyal': True,
        'in_blacklist': False,
        'in_staff': True,
    },
    'driver': {
        'rides_count': 2,
        'registration_date': '2018-03-13T18:00:01+0000',
        'total_claims_count': 1,
        'recent_claims_count': 0,
    },
}


@pytest.mark.parametrize(
    'specific_request_body, rules, expected_response_status_code, '
    'expected_response_body',
    [
        (
            {
                'client': {'blocking_reason': 'FY, thats why'},
                'driver': {'blocking_reason': 'No reason'},
            },
            ['rule_1'],
            200,
            {'verdict': 'simplified_proc', 'rule': 'rule_1'},
        ),
        (
            None,
            ['rule_2'],
            200,
            {'verdict': 'expanded_proc', 'rule': 'rule_2'},
        ),
        (None, ['rule_3_1'], 200, {'verdict': 'expanded_proc'}),
        (None, ['rule_3_2'], 200, {'verdict': 'expanded_proc'}),
        (
            None,
            ['rule_4_test', 'rule_4_prod'],
            200,
            {'verdict': 'rejection', 'rule': 'rule_4_prod'},
        ),
        (None, None, 200, {'verdict': 'expanded_proc'}),
        (
            None,
            ['rule_5_1', 'rule_5_100'],
            200,
            {'verdict': 'expanded_proc', 'rule': 'rule_5_100'},
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(antifraud_rules='generic')
def test_handler(
        taxi_antifraud,
        db,
        specific_request_body,
        rules,
        expected_response_status_code,
        expected_response_body,
):
    _enable_rules(db, rules)

    request_body = _merge_dicts(
        DEFAULT_REQUEST_BODY,
        specific_request_body if specific_request_body else {},
    )
    response = taxi_antifraud.post(HANDLER_URL, request_body)

    if expected_response_status_code:
        assert response.status_code == expected_response_status_code
    if expected_response_body:
        assert response.json() == expected_response_body


def _enable_rules(db, rules):
    if rules:
        db.antifraud_rules.update(
            {'_id': {'$in': rules}}, {'$set': {'enabled': True}}, multi=True,
        )


def _merge_dicts(lh_dict, rh_dict):
    res_dict = deepcopy(lh_dict)

    for key, value in rh_dict.items():
        res_dict[key] = (
            value
            if not isinstance(value, dict)
            else _merge_dicts(
                (res_dict[key] if isinstance(res_dict[key], dict) else {}),
                value,
            )
        )

    return res_dict
