import pytest


@pytest.mark.pgsql('crm_admin', files=['dict_ticket_statuses.sql'])
async def test_without_lang(web_app_client):
    response = await web_app_client.get('/v1/dictionaries/ticket_states')
    assert response.status == 200
    response_data: list = await response.json()
    excepted = [
        {'label': 'Открыт', 'value': 'open'},
        {'label': 'В работе', 'value': 'inProgress'},
        {'label': 'Одобрено', 'value': 'agreed'},
        {'label': 'Закрыт', 'value': 'closed'},
    ]
    assert response_data == excepted


@pytest.mark.pgsql('crm_admin', files=['dict_ticket_statuses.sql'])
async def test_ru(web_app_client):
    response = await web_app_client.get(
        '/v1/dictionaries/ticket_states?language=ru',
    )
    assert response.status == 200
    response_data: list = await response.json()
    excepted = [
        {'label': 'Открыт', 'value': 'open'},
        {'label': 'В работе', 'value': 'inProgress'},
        {'label': 'Одобрено', 'value': 'agreed'},
        {'label': 'Закрыт', 'value': 'closed'},
    ]
    assert response_data == excepted


@pytest.mark.pgsql('crm_admin', files=['dict_ticket_statuses.sql'])
async def test_en(web_app_client):
    response = await web_app_client.get(
        '/v1/dictionaries/ticket_states?language=en',
    )
    assert response.status == 200
    response_data: list = await response.json()
    excepted = [
        {'label': 'Open', 'value': 'open'},
        {'label': 'In Progress', 'value': 'inProgress'},
        {'label': 'Agreed', 'value': 'agreed'},
        {'label': 'Closed', 'value': 'closed'},
    ]
    assert response_data == excepted
