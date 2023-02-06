import datetime
import random

import pytest


@pytest.mark.pgsql('supportai_context', files=['sample.sql'])
async def test_get_samplings(web_app_client):
    response = await web_app_client.get(
        '/v1/samplings/?project_id=demo_dialog',
    )

    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['samplings']) == 1


@pytest.mark.pgsql('supportai_context', files=['sample.sql'])
async def test_post_samplings(web_app_client):
    response = await web_app_client.post(
        '/v1/samplings/?project_id=demo_dialog',
        json={'quantity': 3, 'filters': {}, 'name': 'test'},
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['quantity'] == 3
    assert response_json['percent'] == pytest.approx(100 / 3)
    assert response_json['marked_percent'] == 75.0

    response = await web_app_client.post(
        '/v1/samplings/?project_id=demo_dialog',
        json={'quantity': 6, 'filters': {}, 'name': 'test'},
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['quantity'] == 3
    assert response_json['percent'] == pytest.approx(100 / 3)
    assert response_json['marked_percent'] == 75.0

    response = await web_app_client.post(
        '/v1/samplings/?project_id=demo_dialog',
        json={'quantity': 1, 'filters': {}, 'name': 'test'},
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['quantity'] == 1

    response = await web_app_client.post(
        '/v1/samplings/?project_id=demo_dialog',
        json={
            'quantity': 1,
            'filters': {'start': 1615791600, 'end': 1615791600},
            'name': 'test',
        },
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['quantity'] == 0

    response = await web_app_client.post(
        '/v1/samplings/?project_id=demo_dialog',
        json={'quantity': 2, 'filters': {'topic': 'help'}, 'name': 'test'},
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['quantity'] == 2

    response = await web_app_client.post(
        '/v1/samplings/?project_id=demo_dialog',
        json={
            'quantity': 10,
            'filters': {'topics': ['help', 'hi']},
            'name': 'test',
        },
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['quantity'] == 2

    response = await web_app_client.post(
        '/v1/samplings/?project_id=demo_dialog',
        json={'quantity': 10, 'filters': {'topics': ['hi']}, 'name': 'test'},
    )

    assert response.status == 200

    response_json = await response.json()

    assert response_json['quantity'] == 1


@pytest.fixture(scope='module', name='seed_contexts_data')
def seed_contexts_data_():
    def gen_records(_len: int):
        return [
            {
                'request': {
                    'dialog': {
                        'messages': [{'text': 'hello', 'author': 'user'}],
                    },
                    'features': [],
                },
                'response': {
                    'reply': {'text': 'hi'},
                    'features': {
                        'most_probable_topic': 'mpt',
                        'probabilities': [
                            {'topic_name': 'mpt', 'probability': 0.87},
                            {'topic_name': 'not_mpt', 'probability': 0.1},
                        ],
                    },
                },
            }
            for _ in range(_len)
        ]

    def gen_contexts(context_len: int, record_len: int):
        return {
            'contexts': [
                {
                    'chat_id': f'1234{i}',
                    'created_at': datetime.datetime.now().isoformat(),
                    'simulated': False,
                    'records': gen_records(record_len),
                }
                for i in range(context_len)
            ],
        }

    return gen_contexts


@pytest.fixture(scope='module', name='seed_samplings_data')
def seed_samplings_data_():
    return {'quantity': 150, 'filters': {}, 'name': 'test'}


async def test_sampling_recount_on_mark(
        web_app_client, seed_contexts_data, seed_samplings_data,
):
    async def seed_contexts():
        await web_app_client.post(
            '/v1/contexts/bulk?project_id=demo_dialog',
            json=seed_contexts_data(10, 30),
        )

    async def seed_samplings():
        response = await web_app_client.post(
            '/v1/samplings/?project_id=demo_dialog', json=seed_samplings_data,
        )

        assert response.status == 200

    async def update_mark(chat_id, context_id, mark):
        req = {'context_id': context_id}

        if mark:
            req['mark'] = mark

        response = await web_app_client.post(
            f'/v1/context/record/mark?'
            f'chat_id={chat_id}&project_id=demo_dialog',
            json=req,
        )

        assert response.status == 200

    await seed_contexts()

    await seed_samplings()

    response = await web_app_client.get(
        '/v1/samplings/?project_id=demo_dialog',
    )

    assert response.status == 200
    response_json = await response.json()

    sampling = response_json['samplings'][0]
    sampling_slug = sampling['slug']

    response = await web_app_client.get(
        f'/v1/contexts?project_id=demo_dialog&sampling_slug={sampling_slug}',
    )

    assert response.status == 200
    response_json = await response.json()

    to_change_mark_list = [
        (context['chat_id'], record['id'])
        for context in response_json['contexts']
        for record in context['records']
    ]

    for to_change_mark in random.sample(
            to_change_mark_list, int(40 * len(to_change_mark_list) / 100),
    ):
        await update_mark(*to_change_mark, 'ok')

    response = await web_app_client.get(
        '/v1/samplings/?project_id=demo_dialog',
    )

    assert response.status == 200
    response_json = await response.json()

    sampling = response_json['samplings'][0]

    assert pytest.approx(40.0, sampling['percent'])
