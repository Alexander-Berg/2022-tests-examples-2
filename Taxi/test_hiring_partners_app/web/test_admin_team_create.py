import pytest


async def test_team_create(
        taxi_hiring_partners_app_web, load_json, personal, pgsql,
):
    # act
    response = await taxi_hiring_partners_app_web.post(
        '/admin/v3/team/create',
        json={'name': 'Team A'},
        headers={'X-Yandex-Login': 'yandexlogin_admin'},
    )

    # assert
    body = await response.json()
    assert body == {'team_id': 1}
    assert response.status == 201

    cursor = pgsql['hiring_partners_app'].cursor()
    cursor.execute('SELECT id, name FROM hiring_partners_app.teams;')
    result = [list(row) for row in cursor][0]
    assert result == [1, 'Team A']


@pytest.mark.now('2021-03-03T03:10:00+03:00')
@pytest.mark.parametrize('user', ('yandexlogin_agent', 'fake_user'))
async def test_team_not_create(
        taxi_hiring_partners_app_web, user, load_json, personal,
):
    # arrange
    expected_response = load_json('expected_responses.json')[user]
    expected_body = expected_response['body']
    expected_status = expected_response['status']

    # act
    response = await taxi_hiring_partners_app_web.post(
        '/admin/v3/team/create',
        json={'name': 'Team A'},
        headers={'X-Yandex-Login': user},
    )

    # assert
    body = await response.json()
    assert body == expected_body
    assert response.status == expected_status
