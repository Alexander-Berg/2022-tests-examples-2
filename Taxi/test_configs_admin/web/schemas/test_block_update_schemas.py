import pytest

from test_configs_admin.web.schemas import common


@pytest.mark.parametrize(
    common.Case.get_args(),
    [
        pytest.param(
            *common.Case(
                data={
                    'schemas': {
                        'TEST': {
                            'name': 'TEST',
                            'default': 1,
                            'schema': {'type': 'number'},
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                        },
                    },
                    'group': 'schemas',
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                response_code=409,
                expected_response={
                    'code': 'SCHEMA_UPDATE_LOCKED',
                    'message': (
                        'Update schemas is locked until 2219-03-06 11:00:00'
                    ),
                },
            ),
            id='fail update schema by lock it for schemas update',
        ),
    ],
)
async def test(
        web_context,
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
