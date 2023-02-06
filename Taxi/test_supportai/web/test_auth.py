import pytest


@pytest.mark.pgsql('supportai', files=['default.sql'])
@pytest.mark.disable_standard_auth
async def test_auth(web_app_client, mockserver):
    @mockserver.json_handler(
        '/supportai-tasks/supportai-tasks/v1/users/1/projects/ya_lavka',
        regex=True,
    )
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'id': '1',
                'slug': 'project',
                'title': 'Project',
                'capabilities': [],
                'is_chatterbox': False,
                'permissions': ['read'],
            },
        )

    @mockserver.json_handler(
        '/supportai-tasks/supportai-tasks/v1/users/1/projects/ya_market',
        regex=True,
    )
    async def _(request):
        return mockserver.make_response(status=403)

    response = await web_app_client.get(
        f'/v1/topics?user_id=1&project_slug=ya_lavka',
    )
    assert response.status == 200

    response_json = await response.json()
    topic = response_json['topics'][0]
    topic_id = topic['id']

    response = await web_app_client.put(
        f'/v1/topics/{topic_id}?user_id=1&project_slug=ya_lavka', json=topic,
    )
    assert response.status == 403

    response = await web_app_client.get(f'/v1/topics?project_slug=ya_lavka')
    assert response.status == 403

    response = await web_app_client.get(
        f'/v1/topics?user_id=1&project_slug=ya_market',
    )
    assert response.status == 403
