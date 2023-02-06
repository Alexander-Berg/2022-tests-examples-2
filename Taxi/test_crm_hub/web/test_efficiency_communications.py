import asyncio

import pytest


@pytest.mark.parametrize(
    'sending_id, exists, state, result',
    [
        ('00000000000000000000000000000001', True, 'new', 200),
        ('00000000000000000000000000000002', False, None, 400),
        ('00000000000000000000000000000003', True, 'new', 200),
        ('00000000000000000000000000000011', True, 'error', 200),
        ('00000000000000000000000000000012', True, 'finished', 200),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['init_efficiency_sending.sql'])
async def test_efficiency_communication(
        web_app_client, sending_id, exists, state, result, patch,
):
    @patch('crm_hub.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def _exists(*agrs, **kwargs):
        return exists

    response = await web_app_client.post(
        '/v1/communication/efficiency/new',
        json={'id': sending_id, 'table_path': 'table_path'},
    )
    assert response.status == result
    if result == 200:
        data = await response.json()
        assert data['state'] == state


async def test_efficiency_communication_retry(
        web_context, web_app_client, patch, mockserver,
):
    count = 10
    sending_id = '00000000000000000000000000000001'

    @patch('crm_hub.generated.web.yt_wrapper.plugin.AsyncYTClient.exists')
    async def _exists(*agrs, **kwargs):
        return True

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _queue(request, queue_name):
        pass

    tasks = []
    for _ in range(count):
        tasks.append(
            web_app_client.post(
                '/v1/communication/efficiency/new',
                json={'id': sending_id, 'table_path': 'table_path'},
            ),
        )
    await asyncio.gather(*tasks)

    assert len(_exists.calls) == count
    assert _queue.times_called == 1


@pytest.mark.parametrize(
    'sending_list, state, result',
    [
        (['00000000000000000000000000000001'], 'finished', 200),
        (['00000000000000000000000000000002'], 'finished', 200),
        (['00000000000000000000000000000003'], 'processing', 200),
        (['00000000000000000000000000000004'], 'error', 200),
        (
            [
                '00000000000000000000000000000001',
                '00000000000000000000000000000002',
            ],
            None,
            404,
        ),
        (['00000000000000000000000000000100'], None, 404),
    ],
)
@pytest.mark.pgsql(
    'crm_hub', files=['multi_sending.sql', 'init_efficiency_sending.sql'],
)
async def test_efficiency_communication_status(
        web_app_client, sending_list, state, result,
):
    response = await web_app_client.get(
        '/v1/communication/efficiency/items',
        params={'id': ','.join(sending_list)},
    )
    assert response.status == result
    if result == 200:
        data = await response.json()
        assert data['state'] == state
