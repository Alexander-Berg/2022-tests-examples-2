import json

import pytest

from . import common


@pytest.mark.parametrize(
    'status_code,request_json,method,uri,request_body,response_body',
    [
        (
            200,
            {'name': 'abacaba'},
            'POST',
            '/custom_logging',
            {'name': 'hide'},
            {'name': 'response hide'},
        ),
        (
            200,
            {'name': 'serialize'},
            'POST',
            '/custom_logging',
            {'name': 'hide'},
            {'name': 'serialize response'},
        ),
        (
            500,
            {'name': 'abacaba', 'throw_exception': True},
            'POST',
            '/custom_logging',
            {'name': 'hide', 'throw_exception': True},
            {
                'message': 'Internal server error',
                'code': 'INTERNAL_SERVER_ERROR',
                'details': {'reason': 'some error'},
            },
        ),
        (
            400,
            {'name': 'abacaba', 'request_validate_fail': True},
            'POST',
            '/custom_logging',
            {'name': 'hide', 'request_validate_fail': True},
            {'name': 'response hide', 'greetings': 'Hello, somebody!'},
        ),
        (
            400,
            {'name': 'very very long name', 'request_validate_fail': True},
            'POST',
            '/custom_logging',
            {'name': 'hide', 'request_validate_fail': True},
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Some parameters are invalid',
                'details': {
                    'reason': (
                        'Invalid value for name: \'very very long '
                        'name\' length must be less than or equal '
                        'to 10'
                    ),
                },
            },
        ),
        (
            500,
            {'name': 'abacaba', 'response_validate_fail': True},
            'POST',
            '/custom_logging',
            {'name': 'hide', 'response_validate_fail': True},
            {
                'message': 'Internal server error',
                'code': 'INTERNAL_SERVER_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for name: \'very very very '
                        'very long name\' length must be less than '
                        'or equal to 10'
                    ),
                },
            },
        ),
        (
            500,
            {'name': 'abacaba', 'response_validate_fail_2': True},
            'POST',
            '/custom_logging',
            {'name': 'hide', 'response_validate_fail_2': True},
            {
                'code': 'RESPONSE_VALIDATION_ERROR',
                'message': 'Response validation or serialization failed',
                'details': {
                    'reason': (
                        'Invalid value for SomeHeader: 101 must '
                        'be a value less than or equal to 100'
                    ),
                },
            },
        ),
    ],
)
async def test_custom_logging(
        web_app_client,
        caplog,
        status_code,
        request_json,
        method,
        uri,
        request_body,
        response_body,
):
    response = await web_app_client.post(
        '/custom_logging',
        json=request_json,
        headers={'Content-Type': 'text/html'},
    )
    assert response.status == status_code

    request_log, response_log = common.get_request_response(caplog)
    assert request_log.extdict['method'] == method
    assert request_log.extdict['uri'] == uri
    assert request_log.extdict['body'] == json.dumps(request_body)

    assert response_log.extdict['method'] == method
    assert response_log.extdict['uri'] == uri
    assert response_log.extdict['body'] == json.dumps(response_body)
