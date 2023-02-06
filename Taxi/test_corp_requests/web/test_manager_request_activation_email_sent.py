import pytest


@pytest.mark.parametrize(
    ['request_id'], [pytest.param('request_accepting', id='not sent')],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_manager_requests_activation_email_sent(
        mock_personal, web_app_client, db, request_id,
):
    db_item = await db.corp_manager_requests.find_one(
        {'_id': request_id}, projection={'activation_email_sent': 1},
    )
    assert db_item == {'_id': request_id}

    response = await web_app_client.post(
        '/v1/manager-requests/activation_email_sent',
        params={'request_id': request_id},
    )

    assert response.status == 200, await response.json()

    db_item = await db.corp_manager_requests.find_one(
        {'_id': request_id}, projection={'activation_email_sent': 1},
    )
    assert db_item == {'_id': request_id, 'activation_email_sent': True}
