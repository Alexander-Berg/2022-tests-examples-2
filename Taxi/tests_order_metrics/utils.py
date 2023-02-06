import json


async def send_lb_message(
        taxi_order_metrics,
        testpoint,
        #
        consumer,
        topic,
        message,
        *,
        need_commit=True,
):
    test_cookie = 'test_cookie'

    @testpoint('logbroker_commit')
    def _commit(cookie):
        assert cookie == test_cookie

    response = await taxi_order_metrics.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': consumer,
                'data': json.dumps(message),
                'topic': topic,
                'cookie': test_cookie,
            },
        ),
    )
    assert response.status_code == 200
    if need_commit:
        await _commit.wait_call()
    else:
        assert not _commit.has_calls
