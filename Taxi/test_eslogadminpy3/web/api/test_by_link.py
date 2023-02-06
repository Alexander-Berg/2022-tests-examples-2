# pylint: disable=unused-variable
import copy

import pytest

from test_eslogadminpy3 import constants


@pytest.mark.parametrize(
    'es_response, logs, host, span_id, log_extra_link',
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
            'crons-sas-01.taxi.dev.yandex.net',
            'f4b555796dac4d2cbc10914c8f8a0ff8',
            '291c7a1c2d2447c9a47a943999e7d2d1',
        ),
        (
            constants.ES_RESPONSE_EXAMPLE_WITHOUT_LOGS,
            [],
            'crons-sas-01.taxi.dev.yandex.net',
            'f4b555796dac4d2cbc10914c8f8a0ff8',
            '291c7a1c2d2447c9a47a943999e7d2d1',
        ),
        (
            'es_response_stq_task_no_logs.json',
            [],
            'taxi-stq-myt-01.taxi.tst.yandex.net',
            'b8f8277238cb4898a32eb53ec287bb7c',
            'dfcf22649db64e08be7a37ec4b67647e',
        ),
        (
            'es_response_restored_logs_for_persuggest.json',
            [
                {
                    'time': '2020-03-18T04:18:34.038344+03:00',
                    'message': 'GetData execution',
                    'level': 'info',
                },
            ],
            None,
            '36a324d23173a287',
            '9956f51143584b68ba9a1bf6cff03817',
        ),
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
async def test_by_link(
        patch,
        load_json,
        web_app_client,
        es_response,
        logs,
        host,
        span_id,
        log_extra_link,
        indices,
        expected_index,
):
    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def search(index, body, *args, **kwargs):
        assert index == expected_index
        if isinstance(es_response, str):
            return load_json(es_response)
        return copy.deepcopy(es_response)

    params = {'link_id': log_extra_link}
    if indices is not None:
        params['indices'] = ','.join(indices)
    response = await web_app_client.get('/v1/logs/by_link/', params=params)
    assert response.status == 200
    content = await response.json()
    assert content.get('host') == host
    assert content['span_id'] == span_id
    assert content['log_extra_link'] == log_extra_link
    assert content['logs'] == logs


async def test_by_link_empty_response(web_app_client, patch):
    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def search(index, body, *args, **kwargs):
        return copy.deepcopy(constants.ES_RESPONSE_EXAMPLE_EMPTY)

    response = await web_app_client.get(
        '/v1/logs/by_link/',
        params={'link_id': '291c7a1c2d2447c9a47a943999e7d2d1'},
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
        'log_extra_link': '291c7a1c2d2447c9a47a943999e7d2d1',
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
async def test_by_link_with_level(
        web_app_client, patch, log_level, expected_logs,
):
    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def search(index, body, *args, **kwargs):
        return copy.deepcopy(constants.ES_RESPONSE_EXAMPLE_WITH_LOGS)

    response = await web_app_client.get(
        f'/v1/logs/by_link/', params={'link_id': 'some', 'level': log_level},
    )
    assert response.status == 200
    content = await response.json()
    assert content['logs'] == expected_logs
