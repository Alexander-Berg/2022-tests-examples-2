import datetime
import http
from typing import List
from typing import Optional
from unittest import mock

import pytest

from document_templator.generated.api import web_context
from test_document_templator import common

CSS_STYLE = (
    """
p {
color: red;
}

table {
width: 100%;
}
""".strip()
)
ITEM_1_IN = {
    'id': '1ff4901c583745e089e55ba1',
    'content': common.BASE_ITEM1_CONTENT,
    'enabled': True,
    'inherited': True,
}

ITEM_2_IN = {
    'id': '1ff4901c583745e089e55ba2',
    'content': common.BASE_ITEM2_CONTENT,
    'enabled': False,
    'inherited': True,
}

ITEM_3_IN = {'content': common.CHILD1_ITEM3_CONTENT, 'enabled': True}

REQUEST_1_IN = {
    'id': '5ff4901c583745e089e55bd3',
    'name': 'req1',
    'enabled': True,
    'inherited': True,
}

REQUEST_2_IN = {
    'id': '5ff4901c583745e089e55bd1',
    'name': 'req2',
    'enabled': False,
    'inherited': True,
}

REQUEST_3_IN = {
    'id': '5d275bc3eb584657ebbf24b2',
    'name': 'req3',
    'enabled': True,
}

PARAM_1_IN = {
    'name': 'base template parameter1',
    'description': 'base template parameter1 description',
    'type': 'string',
    'enabled': True,
    'inherited': True,
}

PARAM_2_IN = {
    'name': 'base template parameter2',
    'description': 'base template parameter2 description',
    'type': 'string',
    'enabled': False,
    'inherited': True,
}

PARAM_3_IN = {
    'name': 'child1 template parameter1',
    'description': 'child1 template parameter1 description',
    'type': 'number',
    'enabled': True,
}

ITEM_3_OUT = {
    'content': common.CHILD1_ITEM3_CONTENT,
    'id': '2' * 24,
    'enabled': True,
    'inherited': False,
}

REQUEST_1_OUT = {
    'id': '5ff4901c583745e089e55bd3',
    'name': 'req1',
    'enabled': True,
    'inherited': True,
}

REQUEST_2_OUT = {
    'id': '5ff4901c583745e089e55bd1',
    'name': 'req2',
    'enabled': False,
    'inherited': True,
}

REQUEST_3_OUT = {
    'id': '5d275bc3eb584657ebbf24b2',
    'name': 'req3',
    'enabled': True,
    'inherited': False,
}

PARAM_1_OUT = {
    'name': 'base template parameter1',
    'description': 'base template parameter1 description',
    'type': 'string',
    'enabled': True,
    'inherited': True,
}

PARAM_2_OUT = {
    'name': 'base template parameter2',
    'description': 'base template parameter2 description',
    'type': 'string',
    'enabled': False,
    'inherited': True,
}


def inherited_template(
        items: Optional[List[dict]] = None,
        requests: Optional[List[dict]] = None,
        params: Optional[List[dict]] = None,
) -> dict:
    if not items:
        items = [ITEM_1_IN, ITEM_2_IN, ITEM_3_IN]
    if not requests:
        requests = [REQUEST_1_IN, REQUEST_2_IN, REQUEST_3_IN]
    if not params:
        params = [PARAM_1_IN, PARAM_2_IN, PARAM_3_IN]
    return {
        'name': 'child1 clone',
        'description': 'd',
        'params': params,
        'items': items,
        'requests': requests,
        'base_template_id': '1ff4901c583745e089e55be0',
    }


def inherited_template_output(
        items: Optional[List[dict]] = None,
        requests: Optional[List[dict]] = None,
        params: Optional[List[dict]] = None,
) -> dict:
    if not items:
        items = [common.ITEM_1_RESPONSE, common.ITEM_2_RESPONSE, ITEM_3_OUT]
    if not requests:
        requests = [REQUEST_1_OUT, REQUEST_2_OUT, REQUEST_3_OUT]
    if not params:
        params = [PARAM_1_OUT, PARAM_2_OUT, common.PARAM_3_RESPONSE]
    return {
        'base_template_id': '1ff4901c583745e089e55be0',
        'version': 0,
        'name': 'child1 clone',
        'description': 'd',
        'params': params,
        'items': items,
        'requests': requests,
        'created_by': 'venimaster',
        'modified_by': 'venimaster',
        'modified_at': '2019-01-01T03:00:00+03:00',
        'created_at': '2019-01-01T03:00:00+03:00',
        'id': '7' * 24,
    }


def _inherited_template_modification_output(
        items: Optional[List[dict]] = None,
        requests: Optional[List[dict]] = None,
        params: Optional[List[dict]] = None,
) -> dict:
    result = inherited_template_output(items, requests, params)
    result.update(
        {
            'created_at': '2018-07-01T00:00:00+03:00',
            'id': '5ff4901c583745e089e55be2',
            'version': 1,
            'modified_at': '2019-01-01T03:00:00+03:00',
        },
    )
    return result


@pytest.mark.parametrize(
    'query, body, headers, expected_status, expected_content, '
    'dependent_document_ids',
    [
        (
            {'id': '5ff4901c583745e089e55be1', 'version': 1},
            {
                'description': 'some text',
                'css_style': CSS_STYLE,
                'group_id': '000000000000000000000001',
                'items': [
                    {
                        'description': 'item1 description',
                        'enabled': True,
                        'id': '5ff4901c583745e089e55ba1',
                        'inherited': False,
                        'items': [
                            {
                                'description': 'item1 description',
                                'enabled': True,
                                'id': '5ff4901c583745e089e55ba3',
                                'inherited': False,
                                'params': [],
                                'template_id': '5ff4901c583745e089e55ba4',
                            },
                        ],
                        'params': [],
                        'requests_params': [],
                        'template_id': '5ff4901c583745e089e55be2',
                    },
                ],
                'name': 'test',
                'params': [],
                'requests': [],
            },
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.OK,
            {
                'created_at': '2018-07-01T00:00:00+03:00',
                'css_style': CSS_STYLE,
                'created_by': 'venimaster',
                'description': 'some text',
                'group_id': '000000000000000000000001',
                'id': '5ff4901c583745e089e55be1',
                'items': [
                    {
                        'description': 'item1 description',
                        'enabled': True,
                        'id': '5ff4901c583745e089e55ba1',
                        'inherited': False,
                        'items': [
                            {
                                'description': 'item1 description',
                                'enabled': True,
                                'id': '5ff4901c583745e089e55ba3',
                                'inherited': False,
                                'template_id': '5ff4901c583745e089e55ba4',
                            },
                        ],
                        'template_id': '5ff4901c583745e089e55be2',
                    },
                ],
                'modified_at': '2019-01-01T03:00:00+03:00',
                'modified_by': 'russhakirov',
                'name': 'test',
                'version': 2,
            },
            {'5ff4901c583745e089e55bf1'},
        ),
        (
            {'id': '5ff4901c583745e089e55be1', 'version': 1},
            {'name': 'ghost', 'description': 'some text'},
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.OK,
            {
                'name': 'ghost',
                'id': '5ff4901c583745e089e55be1',
                'version': 2,
                'description': 'some text',
                'created_at': '2018-07-01T00:00:00+03:00',
                'created_by': 'venimaster',
                'modified_by': 'russhakirov',
                'modified_at': '2019-01-01T03:00:00+03:00',
            },
            {'5ff4901c583745e089e55bf1'},
        ),
        # make uninherited template to be inherited one
        (
            {'id': '5ff4901c583745e089e55be2', 'version': 0},
            inherited_template(),
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.OK,
            _inherited_template_modification_output(),
            {'5ff4901c583745e089e55bf2', '5ff4901c583745e089e55bf1'},
        ),
        (
            {'id': '000000000000000000000001', 'version': 0},
            {
                'name': 'has no dependency',
                'description': 'some text',
                'enumerators': [
                    {
                        'name': 'changed_base',
                        'formatter': {
                            'code': 'ARABIC_NUMBER',
                            'start_symbol': '1',
                        },
                    },
                ],
                'items': [
                    {
                        'id': '999999999999999999999999',
                        'content': '<span data-enumerator="changed_base"/>',
                    },
                ],
            },
            {'X-Yandex-Login': 'robot'},
            http.HTTPStatus.OK,
            {
                'created_at': '2018-07-01T00:00:00+03:00',
                'created_by': 'yandex',
                'description': 'some text',
                'id': '000000000000000000000001',
                'items': [
                    {
                        'content': '<span data-enumerator="changed_base"/>',
                        'enabled': True,
                        'id': '999999999999999999999999',
                        'inherited': False,
                    },
                ],
                'modified_at': '2019-01-01T03:00:00+03:00',
                'modified_by': 'robot',
                'name': 'has no dependency',
                'enumerators': [
                    {
                        'formatter': {
                            'code': 'ARABIC_NUMBER',
                            'pattern': '{value}',
                            'separator': '.',
                            'start_symbol': '1',
                            'show_parents': True,
                        },
                        'name': 'changed_base',
                    },
                ],
                'version': 1,
            },
            set(),
        ),
        # make inherited template to be uninherited one
        (
            {'id': '1ff4901c583745e089e55be1', 'version': 0},
            {'name': 'ghost', 'description': 'some text'},
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.OK,
            {
                'name': 'ghost',
                'id': '1ff4901c583745e089e55be1',
                'version': 1,
                'description': 'some text',
                'created_at': '2018-07-01T00:00:00+03:00',
                'created_by': 'venimaster',
                'modified_by': 'russhakirov',
                'modified_at': '2019-01-01T03:00:00+03:00',
            },
            {'1ff4901c583745e089e55bf0'},
        ),
        (
            {'id': '5ff4901c583745e089e55be2', 'version': 0},
            {
                'name': 'test',  # there is template with same name already
                'description': 'some text',
            },
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'TEMPLATE_WITH_NAME_ALREADY_EXIST',
                'details': {},
                'message': 'template with name "test" already exists: ',
            },
            set(),
        ),
        (
            {'id': '000000000000000000000001', 'version': 0},
            {
                'name': 'has no dependency',
                'description': 'some text',
                'base_template_id': '000000000000000000000001',
                'items': [
                    {'id': '999999999999999999999999', 'inherited': True},
                ],
            },
            {'X-Yandex-Login': 'robot'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'CIRCULAR_DEPENDENCY_IN_TEMPLATE',
                'details': {},
                'message': (
                    'the template can not depend on templates '
                    'which depends on the template'
                ),
            },
            set(),
        ),
        (
            {'id': '000000000000000000000001', 'version': 0},
            {
                'name': 'has no dependency',
                'description': 'some text',
                'items': [{'template_id': '000000000000000000000001'}],
            },
            {'X-Yandex-Login': 'robot'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'CIRCULAR_DEPENDENCY_IN_TEMPLATE',
                'details': {},
                'message': (
                    'the template can not depend on templates '
                    'which depends on the template'
                ),
            },
            set(),
        ),
        (
            {'id': '5ff4901c583745e089e55be6', 'version': 0},
            {'name': 'test', 'description': 'some text'},
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'TEMPLATE_NOT_FOUND_ERROR',
                'details': {},
                'message': (
                    'template with id=5ff4901c583745e089e55be6 not found'
                ),
            },
            set(),
        ),
        (
            {'id': '5ff4901c583745e089e55be1', 'version': 2},
            {'name': 'test', 'description': 'some text'},
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'TEMPLATE_NOT_FOUND_ERROR',
                'details': {},
                'message': (
                    'template with id=5ff4901c583745e089e55be1 not found'
                ),
            },
            set(),
        ),
        (
            {'id': '5ff4901c583745e089e55be1', 'version': 1},
            {
                'name': 'ghost',
                'description': 'some text',
                'group_id': '000000000000000000000000',
            },
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'GROUP_NOT_FOUND',
                'details': {},
                'message': 'Group with id=000000000000000000000000 not found',
            },
            set(),
        ),
        (
            {'id': '1ff4901c583745e089e55be1', 'version': 0},
            {'name': 'ghost', 'description': 'some text'},
            {},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'MISSING_LOGIN',
                'details': {},
                'message': 'X-Yandex-Login or login must be given',
            },
            set(),
        ),
        (
            {'id': '5ff4901c583745e089e55be1'},
            {},
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'version is required parameter'},
                'message': 'Some parameters are invalid',
            },
            set(),
        ),
        (
            {'version': '0'},  # no id specified
            {},
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'id is required parameter'},
                'message': 'Some parameters are invalid',
            },
            set(),
        ),
        (
            {'id': '5ff4901c583745e089e55be1', 'version': 1},
            None,
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'body is required'},
                'message': 'Some parameters are invalid',
            },
            set(),
        ),
    ],
)
async def test_put_template(
        api_app_client,
        query,
        headers,
        body,
        expected_status,
        expected_content,
        dependent_document_ids,
):
    context = web_context.Context()
    await context.on_startup()
    now = datetime.datetime(year=2019, day=1, month=1)

    with mock.patch('datetime.datetime.utcnow', return_value=now):
        with mock.patch(
                'document_templator.models.template.'
                'generate_item_persistent_id',
                return_value='2' * 24,
        ):
            response = await api_app_client.put(
                '/v1/template/', params=query, json=body, headers=headers,
            )
    assert response.status == expected_status, await response.text()
    content = await response.json()
    assert content == expected_content

    if response.status == http.HTTPStatus.OK:
        response_get = await api_app_client.get(
            '/v1/template/', params=query, headers=headers,
        )
        assert await response_get.json() == content
    query = """
        SELECT count(*)
        FROM document_templator.dynamic_documents
        WHERE
            persistent_id = $1
            AND NOT removed
            AND outdated_at IS NOT NULL;
    """
    for document_id in dependent_document_ids:
        count = await context.pg.master.fetchval(query, document_id)
        assert count == 1, document_id
