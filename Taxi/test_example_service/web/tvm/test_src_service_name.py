import pytest


@pytest.mark.config(TVM_ENABLED=True)
async def test_name_with_enabled_check(
        web_app_client, patched_tvm_ticket_check,
):
    resp = await web_app_client.get(
        'tvm/whoami', headers={'X-Ya-Service-Ticket': 'good'},
    )
    assert (await resp.json()) == {'name': 'expected_service_name'}


async def test_name_with_disabled_check(
        web_app_client, patched_tvm_ticket_check,
):
    resp = await web_app_client.get('tvm/whoami')
    assert (await resp.json()) == {}
