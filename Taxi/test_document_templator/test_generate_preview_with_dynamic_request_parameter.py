import http
import json

import pytest


@pytest.mark.parametrize(
    'param, expected_status, expected_content',
    (
        (
            {
                'name': 'req',
                'id': '111111111111111111111111',
                'query': [
                    {
                        'name': 'query',
                        'type': 'string',
                        'data_usage': 'CALCULATED',
                        'value': {
                            'operator': 'ADD',
                            'right': {
                                'type': 'string',
                                'value': '_param',
                                'data_usage': 'OWN_DATA',
                            },
                            'left': {
                                'type': 'string',
                                'value': 'query',
                                'data_usage': 'OWN_DATA',
                            },
                        },
                    },
                ],
                'substitutions': [
                    {
                        'name': 'id',
                        'type': 'string',
                        'data_usage': 'CALCULATED',
                        'value': {
                            'operator': 'MUL',
                            'right': {
                                'type': 'number',
                                'value': 24,
                                'data_usage': 'OWN_DATA',
                            },
                            'left': {
                                'type': 'string',
                                'value': '1',
                                'data_usage': 'OWN_DATA',
                            },
                        },
                    },
                ],
                'body': {
                    'type': 'object',
                    'data_usage': 'CALCULATED',
                    'value': {
                        'operator': 'DICT_BUILD',
                        'values': [
                            {
                                'key': {
                                    'value': 'key1',
                                    'data_usage': 'OWN_DATA',
                                    'type': 'string',
                                },
                                'value': {
                                    'type': 'object',
                                    'data_usage': 'CALCULATED',
                                    'value': {
                                        'operator': 'LIST_BUILD',
                                        'values': [
                                            {
                                                'value': {
                                                    'value': 'list_value1',
                                                    'data_usage': 'OWN_DATA',
                                                    'type': 'string',
                                                },
                                            },
                                            {
                                                'value': {
                                                    'value': 'list_value2',
                                                    'data_usage': 'OWN_DATA',
                                                    'type': 'string',
                                                },
                                            },
                                        ],
                                    },
                                },
                            },
                            {
                                'key': {
                                    'value': False,
                                    'data_usage': 'OWN_DATA',
                                    'type': 'boolean',
                                },
                                'value': {
                                    'value': {'key4': 'value4'},
                                    'data_usage': 'OWN_DATA',
                                    'type': 'object',
                                },
                            },
                        ],
                    },
                },
            },
            http.HTTPStatus.OK,
            {
                'generated_text': (
                    'query: \'query_param\', body: {\'key1\': '
                    '[\'list_value1\', \'list_value2\'], '
                    '\'false\': {\'key4\': \'value4\'}}'
                ),
            },
        ),
        (
            {
                'name': 'req',
                'id': '111111111111111111111111',
                'body': {
                    'type': 'string',
                    'data_usage': 'OWN_DATA',
                    'value': 'string',
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_TYPE_MATCHING_FAILED',
                'message': (
                    'Data type matching failed. Need: "object". Got: "string".'
                ),
                'details': {'param_name': 'body', 'template_name': 'test'},
            },
        ),
    ),
)
@pytest.mark.config(
    DOCUMENT_TEMPLATOR_REQUESTS={
        'With body': {
            'method': 'POST',
            'url_pattern': '$mockserver/generate/{id}/',
            'timeout_in_ms': 100,
            'retries_count': 3,
        },
    },
)
async def test_generate_preview_with_dynamic_request_parameter(
        api_app_client, param, expected_status, expected_content, mockserver,
):
    @mockserver.json_handler('/generate/111111111111111111111111/')
    def _handler(request):
        query = request.query.get('query')
        return {'test': f'query: {query!r}, body: {request.json!r}'}

    headers = {'X-Yandex-Login': 'test_name'}
    body = {
        'template': {
            'name': 'test',
            'description': 'test',
            'items': [
                {
                    'template_id': '111111111111111111111111',
                    'requests_params': [param],
                },
            ],
        },
    }
    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    content.pop('id', None)
    content.pop('status', None)
    assert content == expected_content
