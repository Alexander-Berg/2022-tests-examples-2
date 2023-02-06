import pytest


@pytest.mark.usefixtures('mocks_chat_change_status')
async def test_change_status_chat_on_trigger(web_app_client, pgsql):
    res = await web_app_client.post(
        '/v1/case/corp_support_chat/update_status',
        headers={'authorization': 'token'},
        json={'sf_id': '1', 'status': 'OnHold'},
    )

    assert res.status == 200

    res = await web_app_client.post(
        '/v1/case/corp_support_chat/update_status',
        headers={'authorization': 'token1'},
        json={'sf_id': '1', 'status': 'OnHold'},
    )

    assert res.status == 401

    res = await web_app_client.post(
        '/v1/case/corp_support_chat/update_status',
        headers={'authorization': 'token'},
        json={'sf_id': '2', 'status': 'OnHold'},
    )

    assert res.status == 500
