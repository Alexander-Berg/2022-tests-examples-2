import json
import typing

import aiohttp.web
import pytest


async def test_ping(taxi_example_service_web, patch, response_mock):
    @patch('example_service.api.ping_get.handle')
    def patch_ping(*args, **kwargs):
        return response_mock(status=400)

    response = await taxi_example_service_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
    assert not patch_ping.calls


@pytest.mark.config(TVM_ENABLED=True)
async def test_tests_control(taxi_example_service_web):
    response_body = await taxi_example_service_web.tests_control()
    assert response_body is not None


@pytest.mark.now('2000-01-01T03:00:00+03:00')
async def test_now_mark(taxi_example_service_web):
    response = await taxi_example_service_web.get('/what_time')
    assert response.status == 200
    content = await response.text()
    assert response.headers['Content-Type'] == 'text/plain; charset=utf-8'
    assert content == '2000-01-01T00:00:00+00:00'


@pytest.mark.parametrize(
    'locale,expected',
    [
        pytest.param('ru', 'Привет', id='ru'),
        pytest.param('en', 'Hello', id='en'),
        pytest.param('fr', 'Salut', id='fr'),
    ],
)
@pytest.mark.translations(
    order={'hello': {'ru': 'Привет', 'en': 'Hello', 'fr': 'Salut'}},
)
async def test_translations(taxi_example_service_web, locale, expected):
    response = await taxi_example_service_web.get(
        '/hello', headers={'Accept-Language': locale},
    )
    assert response.status == 200
    content = await response.text()
    assert content == expected


@pytest.mark.config(ENABLE_DRIVER_CHANGE_COST=True)
async def test_config_true(taxi_example_service_web):
    response = await taxi_example_service_web.get('/change_cost')
    assert response.status == 200


@pytest.mark.config(ENABLE_DRIVER_CHANGE_COST=False)
async def test_config_false(taxi_example_service_web):
    response = await taxi_example_service_web.get('/change_cost')
    assert response.status == 404


async def test_yas_client(taxi_example_service_web, mock_yet_another_service):
    @mock_yet_another_service('/talk')
    async def handler(request):
        return aiohttp.web.Response(text='It\'s some string')

    response = await taxi_example_service_web.get('/go_to_yas')
    assert response.status == 200
    data = await response.text()
    assert data == 'It\'s some string'
    assert handler.times_called == 1


@pytest.mark.parametrize(
    'test_url,expected_status,expected_content',
    [
        pytest.param(
            'http://www.external-url.com/path',
            400,
            'Request failed',
            id='external url',
        ),
        pytest.param(
            '$mockserver/mocked-service',
            200,
            'Request is successful',
            id='internal url',
        ),
    ],
)
async def test_use_requests(
        taxi_example_service_web,
        mockserver,
        test_url,
        expected_status,
        expected_content,
):
    @mockserver.json_handler('/mocked-service')
    def handler(request):
        return 'Request is successful'

    response = await taxi_example_service_web.get(
        '/use_requests', params={'url': test_url},
    )
    assert response.status == expected_status
    content = await response.text()
    assert content == expected_content
    assert handler.times_called == int(expected_status == 200)


@pytest.mark.parametrize(
    'test_url,expected_status,expected_content',
    [
        pytest.param(
            'http://www.external-url.com/path',
            400,
            'Request failed',
            id='external url',
        ),
        pytest.param(
            '$mockserver/mocked-service',
            200,
            'Request is successful',
            id='internal url',
        ),
    ],
)
async def test_use_aiohttp(
        taxi_example_service_web,
        mockserver,
        test_url,
        expected_status,
        expected_content,
):
    @mockserver.json_handler('/mocked-service')
    def handler(request):
        return 'Request is successful'

    response = await taxi_example_service_web.get(
        '/use_aiohttp', params={'url': test_url},
    )
    assert response.status == expected_status
    content = await response.text()
    assert content == expected_content
    assert handler.times_called == int(expected_status == 200)


class LookupRowsParams(typing.NamedTuple):
    request_data: list
    expected_content_path: str


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            LookupRowsParams(
                request_data=[{'hash': 12345}],
                expected_content_path='response_lookup_rows_expected_1.json',
            ),
            id='simple case',
            marks=pytest.mark.yt(
                dyn_table_data=['yt_response_lookup_rows_1.yaml'],
            ),
        ),
        pytest.param(
            LookupRowsParams(
                request_data=[{'hash': 67890}],
                expected_content_path='response_lookup_rows_expected_2.json',
            ),
            id='simple case 2',
            marks=pytest.mark.yt(
                dyn_table_data=['yt_response_lookup_rows_2.yaml'],
            ),
        ),
        pytest.param(
            LookupRowsParams(
                request_data=[{'hash': 10987}],
                expected_content_path='response_lookup_rows_expected_3.json',
            ),
            id='case without mock',
        ),
    ],
)
async def test_yt_lookup_rows(
        taxi_example_service_web, yt_apply, load_json, params,
):
    response = await taxi_example_service_web.get(
        '/yt/lookup_rows',
        params={'request_data': json.dumps(params.request_data)},
    )
    assert response.status == 200
    content = json.loads(await response.text())
    assert content == load_json(params.expected_content_path)


class SelectRowsParams(typing.NamedTuple):
    request_query: str
    expected_content_path: str


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            SelectRowsParams(
                request_query=(
                    'id FROM [//home/testsuite/select_table] '
                    'WHERE id="some_id"'
                ),
                expected_content_path='response_select_rows_expected_1.json',
            ),
            id='simple case',
            marks=pytest.mark.yt(
                dyn_table_data=['yt_response_select_rows_1.yaml'],
            ),
        ),
        pytest.param(
            SelectRowsParams(
                request_query=(
                    '* FROM [//home/testsuite/select_table] WHERE hash=475638'
                ),
                expected_content_path='response_select_rows_expected_2.json',
            ),
            id='simple case 2',
            marks=pytest.mark.yt(
                dyn_table_data=['yt_response_select_rows_2.yaml'],
            ),
        ),
        pytest.param(
            SelectRowsParams(
                request_query=(
                    '* FROM [//home/testsuite/select_table] WHERE hash=898980'
                ),
                expected_content_path='response_select_rows_expected_3.json',
            ),
            id='case without mock',
        ),
    ],
)
async def test_yt_select_rows(
        taxi_example_service_web, yt_apply, load_json, params,
):
    response = await taxi_example_service_web.get(
        '/yt/select_rows', params={'sql_query': params.request_query},
    )
    assert response.status == 200
    content = json.loads(await response.text())
    assert content == load_json(params.expected_content_path)


async def test_testpoint(taxi_example_service_web, testpoint):
    @testpoint('some_testpoint_name')
    def testpoint_handler(data):
        assert data == {'name': 'John', 'surname': 'Wick'}

    response = await taxi_example_service_web.get('/use_testpoint')
    assert response.status == 200
    assert testpoint_handler.times_called == 1
