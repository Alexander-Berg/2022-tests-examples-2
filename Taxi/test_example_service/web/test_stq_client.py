import datetime

import pytest

from taxi.clients import stq_agent


@pytest.mark.config(
    TVM_RULES=[{'src': 'some_project_web', 'dst': stq_agent.TVM_SERVICE_NAME}],
)
async def test_stq_agent(
        web_context, patch_aiohttp_session, response_mock, mockserver,
):
    @mockserver.json_handler('/stq-agent/queues/api/add/processing')
    def stq_agent_put_task(request):
        assert request.json == {
            'task_id': task_id,
            'eta': eta_str,
            'args': [],
            'kwargs': {},
        }
        return {}

    task_id = 'random_task_id'
    eta = 0
    eta_str = stq_agent._convert_eta(eta)  # pylint: disable=W0212
    await web_context.stq.processing.call_later(
        eta=eta, task_id=task_id, args=None,
    )

    assert stq_agent_put_task.times_called == 1


async def test_stq_client(web_context, stq):
    await web_context.stq.processing.call('some_task')
    assert stq.processing.next_call()['id'] == 'some_task'
    assert stq.is_empty


@pytest.mark.parametrize(
    'call_data, expected_call',
    [
        (
            {'task_id': 'my_task_id', 'double_param': 3.3},
            {
                'args': ['my_task_id', 3.3],
                'eta': datetime.datetime(1970, 1, 1, 0, 0),
                'id': 'my_task_id',
                'kwargs': {},
                'queue': 'example_queue_with_args',
            },
        ),
        (
            {
                'double_param': 3.3,
                'arg_with_default': False,
                'optional_arg': 8,
                'static': 'blabla',
                'vector_arg': ['a', 'b'],
                'task_id': 'my_task_id',
                'eta': datetime.datetime(2020, 1, 1),
            },
            {
                'args': ['my_task_id', 3.3],
                'eta': datetime.datetime(2020, 1, 1),
                'id': 'my_task_id',
                'kwargs': {
                    'arg_with_default': False,
                    'optional_arg': 8,
                    'static': 'blabla',
                    'vector_arg': ['a', 'b'],
                },
                'queue': 'example_queue_with_args',
            },
        ),
    ],
)
async def test_stq_agent_queue(stq, call_data, expected_call, web_context):
    if 'eta' in call_data:
        await web_context.stq.example_queue_with_args.call_later(**call_data)
    else:
        await web_context.stq.example_queue_with_args.call(**call_data)
    assert stq.example_queue_with_args.next_call() == expected_call


async def test_stq_agent_add_bulk(stq, web_app_client):
    response = await web_app_client.post(
        '/stq-agent-queues-add-bulk',
        json={
            'tasks': [
                {
                    'task_id': 'task_id1',
                    'double_param': 11.22,
                    'queue': 'example_queue_with_args',
                },
                {
                    'task_id': 'task_id2',
                    'double_param': 22.11,
                    'eta': stq_agent._convert_eta(0),  # pylint: disable=W0212
                    'queue': 'processing',
                },
                {
                    'task_id': 'task_id3',
                    'double_param': 11.22,
                    'queue': 'processing',
                },
                {
                    'task_id': 'task_id4',
                    'double_param': 22.11,
                    'eta': stq_agent._convert_eta(0),  # pylint: disable=W0212
                    'queue': 'example_queue_with_args',
                },
            ],
        },
    )
    assert response.status == 200
