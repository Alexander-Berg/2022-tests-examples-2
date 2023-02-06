import pytest


@pytest.mark.now('2020-01-01T00:00:00')
async def test_push_salesforce_limits(
        load_json,
        cron_runner,
        mock_limits,
        mock_salesforce_auth,
        mock_solomon,
):
    sf_response = load_json('salesforce_response.json')
    solomon_request = load_json('expected_solomon_data.json')
    limits_mock = mock_limits(sf_response)
    solomon_mock = mock_solomon()

    await cron_runner.push_salesforce_limits()

    assert limits_mock.has_calls

    assert solomon_mock.has_calls
    assert solomon_mock.next_call()['request'].json == solomon_request
