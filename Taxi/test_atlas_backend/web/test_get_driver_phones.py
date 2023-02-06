async def test_get_driver_phones(atlas_blackbox_mock, web_app_client):
    response = await web_app_client.post(
        '/api/map/drivers-phones', json={'drivers': ['parkid4_uuid4']},
    )
    assert response.status == 200
    data = await response.json()
    expected = {'parkid4_uuid4': 'phone_pd_id_4'}
    assert data == expected
