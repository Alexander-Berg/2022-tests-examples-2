import pytest


@pytest.mark.filldb(uconfigs_meta='default')
async def test_get_groups_list(web_app_client, patcher_tvm_ticket_check):
    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.get(
        '/v1/configs/groups/list', headers={'X-Ya-Service-Ticket': 'good'},
    )
    assert response.status == 200
    result = await response.json()
    assert result == [
        {'name': 'devicenotify'},
        {'name': 'first_name'},
        {'name': 'new_group'},
    ]
