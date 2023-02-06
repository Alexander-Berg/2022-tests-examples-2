import pytest

EXPECTED_YT_DATA_TABLE = 'expected_yt_data.json'
YT_STQ_TABLE = '//home/test/stq_table'


@pytest.mark.now('2022-09-15T10:00:00Z')
@pytest.mark.config(HIRING_FAILED_STQ_TABLE_PATH=YT_STQ_TABLE)
@pytest.mark.parametrize('case', ['200', '400', '409'])
async def test_infranaim_api(
        load_json,
        stq_runner,
        stq3_context,
        simple_secdist,
        mock_infranaim_api_create,
        yt_client,
        case,
):
    handler_infranaim_api = mock_infranaim_api_create(int(case))
    await stq_runner.hiring_send_to_infranaim_api.call(
        args=(),
        kwargs={
            'endpoint': 'to_infranaim_api',
            'ticket_data': load_json('ticket_data.json')[case],
        },
    )
    assert handler_infranaim_api.has_calls

    if case != '200':
        expected_yt_data = load_json(EXPECTED_YT_DATA_TABLE)
        rows = list(yt_client.read_table(YT_STQ_TABLE))
        assert rows[-1] == expected_yt_data
