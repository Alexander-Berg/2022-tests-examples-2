async def test_get_drivers_dbs(atlas_blackbox_mock, web_app_client):
    response = await web_app_client.post(
        '/api/drivers/dbs', json={'driver_id': 'uuid1'},
    )
    assert response.status == 200
    data = await response.json()
    expected = [
        {
            'driver_id': 'uuid1',
            'park_id': 'park_id1',
            'clid': 'clid1',
            'park_name': 'ЗооПарк',
        },
        {'driver_id': 'uuid1', 'park_id': 'park_id3', 'clid': 'clid3'},
    ]
    assert data == expected


async def test_get_driver_info(atlas_blackbox_mock, web_app_client):
    response = await web_app_client.post(
        '/api/drivers/info', json={'driver_id': 'uuid1'},
    )
    assert response.status == 200
    data = await response.json()
    expected = {
        'name': 'Юнус Обладатель Рыбы',
        'phone': 'phone_pd_id_1',
        'uuid': 'uuid1',
        'db_id': 'park_id1',
        'profile_state': 'active',
        'car_row_model': 'BMW X6',
        'car_number': 'AA111YYY',
        'park_name': 'ЗооПарк',
        'clid': 'clid1',
        'driver_license': '',
        'status_updated': '',
        'allowed_class': ['Фортуна:Эконом', 'Фортуна:Комфорт'],
    }
    assert data == expected
