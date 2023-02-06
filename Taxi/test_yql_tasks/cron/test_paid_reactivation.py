import pytest

from yql_tasks.generated.cron import run_cron


async def test_paid_reactivation_disabled(patch):
    @patch('yql_tasks.internal.paid_reactivation.run')
    async def handler(*args, **kwargs):
        pass

    await run_cron.main(['yql_tasks.crontasks.paid_reactivation', '-t', '0'])
    assert handler.calls == []


@pytest.mark.now('2021-01-01T00:00:00+0000')
@pytest.mark.config(
    YQL_TASKS_PAID_REACTIVATION_CRON_ENABLE=True,
    YQL_TASKS_PAID_REACTIVATION_TABLE='home/tests/drivers',
)
async def test_paid_reactivation(
        mock_yt_call, mock_update_hiring_details, load_json,
):
    expected = load_json('expected_data.json')

    yt_responses = load_json('yt_responses.json')
    yt_handler = mock_yt_call(yt_responses)

    await run_cron.main(['yql_tasks.crontasks.paid_reactivation', '-t', '0'])

    yt_call = yt_handler.calls[0]
    assert list(yt_call['args'][1:]) == expected['yt_call_args']
    assert yt_call['kwargs'] == expected['yt_call_kwargs']

    assert mock_update_hiring_details.times_called == 3

    expected_dp_requests = expected['driver_profiles_request']

    mock_calls = []
    for _ in range(3):
        mock_call = mock_update_hiring_details.next_call()
        mock_calls.append(
            {
                'query': dict(mock_call['request'].query),
                'data': mock_call['request'].json,
            },
        )

    mock_calls = sorted(mock_calls, key=lambda x: x['query']['park_id'])
    assert mock_calls == expected_dp_requests
