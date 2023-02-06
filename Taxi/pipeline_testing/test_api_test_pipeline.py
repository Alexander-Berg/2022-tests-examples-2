import pytest


@pytest.mark.now('2019-01-01T20:00:00+03:00')
async def test_test_pipeline(web_app_client, mockserver, load_json):
    actual_requests = []

    @mockserver.json_handler('/surge-calculator/v1/js/pipeline/test')
    def _test_taxi_pipeline(request):
        actual_requests.append(request.json)
        return load_json('pipeline_test_response.json')

    response = await web_app_client.post(
        '/v2/pipeline/test/',
        json={'pipeline_id': '5de7baf5eb70bf332afa25f0'},
        params={'consumer': 'taxi-surge'},
    )
    assert response.status == 200
    assert actual_requests == [
        load_json('expected_pipeline_testing_request.json'),
    ]
    assert await response.json() == load_json('expected_response.json')
