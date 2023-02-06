# pylint: disable=unused-variable
import copy

import pytest

from test_eslogadminpy3 import constants


@pytest.mark.parametrize(
    'es_response,logs',
    [
        (
            constants.ES_RESPONSE_EXAMPLE_WITH_LOGS,
            [
                {
                    'time': '2019-06-04T14:25:13.964000+03:00',
                    'message': '(useragent=python-requests/2.10.0) all ok',
                    'level': 'info',
                },
                {
                    'time': '2019-06-04T14:25:13.964000+03:00',
                    'message': '(useragent=python-requests/2.10.0) all ok',
                    'level': 'trace',
                },
            ],
        ),
        (constants.ES_RESPONSE_EXAMPLE_WITHOUT_LOGS, []),
    ],
)
@pytest.mark.parametrize(
    'indices, expected_index',
    [
        (None, 'yandex-taxi-*,pilorama-core-*,yandex-taxi-archive'),
        (['yandex-taxi-api'], 'yandex-taxi-api*,yandex-taxi-archive'),
        (
            ['yandex-taxi-api', 'yandex-taxi-rtc'],
            'yandex-taxi-api*,yandex-taxi-rtc*,yandex-taxi-archive',
        ),
    ],
)
async def test_by_span(
        web_app_client, patch, es_response, logs, indices, expected_index,
):
    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def search(index, body, *args, **kwargs):
        assert index == expected_index
        return copy.deepcopy(es_response)

    params = {'span_id': 'f4b555796dac4d2cbc10914c8f8a0ff8'}
    if indices is not None:
        params['indices'] = ','.join(indices)
    response = await web_app_client.get('/v1/logs/by_span/', params=params)
    assert response.status == 200
    content = await response.json()
    assert content['host'] == 'crons-sas-01.taxi.dev.yandex.net'
    assert content['span_id'] == 'f4b555796dac4d2cbc10914c8f8a0ff8'
    assert content['log_extra_link'] == '291c7a1c2d2447c9a47a943999e7d2d1'
    assert content['logs'] == logs


async def test_by_span_empty_response(web_app_client, patch):
    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def search(index, body, *args, **kwargs):
        return copy.deepcopy(constants.ES_RESPONSE_EXAMPLE_EMPTY)

    response = await web_app_client.get(
        '/v1/logs/by_span/',
        params={'span_id': 'f4b555796dac4d2cbc10914c8f8a0ff8'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'lang': 'json',
        'logs': [],
        'request_body': (
            'Тело запроса не найдено, ' 'возможно, логирование отключено.'
        ),
        'response_body': (
            'Тело ответа не найдено, ' 'возможно, логирование отключено.'
        ),
        'span_id': 'f4b555796dac4d2cbc10914c8f8a0ff8',
    }


@pytest.mark.parametrize(
    'log_level,expected_logs',
    [
        ('ERROR', []),
        (
            'INFO',
            [
                {
                    'level': 'info',
                    'message': '(useragent=python-requests/2.10.0) all ok',
                    'time': '2019-06-04T14:25:13.964000+03:00',
                },
            ],
        ),
    ],
)
async def test_by_span_with_level(
        web_app_client, patch, log_level, expected_logs,
):
    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def search(index, body, *args, **kwargs):
        return copy.deepcopy(constants.ES_RESPONSE_EXAMPLE_WITH_LOGS)

    response = await web_app_client.get(
        f'/v1/logs/by_span/', params={'span_id': 'some', 'level': log_level},
    )
    assert response.status == 200
    content = await response.json()
    assert content['logs'] == expected_logs
