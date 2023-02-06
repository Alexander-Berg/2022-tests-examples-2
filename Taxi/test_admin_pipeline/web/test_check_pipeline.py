import datetime

import pytest


@pytest.mark.now('2019-12-16T23:00:00+03:00')
@pytest.mark.parametrize('pass_tests', [True, False])
async def test_update(
        web_app_client, mockserver, load_json, mongodb, pass_tests,
):
    consumer = 'taxi-surge'
    test_requests = []

    @mockserver.json_handler('/surge-calculator/v1/js/pipeline/compile')
    def _taxi_compile_pipeline(_request):
        return {'metadata': dict()}

    @mockserver.json_handler('/surge-calculator/v1/js/pipeline/test')
    def _taxi_test_pipeline(request):
        test_requests.append(request.json)
        return {
            'tests_results': {
                'created': '2019-12-16T20:38:50+00:00',
                'tests': [
                    {
                        'name': 'the_test',
                        'testcases': [
                            {'passed': True, 'name': 'always_pass'},
                            {'passed': pass_tests, 'name': 'flapping'},
                        ],
                    },
                ],
            },
        }

    pipeline = {
        'id': 'test_id',
        'name': 'default',
        'state': 'draft',
        'comment': 'test_comment',
        'stages': [],
    }

    response = await web_app_client.post(
        '/v2/pipeline/',
        json=pipeline,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == 200

    tzinfo = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    now = datetime.datetime.now().astimezone(tzinfo).isoformat()
    pipeline['state'] = 'valid'
    pipeline['updated'] = now
    response = await web_app_client.put(
        '/v2/pipeline/',
        json=pipeline,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'testsuite'},
    )
    if pass_tests:
        assert response.status == 200
    else:
        assert response.status == 400
        data = await response.text()
        assert data == '400: Some tests failed!'

    assert test_requests == [load_json('expected_test_request.json')]


@pytest.mark.now('2019-12-16T23:00:00+03:00')
@pytest.mark.parametrize('pass_tests', [True, False])
async def test_check_pipeline(web_app_client, mockserver, pass_tests):
    @mockserver.json_handler('/surge-calculator/v1/js/pipeline/compile')
    def _taxi_compile_pipeline(_request):
        return {'metadata': dict()}

    @mockserver.json_handler('/surge-calculator/v1/js/pipeline/test')
    def _taxi_test_pipeline(_request):
        return {
            'tests_results': {
                'created': '2019-12-16T20:38:50+00:00',
                'tests': [
                    {
                        'name': 'the_test',
                        'testcases': [
                            {'passed': True, 'name': 'always_pass'},
                            {'passed': pass_tests, 'name': 'flapping'},
                        ],
                    },
                ],
            },
        }

    pipeline = {
        'id': 'test-id',
        'name': 'default',
        'state': 'active',
        'consumer': 'taxi-surge',
        'comment': 'test_comment',
        'stages': [],
    }
    response = await web_app_client.post(
        'v2/pipeline/check',
        json=pipeline,
        headers={'X-Yandex-Login': 'testsuite'},
    )
    assert response.status == (200 if pass_tests else 422)
