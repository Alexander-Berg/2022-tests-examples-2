from aiohttp import web
import pytest


@pytest.fixture(name='context_samplings')
def gen_context_sampling():
    return {
        'samplings': [
            {
                'slug': 'test_slug_0',
                'name': '',
                'project_id': 'demo_dialog',
                'quantity': 25,
                'percent': 36.6,
                'marked_percent': 20,
                'marked': False,
            },
            {
                'slug': 'test_slug_1',
                'name': '',
                'project_id': 'demo_dialog',
                'quantity': 25,
                'percent': 36.6,
                'marked_percent': 100,
                'marked': True,
            },
        ],
    }


@pytest.fixture(name='context_sampling_post')
def gen_context_sampling_post():
    return {
        'slug': 'test_slug_2',
        'name': '',
        'project_id': 'demo_dialog',
        'quantity': 25,
        'percent': 36.6,
        'marked_percent': 30,
        'marked': False,
    }


@pytest.mark.pgsql('supportai_tasks', files=['samplings.sql'])
async def test_get_samplings(web_app_client, mockserver, context_samplings):
    @mockserver.json_handler('/supportai-context/v1/samplings')
    # pylint: disable=unused-variable
    async def context_handler(request):
        return web.json_response(data=context_samplings)

    samplings_response = await web_app_client.get(
        '/v1/samplings?project_slug=demo_dialog&user_id=007',
    )

    assert samplings_response.status == 200

    samplings = (await samplings_response.json())['samplings']

    assert len(samplings) == 2

    for i, sampling in enumerate(samplings):
        assert sampling['slug'] == context_samplings['samplings'][i]['slug']
        assert 'name' in sampling


@pytest.mark.pgsql('supportai_tasks', files=['samplings.sql'])
async def test_post_sampling(
        web_app_client, mockserver, context_sampling_post,
):
    @mockserver.json_handler('/supportai-context/v1/samplings')
    # pylint: disable=unused-variable
    async def context_handler(request):
        return web.json_response(data=context_sampling_post)

    sampling_response = await web_app_client.post(
        '/v1/samplings?project_slug=demo_dialog&user_id=007',
        json={'name': 'Some', 'quantity': 25, 'filters': {}},
    )

    sampling = await sampling_response.json()

    assert sampling['slug'] == context_sampling_post['slug']
