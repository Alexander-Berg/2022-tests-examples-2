async def test_simple(taxi_client_notify):
    response = await taxi_client_notify.post(
        '/v1/acknowledge',
        json={
            'notification_id': 'notification_id',
            'client_id': '5ca55b1b41844d378da1168ff688a2ad',
            'client_dttm': '2019-01-10T22:39:50+03:00',
            'status': 'shown',
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
