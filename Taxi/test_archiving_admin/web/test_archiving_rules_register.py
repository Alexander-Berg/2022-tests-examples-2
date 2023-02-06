import pytest


def _make_rule_to_register(
        rule_name='foo', *, group_name='abc', ttl_type='now',
):
    return {
        'rule_name': rule_name,
        'source_type': 'bar',
        'group_name': group_name,
        'ttl_info': {
            'duration_default': 123,
            'field': 'updated',
            'savepoint_type': ttl_type,
        },
        'period': 86400,
        'sleep_delay': 5,
    }


@pytest.mark.parametrize(
    'rule_request,expected_code,expected_response',
    [
        (
            {'rules': [_make_rule_to_register()]},
            200,
            {
                'rules': [
                    {
                        'rule_name': 'foo',
                        'source_type': 'bar',
                        'group_name': 'abc',
                    },
                ],
            },
        ),
        (
            {
                'rules': [
                    _make_rule_to_register(),
                    _make_rule_to_register('foo2'),
                ],
            },
            200,
            {
                'rules': [
                    {
                        'rule_name': 'foo',
                        'source_type': 'bar',
                        'group_name': 'abc',
                    },
                    {
                        'rule_name': 'foo2',
                        'source_type': 'bar',
                        'group_name': 'abc',
                    },
                ],
            },
        ),
        (
            {
                'rules': [
                    {
                        'rule_name': 'foo',
                        'source_type': 'bar',
                        'group_name': 'abc',
                        'sleep_delay': 2,
                    },
                ],
            },
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'period is required property'},
                'message': 'Some parameters are invalid',
            },
        ),
        (
            {'rules': [_make_rule_to_register(), _make_rule_to_register()]},
            400,
            {
                'code': 'rule-register-error',
                'message': 'Found duplicate rule in request: foo',
            },
        ),
        (
            {'rules': [_make_rule_to_register(ttl_type='bad')]},
            409,
            {
                'message': 'Unexpected ttl savepoint type: bad',
                'code': 'rule-register-error',
            },
        ),
    ],
)
async def test_register(
        web_app_client, rule_request, expected_code, expected_response,
):
    response = await web_app_client.post(
        '/archiving/v1/rules/register', json=rule_request,
    )
    assert response.status == expected_code, await response.text()
    content = await response.json()
    assert content == expected_response


async def test_register_twice(web_app_client):
    response = await web_app_client.post(
        '/archiving/v1/rules/register',
        json={'rules': [_make_rule_to_register()]},
    )
    assert response.status == 200, await response.text()
    content = await response.json()
    assert content == {
        'rules': [
            {'rule_name': 'foo', 'source_type': 'bar', 'group_name': 'abc'},
        ],
    }

    response = await web_app_client.post(
        '/archiving/v1/rules/register',
        json={
            'rules': [
                _make_rule_to_register(),
                _make_rule_to_register('foo2'),
            ],
        },
    )
    assert response.status == 200, await response.text()
    content = await response.json()
    assert content == {
        'rules': [
            {'rule_name': 'foo2', 'source_type': 'bar', 'group_name': 'abc'},
        ],
    }

    response = await web_app_client.post(
        '/archiving/v1/rules/register',
        json={'rules': [_make_rule_to_register(group_name='vvv')]},
    )
    assert response.status == 200, await response.text()
    content = await response.json()
    assert content == {
        'rules': [
            {'rule_name': 'foo', 'source_type': 'bar', 'group_name': 'vvv'},
        ],
    }
