import http

import pytest

from test_document_templator import common

ITEMS = [
    {
        'id': '5ff4901c583745e089e55ba1',
        'params': common.ITEMS_PARAMS,
        'requests_params': [{'id': '5ff4901c583745e089e55bd3', 'name': 'req'}],
        'description': 'item1 description',
        'template_id': '5ff4901c583745e089e55be2',
        'items': [
            {
                'id': '5ff4901c583745e089e55ba3',
                'params': [
                    {
                        'name': 'subitem1 parameter1',
                        'type': 'array',
                        'data_usage': 'OWN_DATA',
                        'value': [1, 2],
                    },
                ],
                'description': 'item1 description',
                'template_id': '5ff4901c583745e089e55ba4',
                'enabled': True,
                'inherited': False,
            },
            {
                'id': '5ff4901c583745e089e55ba4',
                'description': 'item2 description',
                'content': 'some content',
                'enabled': True,
                'inherited': False,
            },
        ],
        'enabled': True,
        'inherited': False,
    },
    {
        'id': '5ff4901c583745e089e55ba2',
        'content': '<p>Some content</p>',
        'enabled': True,
        'inherited': False,
    },
]

REQUESTS = [
    {
        'id': '5ff4901c583745e089e55bd1',
        'name': 'req1',
        'enabled': True,
        'inherited': False,
    },
    {
        'id': '5ff4901c583745e089e55bd2',
        'name': 'req2',
        'enabled': True,
        'inherited': False,
    },
    {
        'id': '5ff4901c583745e089e55bd3',
        'name': 'req3',
        'enabled': True,
        'inherited': False,
    },
]


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            # document with 2 versions
            {'id': '5ff4901c583745e089e55be1'},
            http.HTTPStatus.OK,
            {
                'name': 'test',
                'id': '5ff4901c583745e089e55be1',
                'version': 1,
                'description': 'some text',
                'params': [
                    {
                        'name': 'template parameter1',
                        'description': 'template parameter1 description',
                        'type': 'object',
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'v1': {'type': 'string'},
                                'v2': {'type': 'number'},
                                'v3': {'type': 'boolean'},
                                'v4': {
                                    'type': 'object',
                                    'properties': {
                                        'v4v1': {
                                            'type': 'array',
                                            'items': {'type': 'number'},
                                        },
                                        'v4v2': {'type': 'number'},
                                    },
                                },
                            },
                        },
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'template parameter2',
                        'type': 'array',
                        'schema': {
                            'type': 'array',
                            'items': {'type': 'string'},
                        },
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'template parameter3',
                        'type': 'string',
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'template parameter4',
                        'type': 'number',
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'template parameter5',
                        'type': 'boolean',
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'items': ITEMS,
                'requests': REQUESTS,
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_by': 'russhakirov',
                'modified_at': '2018-07-01T01:00:00+03:00',
            },
        ),
        (
            # document with 1 version
            {'id': '5ff4901c583745e089e55be2'},
            http.HTTPStatus.OK,
            {
                'name': 'text',
                'id': '5ff4901c583745e089e55be2',
                'version': 0,
                'description': 'some',
                'params': [
                    {
                        'name': 'own array parameter',
                        'type': 'array',
                        'schema': {
                            'type': 'array',
                            'items': {'type': 'string'},
                        },
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'own string parameter',
                        'type': 'string',
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'own number parameter',
                        'type': 'number',
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'own object parameter',
                        'type': 'object',
                        'schema': {
                            'type': 'object',
                            'properties': {'own_obj_data': {'type': 'number'}},
                        },
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'parent template array parameter',
                        'type': 'array',
                        'schema': {
                            'type': 'array',
                            'items': {'type': 'string'},
                        },
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'parent template string parameter',
                        'type': 'string',
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'parent template number parameter',
                        'type': 'number',
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'parent template object parameter',
                        'type': 'object',
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'v4v1': {
                                    'type': 'array',
                                    'items': {'type': 'number'},
                                },
                                'v4v2': {'type': 'number'},
                            },
                        },
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'server array parameter',
                        'type': 'array',
                        'schema': {'type': 'array'},
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'server string parameter',
                        'type': 'string',
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'server number parameter',
                        'type': 'number',
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'server object parameter',
                        'type': 'object',
                        'schema': {
                            'type': 'object',
                            'properties': {'r1': {'type': 'string'}},
                        },
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'items': [
                    {
                        'id': '5ff4901c583745e089e55ba5',
                        'content': (
                            '<p>OWN_DATA string '
                            '[<span data-variable=\"'
                            'own string parameter\">'
                            '</span>]</p>\n'
                            '<p>OWN_DATA number\n'
                            '<span data-variable=\"'
                            'own number parameter\">'
                            '</span>\n</p>\n'
                            '<p>OWN_DATA boolean\n'
                            '<span data-variable=\"'
                            'own boolean parameter\">'
                            '</span>\n</p>\n'
                            '<p>OWN_DATA object: '
                            '<span data-variable=\"'
                            'own object parameter.own_obj_data\">'
                            '</span>'
                            '</p>\n'
                            '<p>PARENT_TEMPLATE_DATA string: '
                            '<span data-variable=\"'
                            'parent template string parameter\">'
                            '</span>'
                            '</p>\n'
                            '<p>PARENT_TEMPLATE_DATA number: '
                            '<span data-variable=\"'
                            'parent template number parameter\">'
                            '</span>'
                            '</p>\n'
                            '<p>PARENT_TEMPLATE_DATA boolean: '
                            '<span data-variable=\"'
                            'parent template boolean parameter\">'
                            '</span>'
                            '</p>\n'
                            '<p>PARENT_TEMPLATE_DATA object: '
                            '<span data-variable=\"'
                            'parent template object parameter.v4v2\">'
                            '</span></p>\n'
                            '<p>SERVER_DATA string: '
                            '<span data-variable=\"'
                            'server string parameter\">'
                            '</span></p>\n'
                            '<p>SERVER_DATA number: '
                            '<span data-variable=\"'
                            'server number parameter\">'
                            '</span></p>\n'
                            '<p>SERVER_DATA boolean: '
                            '<span data-variable=\"'
                            'server boolean parameter\">'
                            '</span></p>\n'
                            '<p>SERVER_DATA object: '
                            '<span data-variable=\"'
                            'server object parameter.r1\">'
                            '</span></p>\n'
                            '<p>SERVER_DATA string: '
                            '<span data-variable=\"req.num\" '
                            'data-request-id='
                            '\"5ff4901c583745e089e55bd3\">'
                            '</span></p>'
                        ),
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'requests': [
                    {
                        'id': '5ff4901c583745e089e55bd3',
                        'name': 'req',
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_by': 'russhakirov',
                'modified_at': '2018-07-01T01:00:00+03:00',
            },
        ),
        (
            # base template
            {'id': '1ff4901c583745e089e55be0'},
            http.HTTPStatus.OK,
            {
                'name': 'base',
                'id': '1ff4901c583745e089e55be0',
                'version': 0,
                'description': 'base template',
                'params': [
                    {
                        'name': 'base template parameter1',
                        'description': 'base template parameter1 description',
                        'type': 'string',
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'name': 'base template parameter2',
                        'description': 'base template parameter2 description',
                        'type': 'string',
                        'enabled': False,
                        'inherited': False,
                    },
                ],
                'items': [
                    {
                        'id': '1ff4901c583745e089e55ba1',
                        'content': common.BASE_ITEM1_CONTENT,
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'id': '1ff4901c583745e089e55ba2',
                        'content': common.BASE_ITEM2_CONTENT,
                        'enabled': False,
                        'inherited': False,
                    },
                ],
                'requests': [
                    {
                        'id': '5ff4901c583745e089e55bd3',
                        'name': 'req1',
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'id': '5ff4901c583745e089e55bd1',
                        'name': 'req2',
                        'enabled': False,
                        'inherited': False,
                    },
                ],
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_by': 'russhakirov',
                'modified_at': '2018-07-01T01:00:00+03:00',
            },
        ),
        (
            # base template's child1
            {'id': '1ff4901c583745e089e55be1'},
            http.HTTPStatus.OK,
            {
                'name': 'child1',
                'base_template_id': '1ff4901c583745e089e55be0',
                'id': '1ff4901c583745e089e55be1',
                'version': 0,
                'description': 'child1 template',
                'params': [
                    {
                        'name': 'base template parameter1',
                        'description': 'base template parameter1 description',
                        'type': 'string',
                        'enabled': True,
                        'inherited': True,
                    },
                    {
                        'name': 'base template parameter2',
                        'description': 'base template parameter2 description',
                        'type': 'string',
                        'enabled': False,
                        'inherited': True,
                    },
                    {
                        'name': 'child1 template parameter1',
                        'description': (
                            'child1 template parameter1 ' 'description'
                        ),
                        'type': 'number',
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'items': [
                    {
                        'id': '1ff4901c583745e089e55ba1',
                        'content': common.BASE_ITEM1_CONTENT,
                        'enabled': True,
                        'inherited': True,
                    },
                    {
                        'id': '1ff4901c583745e089e55ba2',
                        'content': common.BASE_ITEM2_CONTENT,
                        'enabled': False,
                        'inherited': True,
                    },
                    {
                        'id': '1ff4901c583745e089e55ba3',
                        'content': common.CHILD1_ITEM3_CONTENT,
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'requests': [
                    {
                        'id': '5ff4901c583745e089e55bd3',
                        'name': 'req1',
                        'enabled': True,
                        'inherited': True,
                    },
                    {
                        'id': '5ff4901c583745e089e55bd1',
                        'name': 'req2',
                        'enabled': False,
                        'inherited': True,
                    },
                    {
                        'id': '5d275bc3eb584657ebbf24b2',
                        'name': 'req3',
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_by': 'russhakirov',
                'modified_at': '2018-07-01T01:00:00+03:00',
            },
        ),
        (
            # base template's child2
            {'id': '1ff4901c583745e089e55be2'},
            http.HTTPStatus.OK,
            {
                'name': 'child2',
                'base_template_id': '1ff4901c583745e089e55be0',
                'id': '1ff4901c583745e089e55be2',
                'version': 0,
                'description': 'child2 template',
                'params': [
                    {
                        'name': 'base template parameter1',
                        'description': 'base template parameter1 description',
                        'type': 'string',
                        'enabled': False,
                        'inherited': True,
                    },
                    {
                        'name': 'base template parameter2',
                        'description': 'base template parameter2 description',
                        'type': 'string',
                        'enabled': True,
                        'inherited': True,
                    },
                ],
                'items': [
                    {
                        'id': '1ff4901c583745e089e55ba1',
                        'content': common.BASE_ITEM1_CONTENT,
                        'enabled': False,
                        'inherited': True,
                    },
                    {
                        'id': '1ff4901c583745e089e55ba2',
                        'content': common.BASE_ITEM2_CONTENT,
                        'enabled': True,
                        'inherited': True,
                    },
                    {
                        'id': '1ff4901c583745e089e55ba4',
                        'content': common.CHILD2_ITEM3_CONTENT,
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'requests': [
                    {
                        'id': '5ff4901c583745e089e55bd3',
                        'name': 'req1',
                        'enabled': False,
                        'inherited': True,
                    },
                    {
                        'id': '5ff4901c583745e089e55bd1',
                        'name': 'req2',
                        'enabled': True,
                        'inherited': True,
                    },
                ],
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_by': 'russhakirov',
                'modified_at': '2018-07-01T01:00:00+03:00',
            },
        ),
        (
            # child1s child11
            {'id': '1ff4901c583745e089e55be3'},
            http.HTTPStatus.OK,
            {
                'name': 'child11',
                'base_template_id': '1ff4901c583745e089e55be1',
                'id': '1ff4901c583745e089e55be3',
                'version': 0,
                'description': 'child1s child1 template',
                'params': [
                    {
                        'name': 'base template parameter1',
                        'description': 'base template parameter1 description',
                        'type': 'string',
                        'enabled': True,
                        'inherited': True,
                    },
                    {
                        'name': 'base template parameter2',
                        'description': 'base template parameter2 description',
                        'type': 'string',
                        'enabled': False,
                        'inherited': True,
                    },
                    {
                        'name': 'child1 template parameter1',
                        'description': (
                            'child1 template parameter1 ' 'description'
                        ),
                        'type': 'number',
                        'enabled': True,
                        'inherited': True,
                    },
                    {
                        'name': 'child11 template parameter1',
                        'description': (
                            'child11 template parameter1 ' 'description'
                        ),
                        'type': 'string',
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'items': [
                    {
                        'id': '1ff4901c583745e089e55ba1',
                        'content': common.BASE_ITEM1_CONTENT,
                        'enabled': True,
                        'inherited': True,
                    },
                    {
                        'id': '1ff4901c583745e089e55ba2',
                        'content': common.BASE_ITEM2_CONTENT,
                        'enabled': False,
                        'inherited': True,
                    },
                    {
                        'id': '1ff4901c583745e089e55ba5',
                        'content': common.CHILD11_ITEM3_CONTENT,
                        'enabled': True,
                        'inherited': False,
                    },
                    {
                        'id': '1ff4901c583745e089e55ba3',
                        'content': common.CHILD1_ITEM3_CONTENT,
                        'enabled': True,
                        'inherited': True,
                    },
                ],
                'requests': [
                    {
                        'id': '5ff4901c583745e089e55bd3',
                        'name': 'req1',
                        'enabled': True,
                        'inherited': True,
                    },
                    {
                        'id': '5ff4901c583745e089e55bd1',
                        'name': 'req2',
                        'enabled': False,
                        'inherited': True,
                    },
                    {
                        'id': '5d275bc3eb584657ebbf24b2',
                        'name': 'req3',
                        'enabled': True,
                        'inherited': True,
                    },
                ],
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_by': 'russhakirov',
                'modified_at': '2018-07-01T01:00:00+03:00',
            },
        ),
        # removed document with 2 versions
        (
            {'id': '5ff4901c583745e089e55bf6'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'TEMPLATE_NOT_FOUND_ERROR',
                'details': {},
                'message': (
                    'template with ' 'id=5ff4901c583745e089e55bf6 not found'
                ),
            },
        ),
        # missing document
        (
            {'id': '5ff4901c583745e089e55bf7'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'TEMPLATE_NOT_FOUND_ERROR',
                'details': {},
                'message': (
                    'template with ' 'id=5ff4901c583745e089e55bf7 not found'
                ),
            },
        ),
        (
            {},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'id is required parameter'},
                'message': 'Some parameters are invalid',
            },
        ),
    ],
)
async def test_get_template(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.get(
        '/v1/template/', params=query, headers=headers,
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content
