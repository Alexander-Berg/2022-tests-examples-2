import copy
import json

import pytest


CONFIG_AFS_RULES_TEST_CASES = {
    '1': {
        'rule_args': {
            'arg_obj': {
                'array': [{'int': 12}, {'bool': True}, {'double': 36.6}],
                'obj': {'null': None},
                'int': 777,
            },
            'arg_double': -63.6,
            'arg_string': 'azaza ololo',
            'arg_int': 100500,
        },
        'rule_result': 0,
    },
    '2': {
        'rule_args': {
            'driver': {'unique_driver_id': '5982f59a9bb9610c238acaab'},
        },
        'rule_result': {
            'frauder': True,
            'block_begin': 30,
            'block_duration': 60,
            'dict': {
                'arr': [500100, '500100', [3], {}, {'3': '4'}],
                'inner3': 'abc',
                'inner2': 100.500,
                'inner1': 100500,
            },
        },
    },
    '3': {'rule_args': {}, 'rule_result': True},
    '5': {'rule_args': {}, 'rule_result': 'Azaza'},
    'ololo': {'rule_args': {}, 'rule_result': True},
}


def _get_response(
        taxi_antifraud, request_body, expected_response_status_code=200,
):
    response = taxi_antifraud.post('rules/test', json=request_body)
    assert response.status_code == expected_response_status_code
    return response


def _get_response_body(
        taxi_antifraud, request_body, expected_response_status_code=200,
):
    response_text = _get_response(
        taxi_antifraud, request_body, expected_response_status_code,
    ).text
    return json.loads(response_text)


@pytest.mark.parametrize(
    'request_body, expected_response_body, rule_result',
    [
        (
            {
                'rule': {
                    'src': (
                        'function on_check_sign({driver}) { '
                        'if(driver.unique_driver_id === '
                        '"5982f59a9bb9610c238acaab") { '
                        'return { '
                        '"frauder": true, '
                        '"block_begin": 30, '
                        '"block_duration": 60, '
                        '"dict": { '
                        '"inner1": 100500, '
                        '"inner2": 100.500, '
                        '"inner3": "abc", '
                        '"arr": [500100, "500100", [3], {}, {"3": "4"}], '
                        '}, '
                        '}; '
                        '} '
                        'return { '
                        '"frauder": false, '
                        '}; '
                        '} '
                    ),
                    'type': 2,
                },
            },
            {'tests_passed': True},
            None,
        ),
        (
            {
                'rule': {
                    'src': (
                        'function on_check_drivers({arg_obj, arg_double,'
                        ' arg_string, arg_int}) {'
                        '  if (arg_obj.array[0].int != 12) {return 1;}'
                        '  if (arg_obj.array[1].bool != true) {return 2;}'
                        '  if (arg_obj.array[2].double != 36.6) {return 3;}'
                        '  if (arg_obj.obj.null != null) {return 4;}'
                        '  if (arg_obj.int != 777) {return 5;}'
                        '  if (arg_double != -63.6) {return 6;}'
                        '  if (arg_string != "azaza ololo") {return 7;}'
                        '  if (arg_int != 100500) {return 8;}'
                        '  return 0;'
                        '}'
                    ),
                    'type': 1,
                },
            },
            {'tests_passed': True},
            None,
        ),
        (
            {
                'rule': {
                    'src': 'function on_check_drivers() {return true;}',
                    'type': 1,
                },
            },
            {'tests_passed': True},
            True,
        ),
        (
            {
                'rule': {
                    'src': 'function on_check_fake() {return true;}',
                    'type': 3,
                },
            },
            {'tests_passed': True},
            None,
        ),
        (
            {
                'rule': {
                    'src': 'function on_check_driver() {return 0;}',
                    'type': 1,
                },
            },
            {
                'tests_passed': False,
                'tests_results': [
                    {
                        'name': 'basic_test',
                        'passed': False,
                        'error': (
                            'JS As type mismatch, got: \'undefined\' '
                            'when a \'v8::Function\' was expected'
                        ),
                    },
                ],
            },
            None,
        ),
        (
            {
                'rule': {
                    'src': 'function on_check_drivers() {return 1;}',
                    'type': 1,
                },
            },
            {
                'tests_passed': False,
                'tests_results': [
                    {
                        'name': 'basic_test',
                        'passed': False,
                        'error': 'rule returned 1, but 0 was expected',
                    },
                ],
            },
            None,
        ),
        (
            {
                'rule': {
                    'src': 'function on_check_drivers() {return -123.456;}',
                    'type': 1,
                },
            },
            {
                'tests_passed': False,
                'tests_results': [
                    {
                        'name': 'basic_test',
                        'passed': False,
                        'error': (
                            'rule returned -123.456000, '
                            'but 654.321000 was expected'
                        ),
                    },
                ],
            },
            654.321,
        ),
        (
            {
                'rule': {
                    'src': 'function on_check_drivers() {return true;}',
                    'type': 1,
                },
            },
            {
                'tests_passed': False,
                'tests_results': [
                    {
                        'name': 'basic_test',
                        'passed': False,
                        'error': 'rule returned true, but false was expected',
                    },
                ],
            },
            False,
        ),
        (
            {
                'rule': {
                    'src': 'function on_check_drivers() {return \'true\';}',
                    'type': 1,
                },
            },
            {
                'tests_passed': False,
                'tests_results': [
                    {
                        'name': 'basic_test',
                        'passed': False,
                        'error': (
                            'JS TypeCast type mismatch, '
                            'got \'string\' when a \'double\' was '
                            'expected'
                        ),
                    },
                ],
            },
            None,
        ),
        (
            {
                'rule': {
                    'src': 'function check() {return \'Azaza\';}',
                    'type': 5,
                },
            },
            {'tests_passed': True},
            None,
        ),
        (
            {
                'rule': {
                    'src': 'function check() {return \'Ololo\';}',
                    'type': 5,
                },
            },
            {
                'tests_passed': False,
                'tests_results': [
                    {
                        'name': 'basic_test',
                        'passed': False,
                        'error': (
                            'rule returned \'Ololo\', '
                            'but \'Azaza\' was expected'
                        ),
                    },
                ],
            },
            None,
        ),
        (
            {
                'rule': {
                    'src': 'function on_check_drivers() {return null;}',
                    'type': 1,
                },
            },
            {
                'tests_passed': False,
                'tests_results': [
                    {
                        'name': 'basic_test',
                        'passed': False,
                        'error': (
                            'JS TypeCast type mismatch, '
                            'got \'object\' when a \'double\' was '
                            'expected'
                        ),
                    },
                ],
            },
            None,
        ),
    ],
)
@pytest.mark.config(AFS_RULES_TEST_CASES=CONFIG_AFS_RULES_TEST_CASES)
def test_rules_test(
        taxi_antifraud,
        config,
        request_body,
        expected_response_body,
        rule_result,
):
    if rule_result is not None:
        new_config_afs_rules_test_cases = copy.deepcopy(
            CONFIG_AFS_RULES_TEST_CASES,
        )
        new_config_afs_rules_test_cases['1']['rule_result'] = rule_result
        config.set_values(
            dict(AFS_RULES_TEST_CASES=new_config_afs_rules_test_cases),
        )

    response_body = _get_response_body(taxi_antifraud, request_body)

    assert response_body == expected_response_body


@pytest.mark.parametrize(
    'request_body, expected_response_fatal_error_postfix',
    [
        (
            {
                'rule': {
                    'src': 'function on_check_drivers() {return 0;',
                    'type': 1,
                },
            },
            'SyntaxError: Unexpected end of input',
        ),
    ],
)
@pytest.mark.config(AFS_RULES_TEST_CASES=CONFIG_AFS_RULES_TEST_CASES)
def test_fatal_error_test(
        taxi_antifraud, request_body, expected_response_fatal_error_postfix,
):
    response_body = _get_response_body(taxi_antifraud, request_body)

    assert not response_body['tests_passed']
    assert response_body['fatal_error'].endswith(
        expected_response_fatal_error_postfix,
    )


@pytest.mark.parametrize(
    'request_body, expected_response_error_postfix',
    [
        (
            {
                'rule': {
                    'src': (
                        'function on_check_drivers({arg_objj}) {'
                        '  return arg_objj.int;}'
                    ),
                    'type': 1,
                },
            },
            'TypeError: Cannot read property \'int\' of undefined',
        ),
    ],
)
@pytest.mark.config(AFS_RULES_TEST_CASES=CONFIG_AFS_RULES_TEST_CASES)
def test_error_test(
        taxi_antifraud, request_body, expected_response_error_postfix,
):
    response_body = _get_response_body(taxi_antifraud, request_body)

    assert not response_body['tests_passed']
    assert len(response_body['tests_results']) == 1
    assert response_body['tests_results'][0]['error'].endswith(
        expected_response_error_postfix,
    )


@pytest.mark.parametrize(
    'request_body',
    [
        (
            {
                'rule': {
                    'src': 'function on_check_drivers() {return 0;}',
                    'type': 0,
                },
            },
        ),
    ],
)
@pytest.mark.config(AFS_RULES_TEST_CASES=CONFIG_AFS_RULES_TEST_CASES)
def test_internal_server_error_test(taxi_antifraud, request_body):
    response_body = _get_response(taxi_antifraud, request_body, 500).text

    assert response_body == ''


@pytest.mark.parametrize(
    'request_body, expected_response_body',
    [
        (
            {
                'rule': {
                    'src': 'function on_check_chuck() {return true;}',
                    'type': 'ololo',
                },
            },
            {'error': {'text': 'invalid type'}},
        ),
    ],
)
@pytest.mark.config(AFS_RULES_TEST_CASES=CONFIG_AFS_RULES_TEST_CASES)
def test_bad_request_test(
        taxi_antifraud, request_body, expected_response_body,
):
    response_body = _get_response_body(taxi_antifraud, request_body, 400)
    assert response_body == expected_response_body


@pytest.mark.parametrize(
    'rule_src,rule_type,rule_args,rule_result',
    [
        (
            'function handle({arg1}) { return {"status": '
            'arg1 === "val1" ? "block": "allow"}; }',
            11,  # kPayment
            {'arg1': 'val1'},
            {'status': 'block'},
        ),
        (
            'function handle({arg1}) { return {"result": '
            'arg1 === "val1" ? "standard2_3ds": "auto"}; }',
            12,  # kCardVerificationType
            {'arg1': 'val1'},
            {'result': 'standard2_3ds'},
        ),
        (
            'function handle({arg1}) { return {"status": '
            'arg1 === "val1" ? "block": "allow"}; }',
            13,  # kRefuel
            {'arg1': 'val1'},
            {'status': 'block'},
        ),
        (
            'function handle({arg1}) { return {"status": '
            'arg1 === "val1" ? "block": "allow"}; }',
            14,  # kDriverPromo
            {'arg1': 'val1'},
            {'status': 'block'},
        ),
        (
            'function handle({arg1}) { return {"statuses": '
            '[{"id": "card_id1", "status": arg1 === "val1" ? '
            '"standard2_3ds" : "auto"}]}; }',
            15,  # kCardVerifyRequired
            {'arg1': 'val1'},
            {'statuses': [{'id': 'card_id1', 'status': 'standard2_3ds'}]},
        ),
        (
            'function handle({arg1}) { return {"status": '
            'arg1 === "val1" ? "block": "allow"}; }',
            16,  # kPayTypeChangeAvailable
            {'arg1': 'val1'},
            {'status': 'block'},
        ),
        (
            'function handle({arg1}) { return {"frauder": '
            'arg1 === "val1", "status": "hacker"}; }',
            17,  # kPartialDebitStatus
            {'arg1': 'val1'},
            {'frauder': True, 'status': 'hacker'},
        ),
        (
            'function handle({arg1}) { return {"status": '
            'arg1 === "val1" ? "block": "allow"}; }',
            100500,  # unknown type
            {'arg1': 'val1'},
            {'status': 'block'},
        ),
    ],
)
def test_uafs_rules(
        taxi_antifraud, config, rule_src, rule_type, rule_args, rule_result,
):
    config.set_values(
        {
            'AFS_RULES_TEST_CASES': {
                str(rule_type): {
                    'rule_args': rule_args,
                    'rule_result': rule_result,
                },
            },
        },
    )
    response = taxi_antifraud.post(
        'rules/test', json={'rule': {'src': rule_src, 'type': rule_type}},
    )
    assert response.status_code == 200
    assert response.json() == {'tests_passed': True}
