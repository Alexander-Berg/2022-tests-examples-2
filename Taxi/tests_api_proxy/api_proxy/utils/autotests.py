import json
import re
import uuid

import pytest

from . import endpoints as utils_endpoints

__all__ = [
    'body_mismatch_error',
    'call_count_error',
    'call_order_mismatch',
    'check_testrun_status',
    'code_mismatch_error',
    'config_not_loaded',
    'content_type_mismatch_error',
    'exception_error',
    'experiments_consumer_mismatch',
    'experiments_kwargs_mismatch',
    'headers_mismatch_error',
    'location_stack',
    'mock_request_mismatch',
    'secdist_no_toplevel',
]


def validate_error_message(path, errors, message):
    err_prefix = 'Endpoint \'' + path + '\' tests failed. Messages: \''
    err_sep = ', '
    err_suffix = '\'.'

    assert message[: len(err_prefix)] == err_prefix
    assert message[-len(err_suffix) :] == err_suffix

    received_errors = []
    offset = len(err_prefix)
    for err_exp in errors:
        received_errors.append(message[offset : offset + len(err_exp)])
        offset += len(err_exp) + len(err_sep)
    if received_errors:
        assert offset - len(err_sep) + len(err_suffix) == len(message), (
            received_errors,
            errors,
        )

    assert len(message) == len(err_prefix) + len(err_sep.join(errors)) + len(
        err_suffix,
    )

    rgx_rsp_exp = re.compile(
        (
            r'\w+: Response (?P<type>code|body|headers|content type) value'
            r' doesn\'t match the expected one:\n'
            r'Response: \'(?P<rsp>.*)\'\n'
            r'Expected: \'(?P<exp>.*)\'(?:\nDiff: (?P<diff>.*))?.\n'
        ),
        re.DOTALL,
    )

    rgx_req_exp = re.compile(
        (
            r'\w+: Request (?P<type>url path-params) value'
            r' doesn\'t match the expected one:\n'
            r'Request: \'(?P<rsp>.*)\'\n'
            r'Expected: \'(?P<exp>.*)\'(?:\nDiff: (?P<diff>.*))?.\n'
        ),
        re.DOTALL,
    )

    rgx_wrong_mock = re.compile(
        (
            r'\w+: Wrong request to mock \'(?P<resource>\w*)\':'
            r' (?P<param>[\w-]+) value doesn\'t match the expected one:\n'
            r'Request: \'(?P<rsp>.*)\'\n'
            r'Expected: \'(?P<exp>.*)\''
            r'(?:\nDiff: (?P<diff>.*))?'
            r'\. location stack: (?P<loc_stack>.*)'
        ),
        re.DOTALL,
    )

    for err_exp, err_rcv in zip(errors, received_errors):
        matched = False
        for rgx in [rgx_rsp_exp, rgx_req_exp, rgx_wrong_mock]:
            if matched:
                continue
            rcv_match = rgx.match(err_rcv)
            exp_match = rgx.match(err_exp)
            if rcv_match and exp_match:
                matched = True
                for key in ['rsp', 'exp']:
                    try:
                        rcv_json = json.loads(rcv_match.group(key))
                        exp_json = json.loads(exp_match.group(key))
                        assert rcv_json == exp_json
                    except json.decoder.JSONDecodeError:
                        assert err_exp == err_rcv
                rcv_groups = {
                    k: v
                    for k, v in rcv_match.groupdict().items()
                    if k not in ['rsp', 'exp']
                }
                exp_groups = {
                    k: v
                    for k, v in exp_match.groupdict().items()
                    if k not in ['rsp', 'exp']
                }
                assert rcv_groups == exp_groups, (rcv_groups, exp_groups)
        if not matched:
            assert err_exp == err_rcv, (err_exp, err_rcv)


async def check_testrun_status(
        endpoints,
        handler,
        tests,
        success,
        errors=(),
        validation_errors=(),
        path=None,
):
    path = path or '/test/foo/bar' + str(uuid.uuid4())
    if success:
        # safely_create_endpoint checks that tests have successfully passed
        await endpoints.safely_create_endpoint(
            path, post_handler=handler, tests=tests,
        )
    else:
        with pytest.raises(utils_endpoints.Failure) as validation_result:
            await endpoints.safely_create_endpoint(
                path, post_handler=handler, tests=tests,
            )

        response = validation_result.value.response.json()

        if validation_errors:
            assert {k: v for k, v in response.items() if k != 'details'} == {
                'code': 'validation_failed',
                'message': 'Validation failed',
            }
            assert response['details']['errors'] == validation_errors
        else:
            assert {k: v for k, v in response.items() if k != 'message'} == {
                'code': 'tests_failed',
            }

            assert 'message' in response
            validate_error_message(path, errors, response['message'])


def code_mismatch_error(test_name, response_code, expected_code):
    return (
        '%s: Response code value doesn\'t match the expected one:\n'
        'Response: \'%s\'\n'
        'Expected: \'%s\'.\n' % (test_name, response_code, expected_code)
    )


def config_not_loaded(test_name, config, location):
    return (
        '{}: Exception during test execution: config not loaded: "{}"'.format(
            test_name, config,
        )
        + location_stack(*location)
    )


def body_mismatch_error(test_name, response_body, expected_body, diff=None):
    return (
        '%s: Response body value doesn\'t match the expected one:\n'
        'Response: \'%s\'\n'
        'Expected: \'%s\'%s.\n'
        % (
            test_name,
            response_body,
            expected_body,
            '\nDiff: ' + diff if diff else '',
        )
    )


def headers_mismatch_error(
        test_name, response_headers, expected_headers, diff=None,
):
    return (
        '%s: Response headers value doesn\'t match the expected one:\n'
        'Response: \'%s\'\n'
        'Expected: \'%s\'%s.\n'
        % (
            test_name,
            response_headers,
            expected_headers,
            '\nDiff: ' + diff if diff else '',
        )
    )


def content_type_mismatch_error(test_name, response_type, expected_type):
    return (
        '%s: Response content type value doesn\'t match the expected one:\n'
        'Response: \'"%s"\'\n'
        'Expected: \'"%s"\'.\n' % (test_name, response_type, expected_type)
    )


def url_path_params_mismatch_error(
        test_name, request_type, expected_type, diff=None,
):
    return (
        '%s: Request url path-params value doesn\'t match the expected one:\n'
        'Request: \'%s\'\n'
        'Expected: \'%s\'%s.\n'
        % (
            test_name,
            request_type,
            expected_type,
            '\nDiff: ' + diff if diff else '',
        )
    )


def exception_error(test_name, message):
    return '%s: Exception during test execution: %s\n' % (test_name, message)


def call_count_error(test_name, count, expected):
    return (
        '%s: Mock resource call count doesn\'t match the expected one:\n'
        'call count: %s, expected: %s. location stack: \n'
        % (test_name, count, expected)
    )


def call_order_mismatch(test_name, resource1, order, resource2):
    return (
        '%s: Resource \'%s\' shall be called %s \'%s\', expectations failed. '
        'location stack: \n' % (test_name, resource1, order, resource2)
    )


def mock_request_mismatch(
        test_name, mock, parameter, request, expected, diff=None, source_id=0,
):
    return (
        '%s: Wrong request to mock \'%s\': %s value doesn\'t match the '
        'expected one:\nRequest: \'%s\'\nExpected: \'%s\'%s'
        '. location stack: sources[%d]; sources; responses; /; \n'
        % (
            test_name,
            mock,
            parameter,
            request,
            expected,
            '\nDiff: ' + diff if diff else '',
            source_id,
        )
    )


def location_stack(*stack):
    return '. location stack: ' + '; '.join(list(stack) + ['\n'])


def experiments_consumer_mismatch(test_name, received, expected):
    return (
        (
            '{}: Unexpected experiments consumer name. '
            'Expected \'{}\', but got \'{}\'.\n'
        ).format(test_name, expected, received)
        + location_stack('experiments', '/')
    )


def configs_consumer_mismatch(test_name, received, expected):
    return (
        '{}: Unexpected configs consumer name. '
        'Expected \'{}\', but got \'{}\'.\n'
    ).format(test_name, expected, received) + location_stack('configs', '/')


def experiments_kwargs_mismatch(test_name, extra=None, lost=None, diff=None):
    diff_report = [
        '{}:\n  - {}\n  + {}\n'.format(key, old, new)
        for (key, old, new) in diff or []
    ]
    return (
        (
            '{}: Failed to match expected experiment3 kwargs with received.\n'
            '{}{}{}'
        ).format(
            test_name,
            'Extra keys: {}\n'.format(', '.join(extra)) if extra else '',
            'Lost keys: {}\n'.format(', '.join(lost)) if extra else '',
            ''.join(diff_report),
        )
        + location_stack('experiments', '/')
    )


def configs_kwargs_mismatch(test_name, extra=None, lost=None, diff=None):
    diff_report = [
        '{}:\n  - {}\n  + {}\n'.format(key, old, new)
        for (key, old, new) in diff or []
    ]
    return (
        (
            '{}: Failed to match expected experiment3 kwargs with received.\n'
            '{}{}{}'
        ).format(
            test_name,
            'Extra keys: {}\n'.format(', '.join(extra)) if extra else '',
            'Lost keys: {}\n'.format(', '.join(lost)) if extra else '',
            ''.join(diff_report),
        )
        + location_stack('configs', '/')
    )


def disabled_source_error(test_name, source, location):
    return (
        '{}: Exception during test execution: '
        'attempt to access to disabled source "{}"'.format(test_name, source)
        + location_stack(*location)
    )


def secdist_no_toplevel(test_name, toplevel_key, *stack):
    return (
        f'{test_name}: Exception during test execution: secdist doesn\'t '
        f'have top level section: "{toplevel_key}"' + location_stack(*stack)
    )
