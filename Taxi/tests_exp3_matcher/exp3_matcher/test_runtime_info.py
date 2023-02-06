import pytest


@pytest.mark.config(
    EXPERIMENTS3_SERVICE_CONSUMER_RELOAD=[
        'consumer_only_for_test_runtime_info',
    ],
)
@pytest.mark.experiments3(
    name='test_runtime_info',
    consumers=['consumer_only_for_test_runtime_info'],
    clauses=[],
    default_value={'key': 228},
)
async def test_runtime_info(taxi_exp3_matcher, mockserver, testpoint):
    @mockserver.json_handler(
        '/taxi-exp-uservices/v1/consumers/kwargs/',
    )  # runtime info handler
    def _mock_runtime_info(request):
        assert (
            request.json['consumer'] == 'consumer_only_for_test_runtime_info'
        )
        assert request.json['kwargs'] == []
        assert set(request.json['metadata']['supported_features']) == {
            'match-statistics',
            'merge-by-tag',
            'trait-tags',
            'segmentation-predicate',
            # 'matching-logs',
        }
        return {}

    @testpoint('exp3::runtime_info_sent')
    def runtime_info_sent(data):
        pass

    request = {
        'consumer': 'consumer_only_for_test_runtime_info',
        'args': [
            {'name': 'some_kwarg', 'type': 'string', 'value': 'some_value'},
        ],
    }
    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200

    await runtime_info_sent.wait_call()
    assert _mock_runtime_info.times_called == 1
