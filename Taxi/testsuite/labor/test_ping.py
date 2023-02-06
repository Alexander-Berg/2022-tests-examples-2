def test_labor_ping(taxi_labor):
    response = taxi_labor.get('ping')
    assert response.status_code == 200
    assert response.text == 'ok'
