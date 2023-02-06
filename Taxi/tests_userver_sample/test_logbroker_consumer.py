import json


async def test_message(taxi_userver_sample, testpoint):
    @testpoint('logbroker_commit')
    def commit(data):
        assert data == 'cookie1'

    response = await taxi_userver_sample.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'positions',
                'data': 'contents',
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()
