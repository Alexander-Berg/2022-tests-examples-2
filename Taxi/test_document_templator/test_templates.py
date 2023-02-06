# pylint: disable=C0302
import copy
import http
import json
import typing
from typing import List
from typing import Optional

import pytest

from document_templator.generated.api import web_context
from document_templator.repositories import template_repository
from test_document_templator import common


def _unsaved_template(param=None) -> dict:
    if param is None:
        items = common.ITEMS
    else:
        item_0 = copy.copy(typing.cast(dict, common.ITEMS[0]))
        item_params = copy.copy(item_0['params'])
        item_params.append(param)
        item_0['params'] = item_params
        items = [item_0, common.ITEMS[1]]

    return {
        'template': {
            'name': 'name',
            'description': 'test',
            'items': items,
            'params': common.TEMPLATE_PARAMS,
            'requests': common.REQUESTS,
        },
        'requests_params': common.REQUESTS_PARAMS,
        'params': common.PARAMS,
    }


def _unsaved_template_content_items(name: str, changed_item=None) -> dict:
    items = copy.copy(common.CONTENT_ITEMS)
    if changed_item is not None:
        items[changed_item['index']] = changed_item['content']
    return {
        'template': {
            'name': name,
            'description': 'test description',
            'params': common.CONTENT_ITEMS_PARAMS_IN_TEMPLATE,
            'items': items,
            'requests': common.CONTENT_ITEMS_REQUESTS,
        },
        'params': common.CONTENT_ITEMS_PARAMS,
        'requests_params': common.CONTENT_ITEMS_REQUESTS_PARAMS,
    }


def _unsaved_inherited_content_items(
        items: Optional[List[dict]] = None,
        requests: Optional[List[dict]] = None,
):
    if not items:
        items = [
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
            {'content': common.CHILD1_ITEM3_CONTENT, 'enabled': True},
        ]
    if not requests:
        requests = [
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
            },
        ]
    return {
        'template': {
            'name': 'child1 clone',
            'description': 'test description',
            'params': [
                {
                    'name': 'base template parameter1',
                    'inherited': True,
                    'type': 'string',
                },
                {
                    'name': 'base template parameter2',
                    'inherited': True,
                    'type': 'string',
                },
                {'name': 'child1 template parameter1', 'type': 'number'},
            ],
            'items': items,
            'requests': requests,
            'base_template_id': '1ff4901c583745e089e55be0',
        },
        'params': [
            {'name': 'base template parameter1', 'value': 'base text'},
            {'name': 'child1 template parameter1', 'value': 1},
        ],
        'requests_params': [
            {'id': '5ff4901c583745e089e55bd3', 'name': 'req1'},
            {
                'id': '5d275bc3eb584657ebbf24b2',
                'name': 'req3',
                'substitutions': {'zone': 'moscow'},
            },
        ],
    }


def _unsaved_template_properties_items(name: str, properties=None) -> dict:
    items = copy.copy(common.PROPERTIES_ITEMS)

    if properties:
        copied_item = copy.copy(items[0])
        copied_item['properties'] = properties
        items = [copied_item] + items[:1]
    return {
        'template': {
            'name': name,
            'description': 'description',
            'params': common.CONTENT_ITEMS_PARAMS_IN_TEMPLATE,
            'items': items,
            'requests': common.CONTENT_ITEMS_REQUESTS,
        },
        'params': common.PROPERTIES_ITEMS_PARAMS,
        'requests_params': common.CONTENT_ITEMS_REQUESTS_PARAMS,
    }


def _unsaved_template_nested_items(name: str) -> dict:

    return {
        'template': {
            'name': name,
            'description': 'test description',
            'params': common.LIST_PROPERTIES_ITEMS_PARAMS_IN_TEMPLATE,
            'items': common.LIST_PROPERTIES_ITEMS,
            'requests': common.CONTENT_ITEMS_REQUESTS,
        },
        'params': common.LIST_PROPERTIES_ITEMS_PARAMS,
        'requests_params': common.CONTENT_ITEMS_REQUESTS_PARAMS,
    }


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            {'group_id': '000000000000000000000001', 'limit': 2},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': 'has group',
                        'group_id': '000000000000000000000001',
                        'id': '000000000000000000000003',
                        'name': 'has group',
                    },
                    {
                        'description': 'has sub group',
                        'group_id': '000000000000000000000002',
                        'id': '000000000000000000000004',
                        'name': 'has sub group',
                    },
                ],
                'limit': 2,
                'offset': 0,
                'total': 2,
            },
        ),
        (
            {
                'group_id': '000000000000000000000001',
                'limit': 1,
                'recursive': 'false',
            },
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': 'has group',
                        'group_id': '000000000000000000000001',
                        'id': '000000000000000000000003',
                        'name': 'has group',
                    },
                ],
                'limit': 1,
                'offset': 0,
                'total': 1,
            },
        ),
        (
            {'search_string': 'test', 'offset': 0, 'limit': 0},
            http.HTTPStatus.OK,
            {'items': [], 'limit': 0, 'offset': 0, 'total': 1},
        ),
        (
            {'search_string': 'text', 'offset': 0, 'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': 'simple text',
                        'id': '5d27219b73f3b64036c0a03a',
                        'name': 'simple text',
                    },
                    {
                        'description': 'some text',
                        'id': '5ff4901c583745e089e55be1',
                        'name': 'test',
                    },
                    {
                        'description': 'some',
                        'id': '5ff4901c583745e089e55be2',
                        'name': 'text',
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 3,
            },
        ),
        (
            {'search_string': 'reSt', 'offset': 1, 'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': 'frost',
                        'id': '5ff4901c583745e089e55be3',
                        'name': 'Rest',
                    },
                ],
                'limit': 10,
                'offset': 1,
                'total': 2,
            },
        ),
        (
            {'search_string': 'reSt', 'offset': 0, 'limit': 1},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': 'rEsT cost',
                        'id': '5ff4901c583745e089e55be4',
                        'name': 'most',
                    },
                ],
                'limit': 1,
                'offset': 0,
                'total': 2,
            },
        ),
        (
            {'search_string': 'OST', 'offset': 1, 'limit': 1},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': 'frost',
                        'id': '5ff4901c583745e089e55be3',
                        'name': 'Rest',
                    },
                ],
                'limit': 1,
                'offset': 1,
                'total': 3,
            },
        ),
        (
            {'search_string': '', 'limit': 12},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': '111111111111111111111111',
                        'id': '111111111111111111111111',
                        'name': '111111111111111111111111',
                    },
                    {
                        'description': 'base template',
                        'id': '1ff4901c583745e089e55be0',
                        'name': 'base',
                    },
                    {
                        'description': 'child1 template',
                        'id': '1ff4901c583745e089e55be1',
                        'name': 'child1',
                    },
                    {
                        'description': 'child1s child1 template',
                        'id': '1ff4901c583745e089e55be3',
                        'name': 'child11',
                    },
                    {
                        'description': 'child2 template',
                        'id': '1ff4901c583745e089e55be2',
                        'name': 'child2',
                    },
                    {
                        'description': 'empty template',
                        'id': '5ff4901c583745e089e55ba4',
                        'name': 'empty template',
                    },
                    {
                        'description': 'has document',
                        'id': '000000000000000000000002',
                        'name': 'has document',
                    },
                    {
                        'description': 'has group',
                        'group_id': '000000000000000000000001',
                        'id': '000000000000000000000003',
                        'name': 'has group',
                    },
                    {
                        'description': 'has no dependency',
                        'id': '000000000000000000000001',
                        'name': 'has no dependency',
                    },
                    {
                        'description': 'has sub group',
                        'group_id': '000000000000000000000002',
                        'id': '000000000000000000000004',
                        'name': 'has sub group',
                    },
                    {
                        'description': 'iterable item',
                        'id': '000000000000000000000022',
                        'name': 'iterable item',
                    },
                    {
                        'description': 'rEsT cost',
                        'id': '5ff4901c583745e089e55be4',
                        'name': 'most',
                    },
                ],
                'limit': 12,
                'offset': 0,
                'total': 23,
            },
        ),
        (
            {'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': '111111111111111111111111',
                        'id': '111111111111111111111111',
                        'name': '111111111111111111111111',
                    },
                    {
                        'description': 'base template',
                        'id': '1ff4901c583745e089e55be0',
                        'name': 'base',
                    },
                    {
                        'description': 'child1 template',
                        'id': '1ff4901c583745e089e55be1',
                        'name': 'child1',
                    },
                    {
                        'description': 'child1s child1 template',
                        'id': '1ff4901c583745e089e55be3',
                        'name': 'child11',
                    },
                    {
                        'description': 'child2 template',
                        'id': '1ff4901c583745e089e55be2',
                        'name': 'child2',
                    },
                    {
                        'description': 'empty template',
                        'id': '5ff4901c583745e089e55ba4',
                        'name': 'empty template',
                    },
                    {
                        'description': 'has document',
                        'id': '000000000000000000000002',
                        'name': 'has document',
                    },
                    {
                        'description': 'has group',
                        'group_id': '000000000000000000000001',
                        'id': '000000000000000000000003',
                        'name': 'has group',
                    },
                    {
                        'description': 'has no dependency',
                        'id': '000000000000000000000001',
                        'name': 'has no dependency',
                    },
                    {
                        'description': 'has sub group',
                        'group_id': '000000000000000000000002',
                        'id': '000000000000000000000004',
                        'name': 'has sub group',
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 23,
            },
        ),
    ],
)
async def test_templates(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.get(
        '/v1/templates/', params=query, headers=headers,
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content


@pytest.mark.parametrize(
    'body, expected_status, expected_content',
    [
        (
            {
                'template': {
                    'name': 'name',
                    'description': 'test',
                    'items': [
                        {
                            'custom_item_id': 'ITERABLE',
                            'params': [
                                {
                                    'name': '#iterable-header',
                                    'type': 'string',
                                    'value': 'header\n',
                                    'data_usage': 'OWN_DATA',
                                },
                                {
                                    'name': '#iterable-footer',
                                    'type': 'string',
                                    'value': '\nfooter',
                                    'data_usage': 'OWN_DATA',
                                },
                                {
                                    'name': '#items',
                                    'type': 'array',
                                    'value': ['first', 'second', 'third'],
                                    'data_usage': 'OWN_DATA',
                                },
                                {
                                    'name': '#items-separator',
                                    'value': '\n',
                                    'type': 'string',
                                    'data_usage': 'OWN_DATA',
                                },
                            ],
                            'items': [
                                {
                                    'content': (
                                        '<span data-variable="#item-index"/>)'
                                        '<span data-variable="#item"/>-'
                                        '<span data-variable="#now"/>'
                                    ),
                                },
                            ],
                        },
                    ],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.OK,
            'header\n'
            '1)first-2020-03-05T07:00:00+00:00\n'
            '2)second-2020-03-05T07:00:00+00:00\n'
            '3)third-2020-03-05T07:00:00+00:00\n'
            'footer',
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'description': 'test',
                    'items': [
                        {
                            'custom_item_id': 'ITERABLE',
                            'params': [
                                {
                                    'name': '#iterable-header',
                                    'type': 'string',
                                    'value': 'header\n',
                                    'data_usage': 'OWN_DATA',
                                },
                                {
                                    'name': '#iterable-footer',
                                    'type': 'string',
                                    'value': '\nfooter',
                                    'data_usage': 'OWN_DATA',
                                },
                                {
                                    'name': '#items',
                                    'type': 'array',
                                    'value': [],
                                    'data_usage': 'OWN_DATA',
                                },
                                {
                                    'name': '#items-separator',
                                    'value': '\n',
                                    'type': 'string',
                                    'data_usage': 'OWN_DATA',
                                },
                            ],
                            'items': [
                                {
                                    'content': (
                                        '<span data-variable="#item-index"/>)'
                                        '<span data-variable="#item"/>-'
                                        '<span data-variable="#now"/>'
                                    ),
                                },
                            ],
                        },
                    ],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.OK,
            '',
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'description': 'test',
                    'items': [
                        {
                            'content': (
                                '[inner template]'
                                '<span '
                                'data-template-item-id='
                                '"000000000000000000000005"'
                                '/>'
                            ),
                            'items': [
                                {
                                    'id': '000000000000000000000005',
                                    'template_id': '000000000000000000000001',
                                },
                            ],
                        },
                    ],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.OK,
            '[inner template]---1---1.1',
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'description': 'test',
                    'items': [
                        {
                            'content': (
                                '[inner template]'
                                '<span '
                                'data-template-item-id='
                                '"000000000000000000000005"'
                                '/>'
                            ),
                            'items': [
                                {
                                    'id': '000000000000000000000001',
                                    'template_id': '000000000000000000000001',
                                },
                            ],
                        },
                    ],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'CONTENT_HAS_INVALID_ID',
                'details': {
                    'content': (
                        '[inner template]<span '
                        'data-template-item-id="000000000000000000000005"/>'
                    ),
                    'message': (
                        'Item id "000000000000000000000005" does not exist in '
                        'items'
                    ),
                },
                'message': 'Content has invalid id',
            },
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'enumerators': [
                        {
                            'name': 'sub_main',
                            'parent_name': 'main',
                            'formatter': {
                                'code': 'ARABIC_NUMBER',
                                'start_symbol': '1',
                            },
                        },
                        {
                            'name': 'main',
                            'formatter': {
                                'code': 'ARABIC_NUMBER',
                                'start_symbol': '2',
                            },
                        },
                    ],
                    'description': 'test',
                    'items': [
                        {
                            'content': (
                                '<span data-enumerator="main"/>'
                                '[inner template]('
                                '<span '
                                'data-template-item-id='
                                '"000000000000000000000003"/>)'
                                '<span data-enumerator="main"/>'
                            ),
                            'items': [
                                {
                                    'id': '000000000000000000000003',
                                    'template_id': '000000000000000000000001',
                                    'enumerators': [
                                        {
                                            'name': 'base',
                                            'template_enumerator_name': 'main',
                                        },
                                        {
                                            'name': 'sub_base',
                                            'template_enumerator_name': (
                                                'sub_main'
                                            ),
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.OK,
            '2[inner template](---3---3.1)4',
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'enumerators': [
                        {
                            'name': 'main',
                            'formatter': {
                                'code': 'ARABIC_NUMBER',
                                'start_symbol': '1',
                            },
                        },
                        {
                            'name': 'sub_main',
                            'parent_name': 'main',
                            'formatter': {
                                'code': 'ARABIC_NUMBER',
                                'start_symbol': '1',
                                'separator': '/',
                                'pattern': 'Image {value}.',
                            },
                        },
                        {
                            'name': 'sub_sub_main',
                            'parent_name': 'sub_main',
                            'formatter': {
                                'code': 'ARABIC_NUMBER',
                                'start_symbol': '1',
                                'separator': '-',
                            },
                        },
                    ],
                    'description': 'test',
                    'items': [
                        {'content': '<span data-enumerator="main"/>\n'},
                        {'content': '<span data-enumerator="sub_main"/>\n'},
                        {
                            'content': (
                                '<span data-enumerator="sub_sub_main"/>\n'
                            ),
                        },
                        {
                            'enumerators': [
                                {
                                    'name': 'base',
                                    'template_enumerator_name': 'main',
                                },
                            ],
                            'template_id': '000000000000000000000001',
                        },
                    ],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.OK,
            '1\nImage 1/1.\n1/1-1\n---2---2.1',
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'enumerators': [
                        {
                            'name': 'main',
                            'formatter': {
                                'code': 'ARABIC_NUMBER',
                                'start_symbol': '1',
                            },
                        },
                        {
                            'name': 'sub',
                            'parent_name': 'main',
                            'formatter': {
                                'code': 'ARABIC_NUMBER',
                                'start_symbol': '1',
                            },
                        },
                        {
                            'name': 'sub_sub',
                            'formatter': {
                                'code': 'LOWER_CASE_ENGLISH_LETTER',
                                'show_parents': False,
                                'start_symbol': 'a',
                            },
                            'parent_name': 'sub',
                        },
                    ],
                    'description': 'test',
                    'items': [
                        {
                            'content': (
                                '<span data-enumerator="main"/>-'
                                '<span data-enumerator="main"/>-'
                                '<span data-enumerator="sub"/>-'
                                '<span data-enumerator="sub"/>-'
                                '<span data-enumerator="sub_sub"/>-'
                                '<span data-enumerator="sub_sub"/>-'
                                '<span data-enumerator="main"/>-'
                                '<span data-enumerator="sub"/>-'
                                '<span data-enumerator="sub"/>-'
                                '<span data-enumerator="sub_sub"/>'
                            ),
                        },
                    ],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.OK,
            '1-2-2.1-2.2-a-b-3-3.1-3.2-a',
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'base_template_id': '000000000000000000000001',
                    'description': 'test',
                    'items': [
                        {'content': '<span data-enumerator="base"/>'},
                        {'id': '999999999999999999999999', 'inherited': True},
                    ],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.OK,
            '1---2---2.1',
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'enumerators': [
                        {
                            'name': 'main',
                            'formatter': {
                                'code': 'ARABIC_NUMBER',
                                'pattern': 'Text {value}.',
                                'start_symbol': '1',
                            },
                        },
                    ],
                    'description': 'test',
                    'items': [
                        {'content': '<span data-enumerator="main"/> data1. '},
                        {'content': '<span data-enumerator="main"/> data2'},
                    ],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.OK,
            'Text 1. data1. Text 2. data2',
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'enumerators': [
                        {
                            'name': 'sub_base',
                            'formatter': {
                                'code': 'LOWER_CASE_ENGLISH_LETTER',
                                'show_parents': False,
                                'start_symbol': 'a',
                            },
                            'parent_name': 'base',
                        },
                    ],
                    'base_template_id': '000000000000000000000001',
                    'description': 'test',
                    'items': [
                        {'content': '<span data-enumerator="base"/>'},
                        {'id': '999999999999999999999999', 'inherited': True},
                    ],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.OK,
            '1---2---a',
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'description': 'test',
                    'items': [
                        {
                            'enumerators': [
                                {
                                    'name': 'test',
                                    'template_enumerator_name': 'invalid_path',
                                },
                            ],
                            'template_id': '999999999999999999999999',
                        },
                    ],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'ENUMERATOR_NOT_FOUND',
                'details': {'name': 'invalid_path'},
                'message': (
                    'the template does not have enumerator: "invalid_path"'
                ),
            },
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'description': 'test',
                    'enumerators': [
                        {
                            'name': 'sub_base',
                            'formatter': {
                                'code': 'LOWER_CASE_ENGLISH_LETTER',
                                'start_symbol': 'a',
                            },
                            'parent_name': 'base',
                        },
                    ],
                    'items': [],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'ENUMERATOR_NOT_FOUND',
                'details': {'name': 'base'},
                'message': 'the template does not have enumerator: "base"',
            },
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'description': 'test',
                    'items': [{'content': '<span data-enumerator="main"/>'}],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'ENUMERATOR_NOT_FOUND',
                'details': {'name': 'main'},
                'message': 'the template does not have enumerator: "main"',
            },
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'enumerators': [
                        {
                            'name': 'base',
                            'formatter': {
                                'code': 'LOWER_CASE_ENGLISH_LETTER',
                                'start_symbol': '1',
                            },
                        },
                    ],
                    'description': 'test',
                    'items': [],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_START_SYMBOL',
                'details': {},
                'message': (
                    'Invalid start symbols. '
                    'Got: "1". Start symbol must contains only '
                    '"abcdefghijklmnopqrstuvwxyz"'
                ),
            },
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'description': 'test',
                    'items': [
                        {
                            'custom_item_id': 'ITERABLE',
                            'params': [
                                {
                                    'name': '#items',
                                    'data_usage': 'OWN_DATA',
                                    'type': 'array',
                                    'value': [1, 2, 3],
                                },
                                {
                                    'name': '#items-separator',
                                    'data_usage': 'OWN_DATA',
                                    'type': 'string',
                                    'value': ' ',
                                },
                            ],
                            'items': [{'content': 'content'}],
                        },
                    ],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.OK,
            'content content content',
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'description': 'test',
                    'items': [
                        {
                            'custom_item_id': 'ITERABLE',
                            'params': [
                                {
                                    'name': '#items',
                                    'data_usage': 'OWN_DATA',
                                    'type': 'array',
                                    'value': [1, 2, 3],
                                },
                                {
                                    'name': '#items-separator',
                                    'data_usage': 'OWN_DATA',
                                    'type': 'array',
                                    'value': ['invalid type separator'],
                                },
                            ],
                            'items': [{'content': 'content'}],
                        },
                    ],
                    'params': [],
                    'requests': [],
                },
                'requests_params': [],
                'params': [],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_TYPE_MATCHING_FAILED',
                'details': {
                    'param_name': 'separator',
                    'template_name': 'name',
                },
                'message': (
                    'Data type matching failed. '
                    'Need: "string". Got: "[\'invalid type separator\']".'
                ),
            },
        ),
        (_unsaved_template(), http.HTTPStatus.OK, common.GENERATED_TEXT),
        # generate child1 template analog
        (
            _unsaved_inherited_content_items(),
            http.HTTPStatus.OK,
            common.CHILD1_GENERATED_TEXT,
        ),
        # generate child1 template analog with another secuence of requests
        (
            _unsaved_inherited_content_items(
                None,
                [
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
                    },
                    {
                        'id': '5ff4901c583745e089e55bd3',
                        'name': 'req1',
                        'enabled': True,
                        'inherited': True,
                    },
                ],
            ),
            http.HTTPStatus.OK,
            common.CHILD1_GENERATED_TEXT,
        ),
        # try generate child1 template analog with wrong secuence of items
        (
            _unsaved_inherited_content_items(
                [
                    {
                        'id': '1ff4901c583745e089e55ba2',
                        'content': common.BASE_ITEM2_CONTENT,
                        'enabled': False,
                        'inherited': True,
                    },
                    {
                        'id': '1ff4901c583745e089e55ba1',
                        'content': common.BASE_ITEM1_CONTENT,
                        'enabled': True,
                        'inherited': True,
                    },
                    {'content': common.CHILD1_ITEM3_CONTENT, 'enabled': True},
                ],
            ),
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'BASE_AND_INHERITED_TEMPLATE_FIELDS_DO_NOT_MATCH',
                'details': {},
                'message': (
                    'Base and inherited template fields '
                    '"template_items" do not match.'
                ),
            },
        ),
        (
            _unsaved_template(
                {
                    'name': 'n',
                    'description': 'd',
                    'type': 'string',
                    'data_usage': 'PARENT_TEMPLATE_DATA',
                    # params value (value_path) is empty
                    'value': '',
                },
            ),
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_RECURSIVE_GETTING_FAILED',
                'details': {
                    'data': {
                        '#now': '2020-03-05T07:00:00+00:00',
                        '#today': '2020-03-05T00:00:00+00:00',
                        '#tomorrow': '2020-03-06T00:00:00+00:00',
                        '#yesterday': '2020-03-04T00:00:00+00:00',
                        'template parameter1': {
                            'v1': 'str1',
                            'v2': 0,
                            'v3': True,
                            'v4': {'v4v1': [0, 1, 2], 'v4v2': 42},
                        },
                        'template parameter2': [2, 1, 0],
                        'template parameter3': 'some string',
                        'template parameter4': 100500,
                        'template parameter5': True,
                    },
                    'value_path': [''],
                    'template_name': 'name',
                },
                'message': 'Data recursive getting failed.',
            },
        ),
        (
            _unsaved_template(
                {
                    'name': 'n',
                    'description': 'd',
                    'type': 'string',
                    'data_usage': 'PARENT_TEMPLATE_DATA',
                    # params value (value_path) has unfound path
                    'value': 'tp',
                },
            ),
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_RECURSIVE_GETTING_FAILED',
                'details': {
                    'data': {
                        '#now': '2020-03-05T07:00:00+00:00',
                        '#today': '2020-03-05T00:00:00+00:00',
                        '#tomorrow': '2020-03-06T00:00:00+00:00',
                        '#yesterday': '2020-03-04T00:00:00+00:00',
                        'template parameter1': {
                            'v1': 'str1',
                            'v2': 0,
                            'v3': True,
                            'v4': {'v4v1': [0, 1, 2], 'v4v2': 42},
                        },
                        'template parameter2': [2, 1, 0],
                        'template parameter3': 'some string',
                        'template parameter4': 100500,
                        'template parameter5': True,
                    },
                    'value_path': ['tp'],
                    'template_name': 'name',
                },
                'message': 'Data recursive getting failed.',
            },
        ),
        (
            _unsaved_template(
                {
                    'name': 'n',
                    'description': 'd',
                    # 'template parameter2' is array
                    'type': 'number',
                    'data_usage': 'PARENT_TEMPLATE_DATA',
                    'value': 'template parameter2',
                },
            ),
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_TYPE_MATCHING_FAILED',
                'details': {'param_name': 'n', 'template_name': 'name'},
                'message': (
                    'Data type matching failed. Need: "number". '
                    'Got: "[2, 1, 0]".'
                ),
            },
        ),
        (
            _unsaved_template(
                {
                    'name': 'n',
                    'description': 'd',
                    'type': 'string',
                    'data_usage': 'SERVER_DATA',
                    # params value (value_path) is empty
                    'value': '',
                },
            ),
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_RECURSIVE_GETTING_FAILED',
                'details': {
                    'data': {
                        'req1': {
                            'r1': (
                                'body: {\'a\': {\'b\': [], \'c\': 1}}; '
                                'queries: '
                                'q1=1, q2=string'
                            ),
                        },
                        'req2': {'arr': [1, 2, 3]},
                        'req3': {'bool': False, 'num': 10.0},
                    },
                    'value_path': [''],
                    'template_name': 'name',
                },
                'message': 'Data recursive getting failed.',
            },
        ),
        (
            _unsaved_template(
                {
                    'name': 'n',
                    'description': 'd',
                    'type': 'string',
                    'data_usage': 'SERVER_DATA',
                    # params value (value_path) has unfound path
                    'value': 'tp',
                },
            ),
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_RECURSIVE_GETTING_FAILED',
                'details': {
                    'data': {
                        'req1': {
                            'r1': (
                                'body: {\'a\': {\'b\': [], \'c\': 1}}; '
                                'queries: '
                                'q1=1, q2=string'
                            ),
                        },
                        'req2': {'arr': [1, 2, 3]},
                        'req3': {'bool': False, 'num': 10.0},
                    },
                    'value_path': ['tp'],
                    'template_name': 'name',
                },
                'message': 'Data recursive getting failed.',
            },
        ),
        (
            _unsaved_template(
                {
                    'name': 'n',
                    'description': 'd',
                    # 'req2.arr' is array
                    'type': 'number',
                    'data_usage': 'SERVER_DATA',
                    'value': 'req2.arr',
                },
            ),
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_TYPE_MATCHING_FAILED',
                'details': {'param_name': 'n', 'template_name': 'name'},
                'message': (
                    'Data type matching failed. Need: "number". '
                    'Got: "[1, 2, 3]".'
                ),
            },
        ),
        (
            {
                'template': {
                    'name': 'test',
                    'description': 'test',
                    'items': [{'template_id': '5ff4901c583745e089e55be1'}],
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'PARAMETERS_NOT_FILLED',
                'details': {
                    'template_id': '5ff4901c583745e089e55be1',
                    'template_name': 'test',
                },
                'message': (
                    'Not all request_params filled. Got: []. '
                    'Need: [\'req1\', \'req2\', \'req3\'].'
                ),
            },
        ),
        (
            _unsaved_template(
                {
                    'name': 'n',
                    'description': 'd',
                    'type': 'number',
                    'data_usage': 'PARENT_TEMPLATE_DATA',
                    # template parameter1.v1 is not dict
                    'value': 'template parameter1.v1.v2',
                },
            ),
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_RECURSIVE_GETTING_FAILED',
                'details': {
                    'data': 'str1',
                    'value_path': ['template parameter1', 'v1', 'v2'],
                    'template_name': 'name',
                },
                'message': 'Data recursive getting failed.',
            },
        ),
        (
            _unsaved_template(
                {
                    'name': 'n',
                    'description': 'd',
                    'type': 'number',
                    'data_usage': 'PARENT_TEMPLATE_DATA',
                    # template parameter1.v1 has not v5
                    'value': 'template parameter1.v4.v5',
                },
            ),
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_RECURSIVE_GETTING_FAILED',
                'details': {
                    'data': {'v4v1': [0, 1, 2], 'v4v2': 42},
                    'value_path': ['template parameter1', 'v4', 'v5'],
                    'template_name': 'name',
                },
                'message': 'Data recursive getting failed.',
            },
        ),
    ],
)
@pytest.mark.usefixtures('requests_handlers')
@pytest.mark.config(**common.REQUEST_CONFIG)
@pytest.mark.now('2020-03-05T10:00:00.00')
async def test_generate_preview(
        api_app_client, body, expected_status, expected_content,
):
    headers = {'X-Yandex-Login': 'test_name'}
    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    if expected_status == http.HTTPStatus.OK:
        assert content['generated_text'] == expected_content
    else:
        assert content == expected_content


@pytest.mark.parametrize(
    'body, expected_status, expected_content',
    (
        (
            {
                'template': {
                    'name': 'name',
                    'description': 'test',
                    'items': [
                        {
                            'template_id': '000000000000000000000002',
                            'params': [
                                {
                                    'name': 'param',
                                    'type': 'number',
                                    'data_usage': 'CALCULATED',
                                    'value': {
                                        'operator': 'MUL',
                                        'left': {
                                            'value': 2,
                                            'type': 'number',
                                            'data_usage': 'OWN_DATA',
                                        },
                                        'right': {
                                            'value': 5,
                                            'type': 'number',
                                            'data_usage': 'OWN_DATA',
                                        },
                                    },
                                },
                            ],
                            'requests_params': [
                                {
                                    'name': 'request',
                                    'id': '5ff4901c583745e089e55bd3',
                                },
                            ],
                        },
                    ],
                    'requests_params': [
                        {'name': 'request', 'id': '5ff4901c583745e089e55bd3'},
                    ],
                },
                'requests_params': [
                    {'name': 'request', 'id': '5ff4901c583745e089e55bd3'},
                ],
                'params': [],
            },
            http.HTTPStatus.OK,
            '---1---1.1; param=10',
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'description': 'test',
                    'items': [
                        {
                            'template_id': '000000000000000000000002',
                            'params': [
                                {
                                    'name': 'param',
                                    'type': 'string',
                                    'data_usage': 'CALCULATED',
                                    'value': {
                                        'operator': 'ADD',
                                        'left': {
                                            'value': 'first-word',
                                            'type': 'string',
                                            'data_usage': 'OWN_DATA',
                                        },
                                        'right': {
                                            'value': '-second-word',
                                            'type': 'string',
                                            'data_usage': 'OWN_DATA',
                                        },
                                    },
                                },
                            ],
                            'requests_params': [
                                {
                                    'name': 'request',
                                    'id': '5ff4901c583745e089e55bd3',
                                },
                            ],
                        },
                    ],
                    'requests_params': [
                        {'name': 'request', 'id': '5ff4901c583745e089e55bd3'},
                    ],
                },
                'requests_params': [
                    {'name': 'request', 'id': '5ff4901c583745e089e55bd3'},
                ],
                'params': [],
            },
            http.HTTPStatus.OK,
            '---1---1.1; param=first-word-second-word',
        ),
        (
            {
                'template': {
                    'name': 'name',
                    'description': 'test',
                    'items': [
                        {
                            'template_id': '000000000000000000000002',
                            'params': [
                                {
                                    'name': 'param',
                                    'type': 'number',
                                    'data_usage': 'CALCULATED',
                                    'value': {
                                        'operator': 'ADD',
                                        'left': {
                                            'value': 'word',
                                            'type': 'string',
                                            'data_usage': 'OWN_DATA',
                                        },
                                        'right': {
                                            'value': 1,
                                            'type': 'number',
                                            'data_usage': 'OWN_DATA',
                                        },
                                    },
                                },
                            ],
                            'requests_params': [
                                {
                                    'name': 'request',
                                    'id': '5ff4901c583745e089e55bd3',
                                },
                            ],
                        },
                    ],
                    'requests_params': [
                        {'name': 'request', 'id': '5ff4901c583745e089e55bd3'},
                    ],
                },
                'requests_params': [
                    {'name': 'request', 'id': '5ff4901c583745e089e55bd3'},
                ],
                'params': [],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'UNSUPPORTED_OPERATOR',
                'details': {
                    'left': 'word',
                    'operator': 'ADD',
                    'right': '1',
                    'template_name': 'name',
                },
                'message': 'Unsupported operator "ADD" for \'word\' and 1',
            },
        ),
    ),
)
@pytest.mark.usefixtures('requests_handlers')
@pytest.mark.config(**common.REQUEST_CONFIG)
async def test_generate_with_dynamic_parameter(
        api_app_client, body, expected_status, expected_content,
):
    headers = {'X-Yandex-Login': 'robot'}

    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    if expected_status == http.HTTPStatus.OK:
        assert content['generated_text'] == expected_content
    else:
        assert content == expected_content


@pytest.mark.parametrize(
    'request_response, expected_content',
    (
        ({'items': []}, ''),
        ({'items': [{'value': '1'}]}, '1'),
        ({'items': [{'value': 'test'}, {'value': ''}]}, 'test'),
    ),
)
@pytest.mark.config(**common.REQUEST_CONFIG)
async def test_generate_iterable_preview(
        api_app_client, request_response, expected_content, mockserver,
):
    @mockserver.json_handler('/get_surge/')
    def _req1(request):
        return request_response

    headers = {'X-Yandex-Login': 'test_name'}
    body = {
        'template': {
            'name': 'iterable',
            'description': 'iterable',
            'requests': [
                {
                    'name': 'surge',
                    'id': '5ff4901c583745e089e55bd3',
                    'enabled': True,
                },
            ],
            'items': [
                {
                    'template_id': '000000000000000000000022',
                    'params': [
                        {
                            'name': 'items',
                            'type': 'array',
                            'value': 'surge.items',
                            'data_usage': 'SERVER_DATA',
                        },
                        {
                            'name': 'items-separator',
                            'type': 'string',
                            'value': ',',
                            'data_usage': 'OWN_DATA',
                        },
                    ],
                },
            ],
        },
        'requests_params': [
            {'name': 'surge', 'id': '5ff4901c583745e089e55bd3'},
        ],
    }
    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.json()
    assert response.status == http.HTTPStatus.OK, content
    assert content['generated_text'] == expected_content, content


@pytest.mark.config(**common.REQUEST_CONFIG)
async def test_generate_preview_cache_request(api_app_client, mockserver):
    value = 0

    @mockserver.json_handler('/pinstats/')
    def handler_mock(request):
        nonlocal value
        value += 1
        return {'value': value}

    body = {
        'template': {
            'name': 'name',
            'description': 'test',
            'items': [
                {
                    'content': (
                        '<span data-variable="req1.value" data-request-id="">'
                        '</span>'
                        '<span data-variable="req2.value" data-request-id="">'
                        '</span>'
                    ),
                    'params': [],
                },
            ],
            'params': [],
            'requests': [
                {
                    'id': '5ff4901c583745e089e55bd2',
                    'name': 'req1',
                    'enabled': True,
                },
                {
                    'id': '5ff4901c583745e089e55bd2',
                    'name': 'req2',
                    'enabled': True,
                },
            ],
        },
        'requests_params': [
            {'name': 'req1', 'id': '5ff4901c583745e089e55bd2'},
            {'name': 'req2', 'id': '5ff4901c583745e089e55bd2'},
        ],
        'params': [],
    }

    headers = {'X-Yandex-Login': 'test_name'}
    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.json()

    assert response.status == http.HTTPStatus.OK, content
    assert content['generated_text'] == '11'
    assert handler_mock.times_called == 1


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        # only one document generated based on this template
        (
            {'template_id': '5ff4901c583745e089e55be1'},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'name': 'test',
                        'description': 'some text',
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'id': '5ff4901c583745e089e55bf1',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'venimaster',
                    },
                ],
                'total': 1,
            },
        ),
        # one document generated based on this template and another one based
        # on template containing this one in template items
        (
            {'template_id': '5ff4901c583745e089e55be2'},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'name': 'test',
                        'description': 'some text',
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'id': '5ff4901c583745e089e55bf1',
                        'modified_by': 'venimaster',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                    },
                    {
                        'name': 'text',
                        'description': 'some',
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'id': '5ff4901c583745e089e55bf2',
                        'modified_by': 'russhakirov',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                    },
                ],
                'total': 2,
            },
        ),
        # dependencies of base template
        (
            {'template_id': '1ff4901c583745e089e55be0'},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'name': 'n11',
                        'description': 'generated based on child11 template',
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'id': '1ff4901c583745e089e55bf0',
                        'modified_by': 'russhakirov',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                    },
                ],
                'total': 1,
            },
        ),
        (
            {'template_id': '5ff4901c583745e089e55be6'},  # no dependencies
            http.HTTPStatus.OK,
            {'items': [], 'total': 0},
        ),
        # not existing template_id
        (
            {'template_id': '5ff4901c583745e089e55be9'},
            http.HTTPStatus.OK,
            {'items': [], 'total': 0},
        ),
        (
            {},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'template_id is required parameter'},
                'message': 'Some parameters are invalid',
            },
        ),
    ],
)
async def test_get_dependent_documents(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.get(
        '/v1/templates/dependent_documents/', params=query, headers=headers,
    )
    assert response.status == expected_status, await response.json()
    content = await response.json()
    if expected_status == http.HTTPStatus.OK:
        assert content['total'] == expected_content['total']
        items = sorted(content['items'], key=lambda item: item['id'])
        expected_items = expected_content['items']
        assert len(items) == len(expected_items)
        for item, expected_item in zip(items, expected_items):
            assert item == expected_item
    else:
        assert content == expected_content


async def test_template_in_db():
    context = web_context.Context()
    await context.on_startup()

    data = await context.pg.master.fetch(
        'SELECT id, dependencies FROM document_templator.templates',
    )
    dependency_map = {i['id']: i['dependencies'] or set() for i in data}

    repository = template_repository.TemplateRepository(context, None)
    templates = [
        await repository.get_template(template_id)
        for template_id in dependency_map.keys()
    ]
    for template in templates:
        dependency = sorted(dependency_map[template.id_])
        assert dependency == sorted(template.get_dependencies()), template.id_
