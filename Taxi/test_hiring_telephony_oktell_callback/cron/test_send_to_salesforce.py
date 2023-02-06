import pytest

QUERY = """SELECT "task_id", "is_sent_to_sf"
FROM "hiring_telephony_oktell_callback"."tasks"
ORDER BY "task_id"
"""


@pytest.mark.parametrize('chunk_size', [1, 2, 30])
@pytest.mark.usefixtures('mock_hiring_sf_events')
@pytest.mark.now('2020-01-01 00:00:00')
@pytest.mark.parametrize(
    'test_name', ['test_200', 'test_400', 'test_200_400', 'test_500'],
)
async def test_send_to_salesforce_(
        load_json,
        cron_context,
        cron_runner,
        taxi_config,
        send_event,
        test_name,
        chunk_size,
):
    taxi_config.set_values(
        {'HIRING_TELEPHONY_CHUNK_SIZE_SEND_TO_SF': chunk_size},
    )
    sf_events_response = load_json('sf_events_response.json')[test_name]
    send_event_handler = send_event(
        sf_events_response['code'], sf_events_response['response'],
    )
    expected_tasks = load_json('expected_result.json')
    expected_responses = expected_tasks[sf_events_response['expected']][
        'tasks'
    ]
    expected_request_to_sf_events = expected_tasks['tasks']

    await cron_runner.send_to_salesforce()

    assert send_event_handler.times_called == 2

    for req in [
            send_event_handler.next_call()['request'].json
            for _ in range(send_event_handler.times_called)
    ]:
        assert req == expected_request_to_sf_events[req['task_id']]

    async with cron_context.pg.fast_pool.acquire() as conn:
        tasks = await conn.fetch(QUERY)
        assert [dict(task) for task in tasks] == expected_responses


@pytest.mark.config(HIRING_TELEPHONY_SEND_CALLRESULTS=False)
async def test_disabled(cron_context, cron_runner, taxi_config):
    taxi_config.set_values({'HIRING_TELEPHONY_CHUNK_SIZE_SEND_TO_SF': 1})
    with pytest.raises(RuntimeError):
        await cron_runner.send_to_salesforce()
