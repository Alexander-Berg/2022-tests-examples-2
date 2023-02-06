def test_service_statistics(taxi_labor):
    response = taxi_labor.get('service/statistics')
    assert response.status_code == 200
    body = response.json()
    assert 'total' in body
    total = body['total']
    assert 'code' in total
    assert 'message' in total
