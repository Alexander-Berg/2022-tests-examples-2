async def test_get_timezones(web_app_client):
    response = await web_app_client.get('/api/config/cities/timezones')
    assert response.status == 200

    content = sorted(await response.json(), key=lambda x: x['tz'])
    assert len(content) == 2

    assert content[1] == {'tz': 'Europe/Moscow', 'utcoffset': 3.0}
