import datetime


async def test_get_empty_limits(web_app_client):
    params = {'resume_id': 1}
    response = await web_app_client.post(
        '/v1/resumes/purachase_limit', params=params,
    )
    content = await response.json()
    today = str(datetime.datetime.utcnow().strftime('%Y-%m-%d'))
    assert response.status == 200
    assert content['created'] == today
    assert content['requests'] == 1
