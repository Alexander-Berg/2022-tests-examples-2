import pytest


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.usefixtures('patch_configs_by_group', 'patch_call_command')
@pytest.mark.parametrize(
    'headers, response_code',
    [
        ({'X-Ya-Service-Ticket': 'bad_key'}, 200),
        ({}, 200),
        ({'X-Ya-Service-Ticket': 'good'}, 200),
    ],
)
async def test_get_actual_commit_hash(
        web_app_client, headers, response_code, patcher_tvm_ticket_check,
):
    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.get(
        '/v1/schemas/actual_commit/', headers=headers,
    )

    assert response.status == response_code
    if response.status == 200:
        assert await response.json() == {
            'commit': 'b805804d8b5ce277903492c549055f4b5a86ed0a',
        }
