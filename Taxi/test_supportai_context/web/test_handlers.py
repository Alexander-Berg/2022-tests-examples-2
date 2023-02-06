import datetime

import pytest


@pytest.mark.pgsql('supportai_context', files=['sample.sql'])
async def test_get_context(web_app_client):
    response = await web_app_client.get(
        '/v1/context?chat_id=123&project_id=demo_dialog',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['records']) == 2

    assert 'created_at' in response_json['records'][0]
    assert 'is_hidden' in response_json['records'][0]
    assert 'is_sent' in response_json['records'][0]

    response = await web_app_client.get(
        '/v1/context/dialog?chat_id=123&project_id=demo_dialog',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['dialog']['messages']) == 3

    response = await web_app_client.get(
        '/v1/context/dialog?chat_id=123&project_id=demo_dialog&'
        'exclude_hidden=false',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['dialog']['messages']) == 3


async def test_post_context_record(web_app_client):
    get_url = '/v1/context?chat_id=1&project_id=demo_dialog'
    post_url = '/v1/context/record?chat_id=1&project_id=demo_dialog'

    first_get = await web_app_client.get(get_url)
    assert first_get.status == 204

    first_post = await web_app_client.post(
        post_url,
        json={
            'request': {
                'dialog': {'messages': [{'text': 'hello', 'author': 'user'}]},
                'features': [],
            },
            'response': {
                'reply': {'text': 'hi', 'texts': ['hi']},
                'features': {
                    'most_probable_topic': 'topic1',
                    'sure_topic': 'topic1',
                    'probabilities': [
                        {'topic_name': 'topic1', 'probability': 0.87},
                    ],
                },
            },
        },
    )
    assert first_post.status == 200

    second_get = await web_app_client.get(get_url)
    assert second_get.status == 200
    second_get_json = await second_get.json()
    records = second_get_json['records']
    assert len(records) == 1

    assert 'created_at' in records[0]

    second_post = await web_app_client.post(
        post_url,
        json={
            'request': {
                'dialog': {
                    'messages': [
                        {'text': 'im in a trouble', 'author': 'user'},
                    ],
                },
                'features': [],
            },
            'response': {
                'reply': {
                    'text': 'we can solve it',
                    'texts': ['we can solve it'],
                },
                'features': {
                    'most_probable_topic': 'topic2',
                    'sure_topic': 'topic2',
                    'probabilities': [
                        {'topic_name': 'topic2', 'probability': 0.9},
                    ],
                },
            },
        },
    )
    assert second_post.status == 200

    third_get = await web_app_client.get(get_url)
    assert third_get.status == 200
    records = (await third_get.json())['records']
    assert len(records) == 2
    assert not records[-1]['is_hidden']
    assert records[-1]['is_sent']

    third_post = await web_app_client.post(
        post_url + '&is_hidden=true',
        json={
            'request': {
                'dialog': {'messages': [{'text': 'hello', 'author': 'user'}]},
                'features': [],
            },
            'response': {
                'reply': {'text': 'hi', 'texts': ['hi']},
                'features': {
                    'most_probable_topic': 'topic2',
                    'sure_topic': 'topic2',
                    'probabilities': [
                        {'topic_name': 'topic2', 'probability': 0.9},
                    ],
                },
            },
        },
    )
    assert third_post.status == 200

    fourth_get = await web_app_client.get(get_url)
    assert fourth_get.status == 200
    records = (await fourth_get.json())['records']
    assert len(records) == 3
    assert records[-1]['is_hidden']

    fourth_post = await web_app_client.post(
        post_url + '&is_sent=false',
        json={
            'request': {
                'dialog': {'messages': [{'text': 'hello', 'author': 'user'}]},
                'features': [],
            },
            'response': {
                'reply': {'text': 'hi', 'texts': ['hi']},
                'features': {
                    'most_probable_topic': 'topic2',
                    'sure_topic': 'topic2',
                    'probabilities': [
                        {'topic_name': 'topic2', 'probability': 0.9},
                    ],
                },
            },
        },
    )
    assert fourth_post.status == 200

    fifth_get = await web_app_client.get(get_url)
    assert fifth_get.status == 200
    records = (await fifth_get.json())['records']
    assert len(records) == 4
    assert not records[-1]['is_sent']


@pytest.mark.pgsql('supportai_context', files=['sample.sql'])
async def test_search_contexts(web_app_client):
    response = await web_app_client.get('/v1/contexts?project_id=demo_dialog')
    assert response.status == 200
    assert len((await response.json())['contexts']) == 3

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&topic=help',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['contexts']) == 2

    records = response_json['contexts'][1]['records']
    assert len(records) == 2

    assert records[0]['request']['chat_id'] == '123'
    assert 'created_at' in records[0]

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&topics=hi,help',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['contexts']) == 2

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&topics=hi',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['contexts']) == 1

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&topics=hello',
    )
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['contexts']

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&topic=',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['contexts']) == 1

    start = int(
        datetime.datetime.fromisoformat(
            '2021-03-02T00:00:00+03:00',
        ).timestamp(),
    )
    end = int(
        datetime.datetime.fromisoformat(
            '2021-03-16T00:00:00+03:00',
        ).timestamp(),
    )

    response = await web_app_client.get(
        f'/v1/contexts?project_id=demo_dialog'
        f'&topic=help&start={start}&end={end}',
    )
    assert response.status == 200
    assert len((await response.json())['contexts']) == 1

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&limit=1&offset=1',
    )
    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['contexts']) == 1

    records = response_json['contexts'][0]['records']
    assert len(records) == 1

    assert records[0]['request']['chat_id'] == '1234'

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&mark=critical',
    )
    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['contexts']) == 1

    context = response_json['contexts'][0]

    assert context['chat_id'] == '123'
    assert context['chat_mark'] == 'critical'

    assert len(context['records']) == 2
    assert context['records'][1]['mark'] == 'critical'
    assert context['records'][1]['mark_comment']

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&replied=true',
    )
    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['contexts']) == 2

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&replied=false',
    )
    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['contexts']) == 1

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&topic=help&simulated=false&replied=true',  # noqa: E501
    )
    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['contexts']) == 1

    older_than = (
        datetime.datetime.fromisoformat(
            '2021-03-15T18:06:48.891541',
        ).timestamp()
        * 1000
    )

    response = await web_app_client.get(
        f'/v1/contexts?project_id=demo_dialog&'
        f'limit=1&older_than={int(older_than)}',
    )
    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['contexts']) == 1

    records = response_json['contexts'][0]['records']
    assert len(records) == 2

    assert records[0]['request']['chat_id'] == '123'

    response = await web_app_client.get(
        '/v1/contexts/?project_id=demo_dialog&mark=no_mark',
    )

    assert response.status == 200

    response_json = await response.json()

    contexts = response_json['contexts']

    assert len(contexts) == 1
    assert 'chat_mark' not in contexts[0]
    assert contexts[0]['chat_id'] == '1234'

    response = await web_app_client.get(
        '/v1/contexts/?project_id=demo_dialog&chat_id=12345',
    )

    response_json = await response.json()

    contexts = response_json['contexts']

    assert len(contexts) == 1
    assert contexts[0]['chat_id'] == '12345'

    response = await web_app_client.get(
        '/v1/contexts/?project_id=demo_dialog&chat_id=123',
    )

    response_json = await response.json()

    contexts = response_json['contexts']

    assert len(contexts) == 3

    response = await web_app_client.get(
        '/v1/contexts/?project_id=demo_dialog&chat_id=%',
    )

    response_json = await response.json()

    contexts = response_json['contexts']

    assert len(contexts) == 0  # pylint: disable=len-as-condition

    response = await web_app_client.get(
        '/v1/contexts/?project_id=demo_dialog&sampling_slug=demo_sampling',
    )

    response_json = await response.json()

    contexts = response_json['contexts']

    assert len(contexts) == 1

    response = await web_app_client.get(
        '/v1/contexts/?project_id=demo_dialog&version=100_RELEASE',
    )

    response_json = await response.json()

    contexts = response_json['contexts']

    assert len(contexts) == 1
    records = response_json['contexts'][0]['records']
    assert len(records) == 2

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&iterations=1',
    )
    assert response.status == 200
    assert len((await response.json())['contexts']) == 1

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&iterations=2',
    )
    assert response.status == 200
    assert len((await response.json())['contexts']) == 2

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&iterations=1-2',
    )
    assert response.status == 200
    assert len((await response.json())['contexts']) == 3

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&iterations=1,2',
    )
    assert response.status == 200
    assert len((await response.json())['contexts']) == 3

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&iterations=2,5',
    )
    assert response.status == 200
    assert len((await response.json())['contexts']) == 2

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&iterations=1,5',
    )
    assert response.status == 200
    assert len((await response.json())['contexts']) == 1

    response = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&iterations=2-5',
    )
    assert response.status == 200
    assert len((await response.json())['contexts']) == 2


@pytest.mark.pgsql('supportai_context', files=['sample.sql'])
async def test_get_multiple_contexts(web_app_client):
    response = await web_app_client.post(
        '/v1/contexts/multiple?project_id=demo_dialog',
        json={'chat_ids': ['123', '1234']},
    )
    assert response.status == 200
    assert len((await response.json())['contexts']) == 2


async def test_search_contexts_by_mpt(web_app_client):

    record = {
        'request': {
            'dialog': {'messages': [{'text': 'hello', 'author': 'user'}]},
            'features': [],
        },
        'response': {
            'reply': {'text': 'hi', 'texts': ['hi']},
            'features': {
                'most_probable_topic': 'mpt',
                'probabilities': [
                    {'topic_name': 'mpt', 'probability': 0.87},
                    {'topic_name': 'not_mpt', 'probability': 0.1},
                ],
            },
        },
    }

    await web_app_client.post(
        '/v1/context/record?chat_id=1&project_id=demo_dialog', json=record,
    )

    record['response']['features']['probabilities'][0]['probability'] = 0.5

    await web_app_client.post(
        '/v1/context/record?chat_id=2&project_id=demo_dialog', json=record,
    )

    record['response']['features']['probabilities'].pop(0)

    await web_app_client.post(
        '/v1/context/record?chat_id=2&project_id=demo_dialog', json=record,
    )

    search_result = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&most_probable_topic=mpt',
    )
    assert search_result.status == 200
    search_result_json = await search_result.json()

    assert len(search_result_json['contexts']) == 2
    assert len(search_result_json['contexts'][0]['records']) == 2

    search_result = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&most_probable_topic=mpt'
        '&mpt_probability=0.87&mpt_probability_pos=above',
    )
    assert search_result.status == 200
    search_result_json = await search_result.json()

    assert len(search_result_json['contexts']) == 1

    search_result = await web_app_client.get(
        '/v1/contexts'
        '?project_id=demo_dialog'
        '&most_probable_topic=mpt'
        '&iterations=1',
    )
    assert search_result.status == 200
    search_result_json = await search_result.json()

    assert not search_result_json['contexts']

    search_result = await web_app_client.get(
        '/v1/contexts'
        '?project_id=demo_dialog'
        '&most_probable_topic=mpt'
        '&iterations=2',
    )
    assert search_result.status == 200
    search_result_json = await search_result.json()

    assert not search_result_json['contexts']


@pytest.mark.pgsql('supportai_context', files=['sample.sql'])
async def test_markup(web_app_client):
    async def update_mark(context_id, mark):
        req = {'context_id': context_id}

        if mark:
            req['mark'] = mark

        response = await web_app_client.post(
            '/v1/context/record/mark?chat_id=123&project_id=demo_dialog',
            json=req,
        )

        assert response.status == 200

    async def check_mark(record_index, mark, chat_mark):
        context = await web_app_client.get(
            '/v1/context?chat_id=123&project_id=demo_dialog',
        )

        assert context.status == 200
        context_json = await context.json()

        record = context_json['records'][record_index]

        if mark:
            assert record['mark'] == mark
        else:
            assert 'mark' not in record

        assert context_json['chat_mark'] == chat_mark

    await update_mark('1', 'not_ok')
    await check_mark(0, 'not_ok', 'critical')

    await update_mark('2', 'not_ok')
    await check_mark(1, 'not_ok', 'not_ok')

    await update_mark('1', None)
    await check_mark(0, None, 'not_ok')


async def test_simulated(web_app_client):
    response = await web_app_client.post(
        '/v1/context/record?chat_id=1&project_id=demo_dialog&simulated=true',
        json={
            'request': {
                'dialog': {'messages': [{'text': 'hello', 'author': 'user'}]},
                'features': [],
            },
            'response': {'reply': {'text': 'hi', 'texts': ['hi']}},
        },
    )

    assert response.status == 200

    search_result = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&simulated=true',
    )
    assert search_result.status == 200
    search_result_json = await search_result.json()

    assert len(search_result_json['contexts']) == 1

    search_result = await web_app_client.get(
        '/v1/contexts?project_id=demo_dialog&simulated=false',
    )
    assert search_result.status == 200
    search_result_json = await search_result.json()

    assert not search_result_json['contexts']


@pytest.mark.pgsql('supportai_context', files=['sample.sql'])
async def test_clone(web_app_client):
    response = await web_app_client.post(
        '/v1/context/clone?chat_id=123&project_id=demo_dialog',
        json={'new_chat_id': 'auto_generated', 'simulated': True},
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['chat_id'] == 'auto_generated'
    assert response_json['simulated']

    assert len(response_json['records']) == 2

    search_result = await web_app_client.get(
        '/v1/context?project_id=demo_dialog&chat_id=auto_generated',
    )
    assert search_result.status == 200

    response = await web_app_client.post(
        '/v1/context/clone?chat_id=123&project_id=demo_dialog',
        json={'new_chat_id': 'auto_generated', 'simulated': True},
    )

    assert response.status == 400

    response = await web_app_client.post(
        '/v1/context/clone?chat_id=123&project_id=demo_dialog',
        json={
            'new_chat_id': 'auto_generated2',
            'simulated': True,
            'max_record_id': '1',
        },
    )

    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['records']) == 1

    response = await web_app_client.post(
        '/v1/context/clone?chat_id=123&project_id=demo_dialog',
        json={
            'new_chat_id': 'auto_generated3',
            'simulated': True,
            'clone_count': 1,
        },
    )

    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['records']) == 1


@pytest.mark.pgsql('supportai_context', files=['sample.sql'])
async def test_delete_contexts(web_app_client):
    response = await web_app_client.delete(
        '/v1/contexts?project_id=demo_dialog',
    )

    assert response.status == 200

    response = await web_app_client.get('/v1/contexts?project_id=demo_dialog')
    assert response.status == 200
    assert len((await response.json())['contexts']) == 1


async def test_post_contexts_bulk(web_app_client):

    contexts = [
        {
            'chat_id': 'id1',
            'created_at': datetime.datetime.now().isoformat(),
            'simulated': False,
            'records': [
                {
                    'created_at': datetime.datetime.now().isoformat(),
                    'request': {
                        'dialog': {
                            'messages': [{'text': 'hello', 'author': 'user'}],
                        },
                        'features': [],
                    },
                    'response': {'reply': {'text': 'hi', 'texts': ['hi']}},
                },
                {
                    'request': {
                        'dialog': {
                            'messages': [{'text': 'help', 'author': 'user'}],
                        },
                        'features': [],
                    },
                    'response': {'reply': {'text': 'ok', 'texts': ['ok']}},
                },
            ],
        },
        {
            'chat_id': 'id2',
            'created_at': datetime.datetime.now().isoformat(),
            'simulated': False,
            'records': [
                {
                    'request': {
                        'dialog': {
                            'messages': [{'text': 'hello', 'author': 'user'}],
                        },
                        'features': [],
                    },
                    'response': {'reply': {'text': 'hi', 'texts': ['hi']}},
                },
            ],
        },
    ]

    response = await web_app_client.post(
        '/v1/contexts/bulk?project_id=demo_dialog',
        json={'contexts': contexts},
    )

    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['contexts']) == 2

    context = response_json['contexts'][0]

    assert (
        datetime.datetime.fromisoformat(context['created_at'])
        == datetime.datetime.fromisoformat(
            contexts[0]['created_at'],
        ).astimezone()
    )

    assert (
        datetime.datetime.fromisoformat(context['records'][0]['created_at'])
        == datetime.datetime.fromisoformat(
            contexts[0]['records'][0]['created_at'],
        ).astimezone()
    )

    assert len(context['records']) == 2


@pytest.mark.pgsql('supportai_context', files=['sample.sql'])
async def test_get_context_last(web_app_client):
    response = await web_app_client.get(
        '/v1/context/last?project_id=demo_dialog&chat_user=user_1',
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json['chat_id'] == '1234'

    post_response = await web_app_client.post(
        '/v1/context/record?'
        'chat_id=43&project_id=demo_dialog&chat_user=user_1',
        json={
            'request': {
                'dialog': {'messages': [{'text': 'hello', 'author': 'user'}]},
                'features': [],
            },
            'response': {
                'reply': {'text': 'hi', 'texts': ['hi']},
                'features': {
                    'most_probable_topic': 'topic1',
                    'sure_topic': 'topic1',
                    'probabilities': [
                        {'topic_name': 'topic1', 'probability': 0.87},
                    ],
                },
            },
        },
    )
    assert post_response.status == 200

    response = await web_app_client.get(
        '/v1/context/last?project_id=demo_dialog&chat_user=user_1',
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json['chat_id'] == '43'

    response = await web_app_client.get(
        '/v1/context/last?project_id=demo_dialog&chat_user=user_2',
    )
    assert response.status == 204


@pytest.mark.pgsql('supportai_context', files=['sample.sql'])
async def test_post_context_last(web_app_client):
    response = await web_app_client.get(
        '/v1/context?chat_id=123&project_id=demo_dialog',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['records'][-1]['is_hidden']

    response = await web_app_client.post(
        '/v1/context/last?project_id=demo_dialog&chat_id=123',
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/context?chat_id=123&project_id=demo_dialog',
    )
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['records'][-1]['is_hidden']
