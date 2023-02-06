async def test_downtime_list(web_app_client):
    response = await web_app_client.get('/downtime/list/')
    assert response.status == 200
    content = await response.json()
    assert content == [
        {
            'dc': 'vla',
            'id': 'downtime_id1',
            'queues': ['queue1', 'queue2'],
            'until': '2020-01-02T03:00:00+03:00',
        },
        {
            'dc': 'sas',
            'id': 'downtime_id2',
            'queues': ['queue3'],
            'until': '2020-01-02T15:00:00+03:00',
        },
    ]
