import pytest

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql(
        'supportai', files=['default.sql', 'sample_scenarios.sql'],
    ),
]


async def test_get_topics(web_app_client):
    all_topics_response = await web_app_client.get(
        '/v1/topics?user_id=1&project_slug=ya_lavka',
    )
    assert all_topics_response.status == 200
    assert len((await all_topics_response.json())['topics']) == 4
    child_topics_response = await web_app_client.get(
        '/v1/topics?user_id=1&project_slug=ya_lavka&parent_id=1',
    )
    assert child_topics_response.status == 200
    assert len((await child_topics_response.json())['topics']) == 2
    top_topics_response = await web_app_client.get(
        '/v1/topics?user_id=1&project_slug=ya_lavka&is_top=true',
    )
    assert top_topics_response.status == 200
    assert len((await top_topics_response.json())['topics']) == 1
    invalid_topics_response = await web_app_client.get(
        '/v1/topics?user_id=1&project_slug=ya_lavka&is_top=true&parent_id=2',
    )
    assert invalid_topics_response.status == 400


def check_topic_content(topic, ref_topic):
    assert topic['slug'] == ref_topic['slug']
    assert topic['title'] == ref_topic['title']

    if 'rule' in ref_topic:
        assert topic['rule'] == topic['rule']

    if 'parent_id' in ref_topic:
        assert topic['parent_id'] == ref_topic['parent_id']


async def create_topic(web_app_client, ref_topic, project_slug):

    new_topic_response = await web_app_client.post(
        f'/v1/topics?user_id=1&project_slug={project_slug}', json=ref_topic,
    )

    assert new_topic_response.status == 200
    new_topic = await new_topic_response.json()

    check_topic_content(new_topic, ref_topic)

    all_topics_response = await web_app_client.get(
        f'/v1/topics?user_id=1&project_slug={project_slug}',
    )

    all_topics_response_json = await all_topics_response.json()

    assert len(all_topics_response_json['topics']) == 1

    assert new_topic['id'] in [
        entity['id'] for entity in all_topics_response_json['topics']
    ]


async def test_create_topic_with_rule(web_app_client):
    ref_topic = {
        'id': '',
        'slug': 'topic6',
        'title': 'Тема 6',
        'rule': (
            'model_sure_topic is \'topic6\' and last_user_message '
            'is not \'none\' and united_user_messages_length > 0'
        ),
    }

    await create_topic(web_app_client, ref_topic, 'ya_market')


async def test_create_topic_with_parent(web_app_client):
    ref_topic = {
        'id': '',
        'parent_id': '3',
        'slug': 'topic6',
        'title': 'Тема 6',
        'rule': 'true',
    }

    await create_topic(web_app_client, ref_topic, 'ya_market')


async def test_create_topic_without_parent(web_app_client):
    ref_topic = {'id': '', 'slug': 'topic6', 'title': 'Тема 6', 'rule': 'true'}

    await create_topic(web_app_client, ref_topic, 'ya_market')


async def test_create_topic_with_incorrect_rule(web_app_client):
    response = await web_app_client.post(
        '/v1/topics?user_id=1&project_slug=ya_market',
        json={
            'id': '',
            'slug': 'topic6',
            'title': 'Тема 6',
            'rule': 'feature is not None',
        },
    )

    assert response.status == 400


async def test_create_topic_with_incorrect_parent(web_app_client):
    update_topic_response = await web_app_client.post(
        '/v1/topics?user_id=1&project_slug=ya_market',
        json={
            'id': '',
            'parent_id': '10',
            'slug': 'topic6',
            'title': 'Тема 6',
            'rule': 'true',
        },
    )

    assert update_topic_response.status == 400


async def test_post_topics_bulk(web_app_client):

    ref_topics = [
        {
            'id': '',
            'slug': 'topic7',
            'title': 'Тема 7',
            'rule': 'united_user_messages is not \'none\'',
        },
        {'id': '', 'slug': 'topic8', 'title': 'Тема 8', 'rule': 'true'},
    ]

    topics_response = await web_app_client.post(
        '/supportai/v1/topics?user_id=1&project_slug=ya_lavka',
        json={'topics': ref_topics},
    )

    assert topics_response.status == 200

    new_topics = (await topics_response.json())['topics']

    assert len(new_topics) == 2

    for idx, ref_topic in enumerate(ref_topics):
        check_topic_content(new_topics[idx], ref_topic)


async def test_update_topic(web_app_client):
    ref_topic = {
        'id': '3',
        'slug': 'topic6',
        'title': 'Тема 6',
        'rule': 'True',
    }

    update_topic_response = await web_app_client.put(
        '/v1/topics/3?user_id=1&project_slug=ya_lavka', json=ref_topic,
    )

    assert update_topic_response.status == 200
    updated_topic = await update_topic_response.json()

    check_topic_content(updated_topic, ref_topic)

    all_topics_response = await web_app_client.get(
        '/v1/topics?user_id=1&project_slug=ya_lavka',
    )

    all_topics_response_json = await all_topics_response.json()

    for topic in all_topics_response_json['topics']:
        if topic['id'] == ref_topic['id']:
            check_topic_content(topic, ref_topic)
            break


async def test_update_non_existing_topic(web_app_client):
    update_topic_response = await web_app_client.put(
        '/v1/topics/1000?user_id=1&project_slug=ya_market',
        json={
            'id': '1000',
            'parent_id': '2',
            'slug': 'topic6',
            'title': 'Тема 6',
        },
    )

    assert update_topic_response.status == 400


async def test_update_topic_with_incorrect_parent(web_app_client):
    update_topic_response = await web_app_client.post(
        '/v1/topics?user_id=1&project_slug=ya_lavka',
        json={
            'id': '1',
            'parent_id': '10',
            'slug': 'topic1',
            'title': 'Тема 1',
        },
    )

    assert update_topic_response.status == 400


async def test_update_topic_without_access(web_app_client):

    remove_topic_response = await web_app_client.put(
        '/v1/topics/1?user_id=1&project_slug=ya_market',
        json={'id': '1', 'slug': 'topic1', 'title': 'Тема 1'},
    )

    assert remove_topic_response.status == 403


async def test_delete_topic_with_scenario(web_app_client, mockserver):
    @mockserver.json_handler(
        '/supportai-reference-phrases/v1/matrix/topic/topic4',
    )
    async def _(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/supportai-reference-phrases/v1/matrix/topic/topic4/confirm',
    )
    async def _(request):
        return mockserver.make_response(status=200)

    remove_topic_response = await web_app_client.delete(
        '/v1/topics/4?user_id=1&project_slug=ya_lavka',
    )

    assert remove_topic_response.status == 200

    all_topics_response = await web_app_client.get(
        '/v1/topics?user_id=1&project_slug=ya_lavka',
    )

    assert len((await all_topics_response.json())['topics']) == 3

    search_resp = await web_app_client.post(
        '/v1/scenarios/search?user_id=1&project_slug=ya_lavka',
        json={'search_text': 'Scenario'},
    )
    search_resp_data = await search_resp.json()
    assert not search_resp_data['scenarios']


async def test_delete_root_topic(web_app_client, mockserver):
    @mockserver.json_handler(
        '/supportai-reference-phrases/v1/matrix/topic/topic1',
    )
    async def _(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/supportai-reference-phrases/v1/matrix/topic/topic1/confirm',
    )
    async def _(request):
        return mockserver.make_response(status=200)

    remove_topic_response = await web_app_client.delete(
        '/v1/topics/1?user_id=1&project_slug=ya_lavka',
    )

    assert remove_topic_response.status == 400


async def test_delete_topic_without_access(web_app_client, mockserver):
    @mockserver.json_handler(
        '/supportai-reference-phrases/v1/matrix/topic/topic1',
    )
    async def _(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/supportai-reference-phrases/v1/matrix/topic/topic1/confirm',
    )
    async def _(request):
        return mockserver.make_response(status=200)

    remove_topic_response = await web_app_client.delete(
        '/v1/topics/1?user_id=1&project_slug=ya_market',
    )

    assert remove_topic_response.status == 403
