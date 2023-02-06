import pytest


USER_PARAMS = 'requests/user_general.json'


@pytest.mark.pgsql('sms_intents_admin', files=['test_get.sql'])
async def test_get_ok_correct(web_app_client, load_json):
    intent_data = load_json(USER_PARAMS)

    response = await web_app_client.get(
        '/v1/internal/get', params={'intent': 'test_user'},
    )
    assert response.status == 200

    content = await response.json()
    assert content.pop('status') == 'active'
    assert content.pop('is_correct') is True
    assert content.pop('updated') == '2018-06-23T05:10:25+0300'
    assert content == intent_data


@pytest.mark.pgsql('sms_intents_admin', files=['test_get.sql'])
async def test_get_ok_incorrect(web_app_client, load_json):
    response = await web_app_client.get(
        '/v1/internal/get', params={'intent': 'intent_without_texts'},
    )
    assert response.status == 200

    content = await response.json()
    assert content.pop('is_correct') is False


async def test_get_404(web_app_client):
    response = await web_app_client.get(
        '/v1/internal/get', params={'intent': 'unexisting_intent'},
    )
    assert response.status == 404
