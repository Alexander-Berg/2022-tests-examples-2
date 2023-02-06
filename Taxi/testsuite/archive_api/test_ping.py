def test_ping(taxi_archive_api):
    response = taxi_archive_api.get('ping')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
