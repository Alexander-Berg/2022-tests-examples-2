import pytest


@pytest.mark.pgsql('gpbm', files=['terminated.sql'])
async def test_get_terminated_query_list(
        web_app_client, gpdb_manager_api_auth_mock, load_json,
):
    response = await web_app_client.get(
        '/internal/gpdb-manager-api/v1/terminator/list',
        params={
            'database_name': 'ritchie',
            'from_dttm': '2022-07-27T11:45:11+0300',
            'to_dttm': '2022-07-27T13:45:11+0300',
            'user_name': 'unittest_user',
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == load_json('terminated_ritchie.json')

    response = await web_app_client.get(
        '/internal/gpdb-manager-api/v1/terminator/list',
        params={
            'database_name': 'butthead',
            'from_dttm': '2022-07-27T11:45:11+0300',
            'to_dttm': '2022-07-27T13:45:11+0300',
            'user_name': 'unittest_user',
        },
    )
    assert response.status == 200
    content = await response.json()
    print(content)
    assert content == load_json('terminated_butthead.json')
