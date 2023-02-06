import pytest


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_chatterbox.sql'],
)
async def test_get_chatterbox_logins(web_app_client):
    response = await web_app_client.get('/api/v1/chatterbox/logins')
    assert response.status == 200, await response.text()

    data = await response.json()
    logins = sorted(data['logins'])
    assert logins == ['login_1', 'login_2']


@pytest.mark.config(ATLAS_BACKEND_CHATTERBOX_LINES_LIST=['line_1', 'line_2'])
async def test_get_chatterbox_lines(web_app_client):
    response = await web_app_client.get('/api/v1/chatterbox/lines')
    assert response.status == 200, await response.text()

    data = await response.json()
    lines = sorted(data['lines'])
    assert lines == ['line_1', 'line_2']
