import http

import pytest

from test_document_templator import common
from test_document_templator import test_dynamic_documents


@pytest.mark.parametrize(
    'body, expected_status, expected_content',
    [
        (
            test_dynamic_documents.update_data(
                'generation data', 'contains data for generation dynamic_text',
            ),
            http.HTTPStatus.OK,
            common.GENERATED_TEXT,
        ),
        # base template generation
        (
            test_dynamic_documents.update_data(
                'n',
                'd',
                '1ff4901c583745e089e55be0',
                [{'name': 'base template parameter1', 'value': 'text'}],
                [{'id': '5ff4901c583745e089e55bd3', 'name': 'req1'}],
            ),
            http.HTTPStatus.OK,
            'BASE ITEM1 <p>Base PARENT_DATA string [text]</p>\n'
            '<p>Base SERVER_DATA string: 10.0</p>\n',
        ),
        # base's child1 template generation
        (
            test_dynamic_documents.update_data(
                'n',
                'd',
                '1ff4901c583745e089e55be1',
                [
                    {'name': 'base template parameter1', 'value': 'base text'},
                    {'name': 'child1 template parameter1', 'value': 1},
                ],
                [
                    {'id': '5ff4901c583745e089e55bd3', 'name': 'req1'},
                    {
                        'id': '5d275bc3eb584657ebbf24b2',
                        'name': 'req3',
                        'substitutions': {'zone': 'moscow'},
                    },
                ],
            ),
            http.HTTPStatus.OK,
            common.CHILD1_GENERATED_TEXT,
        ),
        # base's child2 template generation
        (
            test_dynamic_documents.update_data(
                'n',
                'd',
                '1ff4901c583745e089e55be2',
                [{'name': 'base template parameter2', 'value': 'base text2'}],
                [
                    {
                        'id': '5ff4901c583745e089e55bd1',
                        'name': 'req2',
                        'query': {'q1': 1, 'q2': 'string'},
                        'substitutions': {
                            'zone': 'moscow',
                            'tariff': 'econom',
                        },
                        'body': {'a': {'b': [], 'c': 1}},
                    },
                ],
            ),
            http.HTTPStatus.OK,
            'BASE ITEM2 <p>Base PARENT_DATA string [base text2]</p>\n'
            '<p>Base SERVER_DATA string: body: '
            '{\'a\': {\'b\': [], \'c\': 1}}; '
            'queries: q1=1, q2=string</p>\n'
            'CHILD2 ITEM3 Some text\n\n',
        ),
        # child1s child11 template generation
        (
            test_dynamic_documents.update_data(
                'n',
                'd',
                '1ff4901c583745e089e55be3',
                [
                    {
                        'name': 'base template parameter1',
                        'value': 'base text3',
                    },
                    {'name': 'child1 template parameter1', 'value': 11},
                    {
                        'name': 'child11 template parameter1',
                        'value': 'child11 text',
                    },
                ],
                [
                    {'id': '5ff4901c583745e089e55bd3', 'name': 'req1'},
                    {
                        'id': '5d275bc3eb584657ebbf24b2',
                        'name': 'req3',
                        'substitutions': {'zone': 'moscow'},
                    },
                ],
            ),
            http.HTTPStatus.OK,
            'BASE ITEM1 <p>Base PARENT_DATA string [base text3]</p>\n'
            '<p>Base SERVER_DATA string: 10.0</p>\n'
            'CHILD11 ITEM3 <p>Child11 PARENT_DATA '
            'string [child11 text]</p>\n'
            'CHILD1 ITEM3 <p>Child1 PARENT_DATA number [11]</p>\n'
            '<p>Child1 SERVER_DATA string: moscow</p>\n',
        ),
        (
            {
                'name': 'n',
                'description': 'd',
                # not existing template_id
                'template_id': '5ff4901c583745e089e55be9',
                'params': None,
                'requests_params': None,
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'TEMPLATE_NOT_FOUND_ERROR',
                'details': {},
                'message': (
                    'template with id=5ff4901c583745e089e55be9 ' 'not found'
                ),
            },
        ),
        (
            {
                'name': 'n',
                'description': 'd',
                'template_id': '5ff4901c583745e089e55be1',
                # params with equal names
                'params': [
                    {'name': 'p1', 'value': 's'},
                    {'name': 'p1', 'value': 's'},
                ],
                'requests_params': None,
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'PARAMETER_NAMES_COLLIDED',
                'details': {
                    'template_id': '5ff4901c583745e089e55be1',
                    'template_name': 'test',
                },
                'message': 'Parameter names collided. Type: request_params.',
            },
        ),
        (
            {
                'name': 'n',
                'description': 'd',
                'template_id': '5ff4901c583745e089e55be1',
                'params': None,
                # requests params with equal names
                'requests_params': [
                    {'id': '5ff4901c583745e089e55bd1', 'name': 'rp1'},
                    {'id': '5ff4901c583745e089e55bd1', 'name': 'rp1'},
                ],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'PARAMETER_NAMES_COLLIDED',
                'details': {
                    'template_id': '5ff4901c583745e089e55be1',
                    'template_name': 'test',
                },
                'message': 'Parameter names collided. Type: params.',
            },
        ),
        (
            {
                'name': 'n',
                'description': 'd',
                'template_id': '5ff4901c583745e089e55be1',
                'params': None,
                # requests params None but template requests not
                'requests_params': None,
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'PARAMETERS_NOT_FILLED',
                'details': {
                    'template_id': '5ff4901c583745e089e55be1',
                    'template_name': 'test',
                },
                'message': (
                    'Not all request_params filled. '
                    'Got: []. Need: [\'req1\', \'req2\', \'req3\'].'
                ),
            },
        ),
        (
            {
                'name': 'n',
                'description': 'd',
                'template_id': '5ff4901c583745e089e55be1',
                'params': None,
                # not enough number of requests params
                'requests_params': [
                    {'id': '5ff4901c583745e089e55bd1', 'name': 'req1'},
                ],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'PARAMETERS_NOT_FILLED',
                'details': {
                    'template_id': '5ff4901c583745e089e55be1',
                    'template_name': 'test',
                },
                'message': (
                    'Not all request_params filled. '
                    'Got: [\'req1\']. '
                    'Need: [\'req1\', \'req2\', \'req3\'].'
                ),
            },
        ),
        (
            {
                'name': 'n',
                'description': 'd',
                'template_id': '5ff4901c583745e089e55be1',
                'params': None,
                # req3 in requests not resolved
                'requests_params': [
                    {'id': '5ff4901c583745e089e55bd1', 'name': 'req1'},
                    {'id': '5ff4901c583745e089e55bd2', 'name': 'req2'},
                    {'id': '5ff4901c583745e089e55bd3', 'name': 'req4'},
                ],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'PARAMETERS_NOT_FILLED',
                'details': {
                    'template_id': '5ff4901c583745e089e55be1',
                    'template_name': 'test',
                },
                'message': (
                    'Not all request_params filled. '
                    'Got: [\'req1\', \'req2\', \'req4\']. '
                    'Need: [\'req1\', \'req2\', \'req3\'].'
                ),
            },
        ),
        (
            {
                'name': 'n',
                'description': 'd',
                'template_id': '5ff4901c583745e089e55be1',
                'params': None,
                # req1 substitutons are None
                'requests_params': [
                    {'id': '5ff4901c583745e089e55bd1', 'name': 'req1'},
                    {'id': '5ff4901c583745e089e55bd2', 'name': 'req2'},
                    {'id': '5ff4901c583745e089e55bd3', 'name': 'req3'},
                ],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_SUBSTITUTION_DOES_NOT_MATCH',
                'details': {
                    'actual': [],
                    'expected': ['tariff', 'zone'],
                    'template_id': '5ff4901c583745e089e55be1',
                    'template_name': 'test',
                },
                'message': 'Substitutions does not match.',
            },
        ),
        (
            {
                'name': 'n',
                'description': 'd',
                'template_id': '5ff4901c583745e089e55be1',
                'params': None,
                # req1 number of substitutons not enough
                'requests_params': [
                    {
                        'id': '5ff4901c583745e089e55bd1',
                        'name': 'req1',
                        'substitutions': {'zone': ''},
                    },
                    {'id': '5ff4901c583745e089e55bd2', 'name': 'req2'},
                    {'id': '5ff4901c583745e089e55bd3', 'name': 'req3'},
                ],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_SUBSTITUTION_DOES_NOT_MATCH',
                'details': {
                    'actual': ['zone'],
                    'expected': ['tariff', 'zone'],
                    'template_id': '5ff4901c583745e089e55be1',
                    'template_name': 'test',
                },
                'message': 'Substitutions does not match.',
            },
        ),
        (
            {
                'name': 'n',
                'description': 'd',
                'template_id': '5ff4901c583745e089e55be1',
                'params': None,
                # req1 'tariff' substituton not specified
                'requests_params': [
                    {
                        'id': '5ff4901c583745e089e55bd1',
                        'name': 'req1',
                        'substitutions': {'zone': '', 's': ''},
                    },
                    {'id': '5ff4901c583745e089e55bd2', 'name': 'req2'},
                    {'id': '5ff4901c583745e089e55bd3', 'name': 'req3'},
                ],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_SUBSTITUTION_DOES_NOT_MATCH',
                'details': {
                    'actual': ['s', 'zone'],
                    'expected': ['tariff', 'zone'],
                    'template_id': '5ff4901c583745e089e55be1',
                    'template_name': 'test',
                },
                'message': 'Substitutions does not match.',
            },
        ),
        (
            {
                'name': 'n',
                'description': 'd',
                'template_id': '5ff4901c583745e089e55be1',
                'params': None,
                # req1 'tariff' substituton has wrong type (dict)
                'requests_params': [
                    {
                        'id': '5ff4901c583745e089e55bd1',
                        'name': 'req1',
                        'substitutions': {'zone': '', 'tariff': {}},
                    },
                    {'id': '5ff4901c583745e089e55bd2', 'name': 'req2'},
                    {'id': '5ff4901c583745e089e55bd3', 'name': 'req3'},
                ],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_SUBSTITUTION_HAS_INVALID_TYPE',
                'details': {
                    'template_id': '5ff4901c583745e089e55be1',
                    'template_name': 'test',
                    'type': '<class \'dict\'>',
                    'value': '{}',
                },
                'message': 'Substitution has invalid type.',
            },
        ),
        (
            {
                'name': 'n',
                'description': 'd',
                'template_id': '5ff4901c583745e089e55be1',
                'params': None,
                # req2 request fails
                'requests_params': [
                    common.REQUESTS_PARAMS[0],
                    {
                        'id': '5ff4901c583745e089e55bd2',
                        'name': 'req2',
                        'query': {'q': ''},
                    },
                    {'id': '5ff4901c583745e089e55bd3', 'name': 'req3'},
                ],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'EXECUTING_REQUEST_FAILED',
                'details': {
                    'endpoint_name': 'Text',
                    'reason': 'unexpected query param',
                    'status': 402,
                    'template_id': '5ff4901c583745e089e55be1',
                    'template_name': 'test',
                },
                'message': (
                    'Executing request with endpoint_'
                    'name="Text" failed with '
                    'status="402" and reason="unexpected query param"'
                ),
            },
        ),
    ],
)
@pytest.mark.usefixtures('requests_handlers')
@pytest.mark.config(**common.REQUEST_CONFIG)
async def test_generate_preview(
        api_app_client, body, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.post(
        '/v1/dynamic_documents/preview/generate/', json=body, headers=headers,
    )
    assert response.status == expected_status, await response.text()
    content = await response.json()
    if expected_status == http.HTTPStatus.OK:
        assert content['generated_text'] == expected_content
    else:
        assert content == expected_content


@pytest.mark.parametrize(
    'body, expected_status, expected_content',
    (
        (
            {
                'name': 'test',
                'description': 'test',
                'template_id': '1ff4901c583745e089e55be0',
                'params': [
                    {'name': 'base template parameter1', 'value': 'text'},
                ],
                'requests_params': [
                    {'id': '5ff4901c583745e089e55bd3', 'name': 'req1'},
                ],
            },
            http.HTTPStatus.OK,
            (
                'BASE ITEM1 <p>Base PARENT_DATA string [<span '
                'style="position:relative;color:#4296ea;">'
                'text<span style="position: '
                'absolute; top: -4px; right: -10px; '
                'font-size: 8px; color: Coral">base '
                'template parameter1</span></span>]</p>\n'
                '<p>Base SERVER_DATA string: <span '
                'style="position:relative;color:#4296ea;">'
                '10.0<span style="position: '
                'absolute; top: -4px; right: -10px; font-size: 8px; color: '
                'Coral">req1.num</span></span></p>\n'
            ),
        ),
    ),
)
@pytest.mark.usefixtures('requests_handlers')
@pytest.mark.config(**common.REQUEST_CONFIG)
async def test_generate_preview_with_tips(
        api_app_client, body, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.post(
        '/v1/dynamic_documents/preview/generate/',
        json=body,
        headers=headers,
        params={'show_tips': 'true'},
    )
    assert response.status == expected_status, await response.text()
    content = await response.json()
    if expected_status == http.HTTPStatus.OK:
        assert content['generated_text'] == expected_content
    else:
        assert content == expected_content
