import pytest


@pytest.mark.parametrize(
    'body',
    [
        {'functions': []},
        {
            'functions': [
                {
                    'name': 'sample_function',
                    'signature': {
                        'arguments': [],
                        'return_value': {'schema': {'type': 'boolean'}},
                    },
                },
            ],
        },
        {
            'functions': [
                {
                    'name': 'sample_function1',
                    'signature': {
                        'arguments': [],
                        'return_value': {'schema': {'type': 'boolean'}},
                    },
                },
                {
                    'name': 'sample_function2',
                    'signature': {
                        'arguments': [
                            {
                                'name': 'sample_argument',
                                'schema': {'type': 'integer'},
                            },
                        ],
                        'return_value': {'schema': {'type': 'boolean'}},
                    },
                },
            ],
        },
    ],
)
async def test_list_native_functions(web_app_client, mockserver, body):
    consumer = 'taxi-surge'
    service = 'surge-calculator'

    @mockserver.json_handler(
        f'/{service}/v1/js/pipeline/native-functions-list',
    )
    def _native_functions_list(request):
        return body

    response = await web_app_client.post(
        '/v2/pipeline/native-functions-list', params={'consumer': consumer},
    )
    assert response.status == 200
    assert await response.json() == body
