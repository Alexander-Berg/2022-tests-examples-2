import pytest

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql(
        'supportai',
        files=['additional_version.sql', 'default.sql', 'data.sql'],
    ),
]


@pytest.mark.parametrize('internal', [True, False])
async def test_get_draft_version(web_app_client, internal):
    response = await web_app_client.get(
        ('supportai' if internal else '')
        + '/v1/versions/draft?project_slug=ya_lavka&user_id=1',
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['draft']
    assert response_json['status'] == 'loaded'

    await web_app_client.put(
        '/v1/topics/7?user_id=1&project_slug=ya_lavka',
        json={
            'id': '7',
            'slug': 'topic2',
            'title': 'New name',
            'rule': 'true',
        },
    )

    response = await web_app_client.get(
        '/v1/versions/draft?project_slug=ya_lavka&user_id=1',
    )

    assert response.status == 200

    response_json = await response.json()
    assert response_json['status'] == 'need_to_load'


async def test_draft_version_reload(web_app_client):
    response = await web_app_client.post(
        '/v1/versions/draft/reload?project_slug=ya_lavka&user_id=1',
    )

    assert response.status == 304

    await web_app_client.put(
        '/v1/topics/7?user_id=1&project_slug=ya_lavka',
        json={
            'id': '7',
            'slug': 'topic2',
            'title': 'New name',
            'rule': 'true',
        },
    )

    response = await web_app_client.post(
        '/v1/versions/draft/reload?project_slug=ya_lavka&user_id=1',
    )

    assert response.status == 200
    response_json = await response.json()

    assert response_json['status'] == 'loading'


@pytest.mark.parametrize(
    ('exclude_entities', 'status'),
    [
        ([], 200),
        (['tags', 'lines', 'features', 'scenarios'], 200),
        (['topics'], 400),
    ],
)
async def test_draft_version_copy(web_app_client, exclude_entities, status):

    response = await web_app_client.post(
        '/supportai/v1/versions/draft/copy?project_slug=ya_lavka',
        json={'exclude_entities': exclude_entities},
    )

    assert response.status == status

    if status == 200:
        response_json = await response.json()
        version_id = response_json['id']

        await web_app_client.post(
            f'/v1/versions/{version_id}/reveal?project_slug=ya_lavka',
        )

        response = await web_app_client.delete(
            '/v1/versions/1?project_slug=ya_lavka&user_id=34',
        )

        assert response.status == 200


@pytest.mark.config(
    SUPPORTAI_RELEASE_SETTINGS={
        'projects': [{'project_slug': 'ya_lavka', 'limit': 10}],
    },
)
async def test_draft_version_release(web_app_client):

    response = await web_app_client.post(
        '/v1/versions/draft/release?project_slug=ya_lavka&user_id=34',
        json={'name': 'Version22'},
    )

    assert response.status == 200

    response_json = await response.json()
    assert response_json['name'] == 'Version22'
    version_id = response_json['id']

    response = await web_app_client.get(
        '/supportai/v1/topics',
        params={
            'project_slug': 'ya_lavka',
            'version': version_id,
            'limit': 10,
            'offset': 0,
        },
    )

    topics = (await response.json())['topics']

    assert len(topics) == 2

    topic_id_to_slug = {topic['id']: topic['slug'] for topic in topics}
    topic_slug_to_topic = {topic['slug']: topic for topic in topics}

    assert 'parent_id' not in topic_slug_to_topic['topic1']
    assert (
        topic_id_to_slug[topic_slug_to_topic['topic2']['parent_id']]
        == 'topic1'
    )

    assert response.status == 200


async def test_delete_version(web_app_client):
    response = await web_app_client.delete(
        '/v1/versions/1?project_slug=ya_lavka&user_id=34',
    )

    assert response.status == 200

    response = await web_app_client.get(
        '/v1/tags?user_id=1&project_slug=ya_lavka',
    )
    assert response.status == 200
    assert not (await response.json())['tags']


async def test_delete_last_draft_version(web_app_client):
    response = await web_app_client.delete(
        '/v1/versions/4?project_slug=ya_taxi&user_id=34',
    )

    assert response.status == 200

    response = await web_app_client.delete(
        '/v1/versions/3?project_slug=ya_taxi&user_id=34',
    )

    assert response.status == 400


async def test_delete_incorrect_versions(web_app_client):
    response = await web_app_client.delete(
        '/v1/versions/1?project_slug=ya_market&user_id=34',
    )

    assert response.status == 400

    response = await web_app_client.delete(
        '/v1/versions/2?project_slug=ya_market&user_id=34',
    )

    assert response.status == 400


async def test_reveal_versions(web_app_client):
    response = await web_app_client.post(
        '/supportai/v1/versions/2/reveal?project_slug=ya_lavka',
    )

    assert response.status == 400

    version = await web_app_client.post(
        '/supportai/v1/versions/draft/copy?project_slug=ya_lavka',
        json={'exclude_entities': []},
    )

    assert version.status == 200

    version_json = await version.json()
    version_id = version_json['id']

    response = await web_app_client.post(
        f'/supportai/v1/versions/{version_id}/reveal?project_slug=ya_lavka',
    )

    assert response.status == 200

    response_json = await response.json()
    assert not response_json['hidden']


async def test_versions_all(web_app_client):
    response = await web_app_client.get(
        '/v1/versions/release?project_slug=ya_lavka&user_id=34',
    )

    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['versions']) == 2


async def test_versions_percentage(web_app_client):
    response = await web_app_client.post(
        '/v1/versions/percentage?project_slug=ya_lavka&user_id=34',
        json={
            'mapping': [
                {'version_id': 1001, 'percentage': 20},
                {'version_id': 1002, 'percentage': 80},
            ],
        },
    )

    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['versions']) == 2
    assert response_json['versions'][0]['percentage'] == 20
    assert response_json['versions'][1]['percentage'] == 80
