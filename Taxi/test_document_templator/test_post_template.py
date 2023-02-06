import datetime
import http
from unittest import mock

import pytest

from test_document_templator import common
from test_document_templator import test_template

NEW_TEMPLATE_ID = '7' * 24
NEW_ITEM_ID_1 = '2' * 24
NEW_ITEM_ID_2 = '3' * 24
NEW_ITEM_ID_3 = '4' * 24


@pytest.mark.parametrize(
    'body, headers, expected_status, expected_content',
    [
        (
            {
                'name': 'name',
                'description': 'test',
                'items': [
                    {
                        'template': {
                            'name': 'String Provider',
                            'description': 'String Provider',
                            'requests': [],
                            'params': [
                                {
                                    'name': 'param',
                                    'type': 'string',
                                    'inherited': False,
                                    'enabled': True,
                                },
                            ],
                            'items': [
                                {
                                    'id': '5e73d2599519e9df383de392',
                                    'content': '<a data-variable="param"/>',
                                    'inherited': False,
                                    'enabled': True,
                                },
                            ],
                        },
                        'params': [
                            {
                                'name': 'param',
                                'type': 'string',
                                'data_usage': 'OWN_DATA',
                                'value': 'param_value',
                            },
                        ],
                        'custom_item_id': 'INNER_TEMPLATE',
                    },
                ],
            },
            {'X-Yandex-Login': 'robot'},
            http.HTTPStatus.OK,
            {
                'created_at': '2019-01-01T03:00:00+03:00',
                'created_by': 'robot',
                'description': 'test',
                'id': NEW_TEMPLATE_ID,
                'items': [
                    {
                        'custom_item_id': 'INNER_TEMPLATE',
                        'enabled': True,
                        'id': '222222222222222222222222',
                        'inherited': False,
                        'params': [
                            {
                                'data_usage': 'OWN_DATA',
                                'name': 'param',
                                'type': 'string',
                                'value': 'param_value',
                            },
                        ],
                        'template': {
                            'description': 'String Provider',
                            'items': [
                                {
                                    'content': '<a data-variable="param"/>',
                                    'enabled': True,
                                    'id': '5e73d2599519e9df383de392',
                                    'inherited': False,
                                },
                            ],
                            'name': 'String Provider',
                            'params': [
                                {
                                    'enabled': True,
                                    'inherited': False,
                                    'name': 'param',
                                    'type': 'string',
                                },
                            ],
                        },
                    },
                ],
                'modified_at': '2019-01-01T03:00:00+03:00',
                'modified_by': 'robot',
                'name': 'name',
                'version': 0,
            },
        ),
        (
            {
                'name': 'with enumerators in base',
                'description': 'description',
                'base_template_id': '000000000000000000000002',
                'items': [
                    {
                        'id': '999999999999999999999990',
                        'enabled': True,
                        'inherited': True,
                    },
                ],
                'params': [
                    {
                        'name': 'param',
                        'type': 'string',
                        'enabled': True,
                        'inherited': True,
                    },
                ],
                'requests': [
                    {
                        'name': 'request',
                        'id': '5ff4901c583745e089e55bd3',
                        'enabled': True,
                        'inherited': True,
                    },
                ],
            },
            {'X-Yandex-Login': 'robot'},
            http.HTTPStatus.OK,
            {
                'base_enumerators': [
                    {
                        'formatter': {
                            'code': 'ARABIC_NUMBER',
                            'pattern': '{value}',
                            'separator': '.',
                            'show_parents': True,
                            'start_symbol': '1',
                        },
                        'name': 'common',
                    },
                    {
                        'formatter': {
                            'code': 'ARABIC_NUMBER',
                            'pattern': '{value}',
                            'separator': '.',
                            'show_parents': True,
                            'start_symbol': '1',
                        },
                        'name': 'base',
                    },
                    {
                        'formatter': {
                            'code': 'ARABIC_NUMBER',
                            'pattern': '{value}',
                            'separator': '.',
                            'show_parents': True,
                            'start_symbol': '1',
                        },
                        'name': 'sub_base',
                        'parent_name': 'base',
                    },
                ],
                'base_template_id': '000000000000000000000002',
                'created_at': '2019-01-01T03:00:00+03:00',
                'created_by': 'robot',
                'description': 'description',
                'id': NEW_TEMPLATE_ID,
                'items': [
                    {
                        'content': (
                            '---<span data-enumerator="base"/>---<span '
                            'data-enumerator="sub_base"/>; param=<span '
                            'data-variable="param"/>'
                        ),
                        'description': 'test',
                        'enabled': True,
                        'id': '999999999999999999999990',
                        'inherited': True,
                    },
                ],
                'modified_at': '2019-01-01T03:00:00+03:00',
                'modified_by': 'robot',
                'name': 'with enumerators in base',
                'params': [
                    {
                        'enabled': True,
                        'inherited': True,
                        'name': 'param',
                        'schema': {'type': 'number'},
                        'type': 'number',
                    },
                ],
                'requests': [
                    {
                        'enabled': True,
                        'id': '5ff4901c583745e089e55bd3',
                        'inherited': True,
                        'name': 'request',
                    },
                ],
                'version': 0,
            },
        ),
        # minimal template
        (
            {
                'description': 'test',
                'name': 'test Andrey',
                'params': [
                    {
                        'enabled': True,
                        'type': 'object',
                        'schema': {
                            'obj': {
                                'type': 'object',
                                'properties': {'param1': {'type': 'string'}},
                            },
                        },
                        'name': 'obj',
                    },
                ],
                'items': [
                    {
                        'params': [
                            {
                                'name': '#item',
                                'data_usage': 'CALCULATED',
                                'type': 'string',
                                'description': '#item',
                                'value': {
                                    'left': {
                                        'data_usage': 'PARENT_TEMPLATE_DATA',
                                        'type': 'string',
                                        'value': 'obj.param1',
                                    },
                                    'operator': 'ADD',
                                    'right': {
                                        'data_usage': 'PARENT_TEMPLATE_DATA',
                                        'type': 'string',
                                        'value': 'obj.param1',
                                    },
                                },
                            },
                        ],
                        'custom_item_id': 'CONDITIONAL',
                        'items': [
                            {
                                'content': (
                                    'Test&nbsp;'
                                    '<span style="color: Coral;" '
                                    'data-variable="obj.param1">'
                                    '</span>'
                                ),
                                'enabled': True,
                            },
                        ],
                        'else_items': [
                            {
                                'content': (
                                    'Test&nbsp;'
                                    '<span style="color: Coral;" '
                                    'data-variable="obj.param2">'
                                    '</span>'
                                ),
                                'enabled': True,
                            },
                        ],
                        'enabled': True,
                        'properties': {
                            'filter_groups': [
                                {
                                    'filter': {
                                        'reference_value': '#item',
                                        'condition': 'equal',
                                        'value': 'param1Value',
                                    },
                                },
                            ],
                        },
                    },
                ],
            },
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.OK,
            {
                'created_at': '2019-01-01T03:00:00+03:00',
                'created_by': 'venimaster',
                'description': 'test',
                'id': NEW_TEMPLATE_ID,
                'items': [
                    {
                        'enabled': True,
                        'id': NEW_ITEM_ID_1,
                        'inherited': False,
                        'items': [
                            {
                                'content': (
                                    'Test&nbsp;<span style="color: Coral;" '
                                    'data-variable="obj.param1"></span>'
                                ),
                                'enabled': True,
                                'id': NEW_ITEM_ID_2,
                                'inherited': False,
                            },
                        ],
                        'else_items': [
                            {
                                'content': (
                                    'Test&nbsp;<span style="color: Coral;" '
                                    'data-variable="obj.param2"></span>'
                                ),
                                'enabled': True,
                                'id': NEW_ITEM_ID_3,
                                'inherited': False,
                            },
                        ],
                        'params': [
                            {
                                'data_usage': 'CALCULATED',
                                'description': '#item',
                                'name': '#item',
                                'type': 'string',
                                'value': {
                                    'left': {
                                        'data_usage': 'PARENT_TEMPLATE_DATA',
                                        'type': 'string',
                                        'value': 'obj.param1',
                                    },
                                    'operator': 'ADD',
                                    'right': {
                                        'data_usage': 'PARENT_TEMPLATE_DATA',
                                        'type': 'string',
                                        'value': 'obj.param1',
                                    },
                                },
                            },
                        ],
                        'custom_item_id': 'CONDITIONAL',
                        'properties': {
                            'filter_groups': [
                                {
                                    'filter': {
                                        'condition': 'equal',
                                        'reference_value': '#item',
                                        'value': 'param1Value',
                                    },
                                },
                            ],
                        },
                    },
                ],
                'modified_at': '2019-01-01T03:00:00+03:00',
                'modified_by': 'venimaster',
                'name': 'test Andrey',
                'params': [
                    {
                        'enabled': True,
                        'inherited': False,
                        'name': 'obj',
                        'schema': {
                            'obj': {
                                'properties': {'param1': {'type': 'string'}},
                                'type': 'object',
                            },
                        },
                        'type': 'object',
                    },
                ],
                'version': 0,
            },
        ),
        (
            {
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
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.OK,
            {
                'created_at': '2019-01-01T03:00:00+03:00',
                'created_by': 'venimaster',
                'description': 'test',
                'id': NEW_TEMPLATE_ID,
                'items': [
                    {
                        'content': (
                            '[inner template]<span '
                            'data-template-item-id='
                            '"000000000000000000000005"/>'
                        ),
                        'enabled': True,
                        'id': '222222222222222222222222',
                        'inherited': False,
                        'items': [
                            {
                                'enabled': True,
                                'id': '000000000000000000000005',
                                'inherited': False,
                                'template_id': '000000000000000000000001',
                            },
                        ],
                    },
                ],
                'modified_at': '2019-01-01T03:00:00+03:00',
                'modified_by': 'venimaster',
                'name': 'name',
                'version': 0,
            },
        ),
        (
            {'name': 'ghost', 'description': 'some text'},
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.OK,
            {
                'name': 'ghost',
                'version': 0,
                'description': 'some text',
                'created_by': 'venimaster',
                'created_at': '2019-01-01T03:00:00+03:00',
                'id': NEW_TEMPLATE_ID,
                'modified_by': 'venimaster',
                'modified_at': '2019-01-01T03:00:00+03:00',
            },
        ),
        (
            {
                'name': 'ghost',
                'description': 'some text',
                'group_id': '000000000000000000000001',
            },
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.OK,
            {
                'name': 'ghost',
                'version': 0,
                'description': 'some text',
                'group_id': '000000000000000000000001',
                'created_by': 'venimaster',
                'created_at': '2019-01-01T03:00:00+03:00',
                'id': NEW_TEMPLATE_ID,
                'modified_by': 'venimaster',
                'modified_at': '2019-01-01T03:00:00+03:00',
            },
        ),
        # minimal items/requests/params
        (
            {
                'name': 'n',
                'description': 'd',
                'params': [{'name': 'p', 'type': 'number', 'enabled': True}],
                'requests': [
                    {
                        'id': '5ff4901c583745e089e55bd1',
                        'name': 'r',
                        'enabled': True,
                    },
                ],
                'items': [{'enabled': True}],
            },
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.OK,
            {
                'name': 'n',
                'version': 0,
                'description': 'd',
                'params': [
                    {
                        'name': 'p',
                        'type': 'number',
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'requests': [
                    {
                        'id': '5ff4901c583745e089e55bd1',
                        'name': 'r',
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'items': [
                    {'enabled': True, 'inherited': False, 'id': NEW_ITEM_ID_1},
                ],
                'created_by': 'venimaster',
                'modified_by': 'venimaster',
                'modified_at': '2019-01-01T03:00:00+03:00',
                'created_at': '2019-01-01T03:00:00+03:00',
                'id': NEW_TEMPLATE_ID,
            },
        ),
        # create child1 template analog
        (
            test_template.inherited_template(),
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.OK,
            test_template.inherited_template_output(),
        ),
        # valid change in items order
        (
            test_template.inherited_template(
                [
                    test_template.ITEM_1_IN,
                    test_template.ITEM_3_IN,
                    test_template.ITEM_2_IN,
                ],
            ),
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.OK,
            test_template.inherited_template_output(
                [
                    common.ITEM_1_RESPONSE,
                    test_template.ITEM_3_OUT,
                    common.ITEM_2_RESPONSE,
                ],
            ),
        ),
        # change in child requests order
        (
            test_template.inherited_template(
                None,
                [
                    test_template.REQUEST_1_IN,
                    test_template.REQUEST_3_IN,
                    test_template.REQUEST_2_IN,
                ],
            ),
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.OK,
            test_template.inherited_template_output(
                None,
                [
                    test_template.REQUEST_1_OUT,
                    test_template.REQUEST_3_OUT,
                    test_template.REQUEST_2_OUT,
                ],
            ),
        ),
        # change in child params order
        (
            test_template.inherited_template(
                None,
                None,
                [
                    test_template.PARAM_1_IN,
                    test_template.PARAM_3_IN,
                    test_template.PARAM_2_IN,
                ],
            ),
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.OK,
            test_template.inherited_template_output(
                None,
                None,
                [
                    test_template.PARAM_1_OUT,
                    common.PARAM_3_RESPONSE,
                    test_template.PARAM_2_OUT,
                ],
            ),
        ),
        (
            {
                'name': 'name',
                'description': 'test',
                'items': [{'content': '<span data-enumerator="invalid"/>'}],
                'params': [],
                'requests': [],
            },
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'ENUMERATOR_NOT_FOUND',
                'details': {'name': 'invalid'},
                'message': 'the template does not have enumerator: "invalid"',
            },
        ),
        (
            {
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
            {'X-Yandex-Login': 'venimaster'},
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
                'name': 'name',
                'description': 'test',
                'enumerators': [
                    {
                        'name': 'test',
                        'formatter': {
                            'code': 'LOWER_CASE_ENGLISH_LETTER',
                            'start_symbol': 'a',
                        },
                    },
                ],
                'items': [
                    {
                        'enumerators': [
                            {
                                'name': 'test',
                                'template_enumerator_name': 'test',
                            },
                            {
                                'name': 'test',
                                'template_enumerator_name': 'test',
                            },
                        ],
                        'template_id': '999999999999999999999999',
                    },
                ],
                'params': [],
                'requests': [],
            },
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'ITEM_ENUMERATORS_NAMES_COLLIDED',
                'details': {},
                'message': 'Enumerators names in item collided.',
            },
        ),
        (
            {
                'name': 'name',
                'description': 'test',
                'enumerators': [
                    {
                        'name': 'test',
                        'formatter': {'code': 'INVALID', 'start_symbol': 'a'},
                    },
                ],
                'items': [],
                'params': [],
                'requests': [],
            },
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for code: \'INVALID\' must be one of '
                        '[\'ARABIC_NUMBER\', \'LOWER_CASE_ENGLISH_LETTER\', '
                        '\'UPPER_CASE_ENGLISH_LETTER\', '
                        '\'LOWER_CASE_RUSSIAN_LETTER\', '
                        '\'UPPER_CASE_RUSSIAN_LETTER\']'
                    ),
                },
                'message': 'Some parameters are invalid',
            },
        ),
        (
            {
                'name': 'name',
                'description': 'test',
                'enumerators': [
                    {
                        'name': 'test',
                        'formatter': {
                            'code': 'ARABIC_NUMBER',
                            'pattern': 'invalid pattern',
                            'start_symbol': '1',
                        },
                    },
                ],
                'items': [],
                'params': [],
                'requests': [],
            },
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for pattern: '
                        '\'invalid pattern\' must match '
                        'r\'^[^{}]*{value}[^{}]*$\''
                    ),
                },
                'message': 'Some parameters are invalid',
            },
        ),
        (
            {
                'name': 'name',
                'description': 'test',
                'enumerators': [
                    {
                        'name': 'test',
                        'formatter': {
                            'code': 'ARABIC_NUMBER',
                            'start_symbol': 'a',
                        },
                    },
                ],
                'items': [],
                'params': [],
                'requests': [],
            },
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_START_SYMBOL',
                'details': {},
                'message': (
                    'Invalid start symbols. '
                    'Got: "a". Start symbol must contains only '
                    '"0123456789"'
                ),
            },
        ),
        (
            {
                'name': 'name',
                'description': 'test',
                'enumerators': [
                    {
                        'name': 'test',
                        'formatter': {
                            'code': 'LOWER_CASE_ENGLISH_LETTER',
                            'start_symbol': 'a',
                        },
                    },
                    {
                        'name': 'test',
                        'formatter': {
                            'code': 'LOWER_CASE_ENGLISH_LETTER',
                            'start_symbol': 'a',
                        },
                    },
                ],
                'items': [],
                'params': [],
                'requests': [],
            },
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'ENUMERATORS_NAMES_COLLIDED',
                'details': {},
                'message': 'Enumerators names collided.',
            },
        ),
        (
            {
                'name': 'name',
                'description': 'test',
                'enumerators': [
                    {
                        'name': 'first',
                        'parent_name': 'third',
                        'formatter': {
                            'code': 'LOWER_CASE_ENGLISH_LETTER',
                            'start_symbol': 'a',
                        },
                    },
                    {
                        'name': 'second',
                        'parent_name': 'first',
                        'formatter': {
                            'code': 'LOWER_CASE_ENGLISH_LETTER',
                            'start_symbol': 'a',
                        },
                    },
                    {
                        'name': 'third',
                        'parent_name': 'second',
                        'formatter': {
                            'code': 'LOWER_CASE_ENGLISH_LETTER',
                            'start_symbol': 'a',
                        },
                    },
                ],
            },
            {'X-Yandex-Login': 'robot'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'CIRCULAR_DEPENDENCY_IN_ENUMERATOR',
                'details': {},
                'message': 'the enumerator can not be descendant of itself',
            },
        ),
        (
            {
                'name': 'ghost',
                'description': 'some text',
                'group_id': '000000000000000000000000',
            },
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'GROUP_NOT_FOUND',
                'details': {},
                'message': 'Group with id=000000000000000000000000 not found',
            },
        ),
        # invalid change in base items order
        (
            test_template.inherited_template(
                [
                    test_template.ITEM_2_IN,
                    test_template.ITEM_1_IN,
                    test_template.ITEM_3_IN,
                ],
            ),
            {'X-Yandex-Login': 'venimaster'},
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
        # not all base items
        (
            test_template.inherited_template(
                [test_template.ITEM_1_IN, test_template.ITEM_3_IN],
            ),
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'BASE_AND_INHERITED_TEMPLATE_FIELDS_DO_NOT_MATCH',
                'details': {},
                'message': (
                    'Base and inherited '
                    'template fields "template_items" do not match.'
                ),
            },
        ),
        # not all base requests
        (
            test_template.inherited_template(
                None, [test_template.REQUEST_1_IN, test_template.REQUEST_3_IN],
            ),
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'BASE_AND_INHERITED_TEMPLATE_FIELDS_DO_NOT_MATCH',
                'details': {},
                'message': (
                    'Base and inherited template fields '
                    '"requests" do not match.'
                ),
            },
        ),
        # not all base params
        (
            test_template.inherited_template(
                None,
                None,
                [test_template.PARAM_1_IN, test_template.PARAM_3_IN],
            ),
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'BASE_AND_INHERITED_TEMPLATE_FIELDS_DO_NOT_MATCH',
                'details': {},
                'message': (
                    'Base and inherited template '
                    'fields "params" do not match.'
                ),
            },
        ),
        (
            {'name': 'test', 'description': 'some text'},
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'TEMPLATE_WITH_NAME_ALREADY_EXIST',
                'details': {},
                'message': 'template with name "test" already exists: ',
            },
        ),
        (
            {'name': 'test', 'description': 'some text'},
            {},  # yandex_login not specified
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'MISSING_LOGIN',
                'details': {},
                'message': 'X-Yandex-Login or login must be given',
            },
        ),
        (
            None,
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'body is required'},
                'message': 'Some parameters are invalid',
            },
        ),
    ],
)
async def test_post_template(
        api_app_client, body, headers, expected_status, expected_content,
):
    now = datetime.datetime(year=2019, day=1, month=1)
    with mock.patch(
            'document_templator.models.template.generate_template_id',
            return_value=NEW_TEMPLATE_ID,
    ):
        with mock.patch(
                'document_templator.models.template.'
                'generate_item_persistent_id',
        ) as generate_item_identifier_mock:
            generate_item_identifier_mock.side_effect = [
                NEW_ITEM_ID_1,
                NEW_ITEM_ID_2,
                NEW_ITEM_ID_3,
            ]
            with mock.patch('datetime.datetime.utcnow', return_value=now):
                response = await api_app_client.post(
                    '/v1/template/', json=body, headers=headers,
                )
    assert response.status == expected_status, await response.text()
    content = await response.json()
    assert content == expected_content

    if expected_status == http.HTTPStatus.OK:
        response_ = await api_app_client.get(
            '/v1/template/', params={'id': NEW_TEMPLATE_ID}, headers=headers,
        )
        context_get = await response_.json()
        assert context_get == expected_content
