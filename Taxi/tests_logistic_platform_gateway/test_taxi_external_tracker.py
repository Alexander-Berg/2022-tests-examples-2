import pytest


@pytest.mark.config(
    LOGISTIC_PLATFORM_GATEWAY_TAXI_EXTERNAL_CORP_CLIENTS={
        'corp_client_id': {'cursor': 'cursor'},
    },
)
async def test_taxi_external_order_history(
        taxi_logistic_platform_gateway, stq_runner, mockserver, load_json,
):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/journal',
    )
    def events_journal(request):
        return mockserver.make_response(
            status=200,
            json={
                'cursor': request.json['cursor'] + '1',
                'events': load_json('journal.json'),
            },
            headers={'X-Polling-Delay-Ms': '1000'},
        )

    await stq_runner.logistic_platform_gateway_poll_journal_taxi_external_main_cluster.call(  # noqa E501
        task_id='corp_client_id',
    )

    assert events_journal.times_called == 1

    @mockserver.json_handler('/b2b-taxi/b2b/cargo/integration/v2/claims/info')
    def claim_info(_):
        return load_json('claim_info.json')

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v2/claims/confirmation_code',
    )
    def confirmation_code(_):
        return {'code': '559968', 'attempts': 5}

    response = await taxi_logistic_platform_gateway.post(
        '/internal/operator/taxi-external/order/history',
        params={'external_order_id': '58bcde6d313242808b65fc5690489b47'},
    )

    assert claim_info.times_called == 1
    assert confirmation_code.times_called == 1

    assert response.status_code == 200
    assert response.json()['order_events'] == load_json(
        'converted_events.json',
    )
