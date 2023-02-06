import aiohttp.web
import pytest


# root conftest for service pro-gateway
pytest_plugins = ['pro_gateway_plugins.pytest_plugins']

REMOTE_RESPONSE = {'sentinel': True}
URL_PATH = 'test/test'
CONSUMER_HEADER = 'X-Platform-Consumer'
CONSUMER = 'consumer'


@pytest.fixture(name='ignore_trace_id', autouse=True)
def _ignore_trace_id(mockserver):
    with mockserver.ignore_trace_id():
        yield


@pytest.fixture
def am_proxy_name():
    return 'pro-gateway'


@pytest.fixture
def mock_remote(mockserver):
    def _wrapper(url_path=URL_PATH, response_code=200, response_body=None):
        if response_body is None:
            response_body = REMOTE_RESPONSE

        @mockserver.json_handler(f'/{url_path}')
        def handler(request):
            return aiohttp.web.json_response(
                status=response_code, data=response_body,
            )

        return handler

    return _wrapper


@pytest.fixture
async def make_request(taxi_pro_gateway):
    async def _wrapper(
            url_path=URL_PATH,
            request_body=None,
            headers=None,
            params=None,
            token=None,
            method='post',
    ):
        if request_body is None:
            request_body = ''
        if headers is None:
            headers = {}
        if 'Origin' not in headers:
            headers['origin'] = 'localhost'

        if not params:
            params = {}

        method = method.lower()
        if method == 'post':
            response = await taxi_pro_gateway.post(
                url_path, json=request_body, headers=headers, params=params,
            )
        elif method == 'put':
            response = await taxi_pro_gateway.put(
                url_path, json=request_body, headers=headers, params=params,
            )
        elif method == 'patch':
            response = await taxi_pro_gateway.patch(
                url_path, json=request_body, headers=headers, params=params,
            )
        elif method == 'delete':
            response = await taxi_pro_gateway.delete(
                url_path, json=request_body, headers=headers, params=params,
            )
        elif method == 'get':
            response = await taxi_pro_gateway.get(
                url_path, headers=headers, params=params,
            )
        elif method == 'options':
            response = await taxi_pro_gateway.options(
                url_path, headers=headers, params=params,
            )
        else:
            assert False
        return response

    return _wrapper


# ya tool tvmknife unittest service -s 404 -d 2345
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIlAMQqRI:Ta6H2YvxBztdoylkA5V9jOsk_ZoEfPw8MEr1N'
    'et0nrw84sTLgkL3iw6Db4qL7-GifB4Pm06RAoQAseBmmCTdHmYjd0Vk-py6lFR6iQK9QprtN'
    '3Z5_k4fDQ-JLEY9cI6L5qGs2Dcsprt8zTXjmCQPY5CdQnWPOSuU6iu9AqHYWPY'
)


@pytest.fixture
async def service_ticket():
    return MOCK_SERVICE_TICKET


@pytest.fixture
def request_headers():
    def _wrapper(consumer=CONSUMER, additional_headers=None):
        headers = {
            'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
            'X-Remote-Ip': '192.1.1.200',
            'X-Forwarded-For-Y': '192.1.1.200',
            'X-Forwarded-Host': 'localhost',
        }
        if consumer:
            headers[CONSUMER_HEADER] = consumer
        if not additional_headers:
            additional_headers = {}
        return {**headers, **additional_headers}

    return _wrapper
