async def test_ride_report_user_get_not_found(web_app_client):
    response = await web_app_client.get(
        '/v1/ride_report/users', params={'user_id': 'unknown'},
    )
    assert response.status == 404


async def test_ride_report_user_get_success(web_app_client):
    response = await web_app_client.get(
        '/v1/ride_report/users', params={'user_id': 'test_user_3'},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'client_id': 'client3',
        'fullname': 'fullname',
        'id': 'test_user_3',
        'personal_phone_id': 'phone_pd_id_3',
    }
