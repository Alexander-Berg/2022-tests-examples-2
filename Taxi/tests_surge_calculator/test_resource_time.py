import pytest

YT_LOGS = []


@pytest.fixture(autouse=True)
def testpoint_service(testpoint):
    @testpoint('yt_logger::messages::calculations')
    def _handler(data_json):
        YT_LOGS.append(data_json)


@pytest.mark.config(
    SURGE_PIPELINE_EXECUTION={
        'UNIFIED_RESOURCES_LOGGING_MODE': 'instance',
        'ENABLE_UNIFIED_STAGE_OUT_LOGGING': True,
    },
)
@pytest.mark.now('2022-02-15T19:21:49+03:00')
async def test_time(taxi_surge_calculator):
    YT_LOGS.clear()
    request = {'point_a': [32.15101, 51.12101], 'classes': ['econom', 'vip']}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200, response.json()

    resource = YT_LOGS[0]['calculation']['$resources']['time']
    meta = YT_LOGS[0]['calculation']['$meta']
    expected_time_since_epoch_ms = 1644942109000

    assert resource == {
        '$instance': {
            'utc': {'time_since_epoch_ms': expected_time_since_epoch_ms},
            'zones': {
                'point_a': {'offset_ms': 7200000, 'name': 'Europe/Kiev'},
            },
        },
        '$resource_id': 'time',
    }
    assert meta == [
        {
            '$iteration': 0,
            '$logs': [
                {
                    '$level': 'info',
                    '$message': str(expected_time_since_epoch_ms),
                    '$region': 'user_code',
                    '$timestamp': '2022-02-15T16:21:49+0000',
                },
            ],
            '$stage': 'add_classes',
        },
    ]
