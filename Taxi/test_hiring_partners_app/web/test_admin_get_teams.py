async def test_get_all_teams(taxi_hiring_partners_app_web):
    # act
    response = await taxi_hiring_partners_app_web.get('/admin/v3/teams')

    # assert
    assert response.status == 200
    body = await response.json()
    assert body == {
        'teams': [
            {'id': 1, 'name': 'Team A'},
            {'id': 2, 'name': 'Team Fortress'},
            {'id': 3, 'name': 'Dream Team'},
        ],
    }
