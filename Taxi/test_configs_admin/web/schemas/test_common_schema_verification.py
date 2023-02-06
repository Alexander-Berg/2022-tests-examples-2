import pytest

from test_configs_admin.web.schemas import common


@pytest.mark.parametrize(
    common.Case.get_args(),
    [
        pytest.param(
            *common.Case(
                data={
                    'schemas': {
                        'test': {
                            'default': 1,
                            'schema': {'type': 'number'},
                            'description': '',
                            'full_description': '',
                            'name': 'test',
                            'group': 'schemas',
                        },
                    },
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                response_code=400,
                expected_response={
                    'code': 'REQUEST_VALIDATION_ERROR',
                    'message': 'Schema name must be equal `[A-Z][A-Z0-9_]+`',
                },
            ),
            id='fail if key is lower',
        ),
        pytest.param(
            *common.Case(
                data={
                    'schemas': {
                        'TEST': {
                            'default': 1,
                            'schema': {'type': 'number'},
                            'description': '',
                            'full_description': '',
                            'name': 'ANOTHER_TEST',
                            'group': 'schemas',
                        },
                    },
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                response_code=400,
                expected_response={
                    'code': 'REQUEST_VALIDATION_ERROR',
                    'message': (
                        'Field `name` must be equal schema key, '
                        'but it`s not. '
                        'Expected: `ANOTHER_TEST`, found: `TEST`'
                    ),
                },
            ),
            id='fail if key is not equal name',
        ),
        pytest.param(
            *common.Case(
                data={
                    'schemas': {
                        'ANOTHER_TEST': {
                            'default': 1,
                            'schema': {'type': 'number'},
                            'description': '',
                            'full_description': '',
                            'name': 'ANOTHER_TEST',
                            'group': 'schemas',
                        },
                    },
                    'group': 'another_group_schemas',
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                response_code=400,
                expected_response={
                    'code': 'REQUEST_VALIDATION_ERROR',
                    'message': (
                        'Group `schemas` in config schema `ANOTHER_TEST` '
                        'is not equal to group '
                        '`another_group_schemas` in request'
                    ),
                },
            ),
            id='fail if set group and it not equal inner groups',
        ),
    ],
)
async def test(
        web_app_client,
        data,
        not_existed_names,
        response_code,
        expected_response,
):
    response = await web_app_client.post(
        '/v1/schemas/', headers={'X-YaTaxi-Api-Key': 'secret'}, json=data,
    )

    assert response.status == response_code, await response.text()
    assert await response.json() == expected_response
