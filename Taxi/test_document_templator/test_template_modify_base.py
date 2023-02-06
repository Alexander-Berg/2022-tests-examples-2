# noqa  # pylint: disable=C0302
import datetime
import http
from unittest import mock

import pytest

from document_templator.generated.api import web_context
from test_document_templator import common

MODIFIED_AT = datetime.datetime(day=1, month=1, year=2019)


async def _load_inherited_templates(pg_document_templator):
    ids = [
        '1ff4901c583745e089e55be1',
        '1ff4901c583745e089e55be2',
        '1ff4901c583745e089e55be3',
    ]
    templates = await pg_document_templator.master.fetch(
        'SELECT * FROM document_templator.templates WHERE id = ANY($1);', ids,
    )
    return sorted(templates, key=lambda template: template['id'])


@pytest.mark.parametrize(
    'body, expected_status',
    [
        (
            {
                'name': 'n',
                'description': 'd',
                'params': [
                    {
                        'name': 'base template parameter1',
                        'description': 'd',
                        'type': 'number',
                        'enabled': False,
                        'inherited': False,
                    },
                    {
                        'name': 'base template parameter2',
                        'description': 'd',
                        'type': 'array',
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'items': [
                    {
                        'id': '1ff4901c583745e089e55ba1',
                        'content': '',
                        'enabled': False,
                        'inherited': False,
                    },
                    {
                        'id': '1ff4901c583745e089e55ba2',
                        'content': '',
                        'enabled': True,
                        'inherited': False,
                    },
                ],
                'requests': [
                    {
                        'id': '5ff4901c583745e089e55bd1',
                        'name': 'req1',
                        'enabled': False,
                        'inherited': False,
                    },
                    {
                        'id': '5ff4901c583745e089e55bd3',
                        'name': 'req2',
                        'enabled': True,
                        'inherited': False,
                    },
                ],
            },
            http.HTTPStatus.OK,
        ),
    ],
)
async def test_put_base_template_non_modifying_children(
        api_app_client, body, expected_status,
):
    context = web_context.Context()
    await context.on_startup()
    inherited_templates = await _load_inherited_templates(context.pg)
    response = await api_app_client.put(
        '/v1/template/',
        params={'id': '1ff4901c583745e089e55be0', 'version': 0},
        json=body,
        headers={'X-Yandex-Login': 'russhakirov'},
    )
    assert response.status == expected_status, await response.text()
    if expected_status == http.HTTPStatus.OK:
        updated_inherited_templates = await _load_inherited_templates(
            context.pg,
        )
        assert inherited_templates == updated_inherited_templates


@pytest.mark.parametrize(
    'body, modified_ids, expected_status, expected_content',
    [
        pytest.param(
            {
                'name': 'n',
                'description': 'd',
                'params': [
                    {
                        'name': 'child11 template parameter1',
                        'description': 'base template parameter1 description',
                        'type': 'string',
                        'enabled': True,
                        'inherited': False,
                    },
                ],
            },
            {'1ff4901c583745e089e55be1'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'BASE_AND_INHERITED_TEMPLATE_FIELDS_DO_NOT_MATCH',
                'details': {},
                'message': (
                    'Base and inherited template '
                    'fields "params" do not match.'
                ),
            },
            id='invalid_params',
        ),
        pytest.param(
            {
                'name': 'n',
                'description': 'd',
                'requests': [
                    {
                        'id': '5d275bc3eb584657ebbf24b1',
                        'name': 'req3',
                        'enabled': True,
                        'inherited': False,
                    },
                ],
            },
            {},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'BASE_AND_INHERITED_TEMPLATE_FIELDS_DO_NOT_MATCH',
                'details': {},
                'message': (
                    'Base and inherited template fields '
                    '"requests" do not match.'
                ),
            },
            id='invalid_requests',
        ),
    ],
)
async def test_put_base_template_with_children_params(
        api_app_client, body, modified_ids, expected_status, expected_content,
):
    context = web_context.Context()
    await context.on_startup()

    inherited_templates = await _load_inherited_templates(context.pg)
    response = await api_app_client.put(
        '/v1/template/',
        params={'id': '1ff4901c583745e089e55be0', 'version': 0},
        json=body,
        headers={'X-Yandex-Login': 'russhakirov'},
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content
    updated_inherited_templates = await _load_inherited_templates(context.pg)
    assert updated_inherited_templates == inherited_templates


def get_base_item1(inherited: bool, enabled: bool):
    return {
        'id': '1ff4901c583745e089e55ba1',
        'content': common.BASE_ITEM1_CONTENT,
        'enabled': enabled,
        'inherited': inherited,
    }


def get_base_item2(inherited: bool, enabled: bool):
    return {
        'id': '1ff4901c583745e089e55ba2',
        'content': common.BASE_ITEM2_CONTENT,
        'enabled': enabled,
        'inherited': inherited,
    }


def get_new_item(id_: str, inherited: bool):
    return {'content': id_, 'enabled': True, 'id': id_, 'inherited': inherited}


def get_child1_item(inherited=False):
    return {
        'content': common.CHILD1_ITEM3_CONTENT,
        'enabled': True,
        'id': '1ff4901c583745e089e55ba3',
        'inherited': inherited,
    }


def get_child_of_child_item(inherited: bool):
    return {
        'content': common.CHILD11_ITEM3_CONTENT,
        'enabled': True,
        'id': '1ff4901c583745e089e55ba5',
        'inherited': inherited,
    }


def get_child2_item():
    return {
        'content': common.CHILD2_ITEM3_CONTENT,
        'enabled': True,
        'id': '1ff4901c583745e089e55ba4',
        'inherited': False,
    }


def get_base_parameter1(inherited: bool, enabled: bool):
    return {
        'name': 'base template parameter1',
        'description': 'base template parameter1 description',
        'type': 'string',
        'enabled': enabled,
        'inherited': inherited,
    }


def get_new_parameter(inherited: bool, enabled: bool):
    return {
        'name': 'new',
        'description': 'new',
        'type': 'string',
        'enabled': enabled,
        'inherited': inherited,
    }


def get_base_parameter2(inherited: bool, enabled: bool):
    return {
        'name': 'base template parameter2',
        'description': 'base template ' 'parameter2 description',
        'type': 'string',
        'enabled': enabled,
        'inherited': inherited,
    }


def get_child1_parameter(inherited=False):
    return {
        'description': 'child1 template parameter1 description',
        'enabled': True,
        'inherited': inherited,
        'name': 'child1 template parameter1',
        'type': 'number',
    }


def get_child_of_child_parameter():
    return {
        'description': 'child11 template parameter1 description',
        'enabled': True,
        'inherited': False,
        'name': 'child11 template parameter1',
        'type': 'string',
    }


def get_child1_request(inherited: bool):
    return {
        'enabled': True,
        'id': '5d275bc3eb584657ebbf24b2',
        'inherited': inherited,
        'name': 'req3',
    }


def get_base_request1(inherited: bool, enabled: bool):
    return {
        'id': '5ff4901c583745e089e55bd3',
        'name': 'req1',
        'enabled': enabled,
        'inherited': inherited,
    }


def get_base_request2(inherited: bool, enabled: bool):
    return {
        'id': '5ff4901c583745e089e55bd1',
        'name': 'req2',
        'enabled': enabled,
        'inherited': inherited,
    }


def get_new_request(inherited: bool):
    return {
        'enabled': True,
        'id': '5ff4901c583745e089e55bd1',
        'inherited': inherited,
        'name': 'new_request',
    }


def get_child1():
    return {
        'base_template_id': '1ff4901c583745e089e55be0',
        'created_at': '2018-07-01T00:00:00+03:00',
        'created_by': 'venimaster',
        'description': 'child1 template',
        'id': '1ff4901c583745e089e55be1',
        'modified_at': '2019-01-01T03:00:00+03:00',
        'modified_by': 'russhakirov',
        'name': 'child1',
        'version': 1,
    }


def get_child2():
    return {
        'base_template_id': '1ff4901c583745e089e55be0',
        'created_at': '2018-07-01T00:00:00+03:00',
        'created_by': 'venimaster',
        'description': 'child2 template',
        'id': '1ff4901c583745e089e55be2',
        'modified_at': '2019-01-01T03:00:00+03:00',
        'modified_by': 'russhakirov',
        'name': 'child2',
        'version': 1,
    }


def get_child_of_child():
    return {
        'base_template_id': '1ff4901c583745e089e55be1',
        'created_at': '2018-07-01T00:00:00+03:00',
        'created_by': 'venimaster',
        'description': 'child1s child1 template',
        'id': '1ff4901c583745e089e55be3',
        'modified_at': '2019-01-01T03:00:00+03:00',
        'modified_by': 'russhakirov',
        'name': 'child11',
        'version': 1,
    }


@pytest.mark.parametrize(
    'body, expected_data_list, expected_status',
    [
        pytest.param(
            {'name': 'n', 'description': 'd'},
            [
                {
                    **get_child1(),
                    'items': [get_child1_item()],
                    'params': [get_child1_parameter(False)],
                    'requests': [get_child1_request(False)],
                },
                {**get_child2(), 'items': [get_child2_item()]},
                {
                    **get_child_of_child(),
                    'items': [
                        get_child_of_child_item(False),
                        get_child1_item(True),
                    ],
                    'params': [
                        get_child1_parameter(True),
                        get_child_of_child_parameter(),
                    ],
                    'requests': [get_child1_request(True)],
                },
            ],
            http.HTTPStatus.OK,
            id='remove all base items/params/requests',
        ),
        pytest.param(
            {
                'name': 'n',
                'description': 'd',
                'params': [
                    get_base_parameter1(False, True),
                    get_base_parameter2(False, False),
                ],
                'items': [
                    get_new_item('3' * 24, False),
                    get_base_item1(False, True),
                    get_new_item('4' * 24, False),
                    get_base_item2(False, False),
                    get_new_item('5' * 24, False),
                ],
                'requests': [
                    get_base_request1(False, True),
                    get_base_request2(False, False),
                    get_new_request(False),
                ],
            },
            [
                {
                    **get_child1(),
                    'items': [
                        get_child1_item(),
                        get_new_item('3' * 24, True),
                        get_base_item1(True, True),
                        get_new_item('4' * 24, True),
                        get_base_item2(True, False),
                        get_new_item('5' * 24, True),
                    ],
                    'params': [
                        get_base_parameter1(True, True),
                        get_base_parameter2(True, False),
                        get_child1_parameter(False),
                    ],
                    'requests': [
                        get_base_request1(True, True),
                        get_base_request2(True, False),
                        get_child1_request(False),
                        get_new_request(True),
                    ],
                },
                {
                    **get_child2(),
                    'items': [
                        get_child2_item(),
                        get_new_item('3' * 24, True),
                        get_base_item1(True, False),
                        get_new_item('4' * 24, True),
                        get_base_item2(True, True),
                        get_new_item('5' * 24, True),
                    ],
                    'params': [
                        get_base_parameter1(True, False),
                        get_base_parameter2(True, True),
                    ],
                    'requests': [
                        get_base_request1(True, False),
                        get_base_request2(True, True),
                        get_new_request(True),
                    ],
                },
                {
                    **get_child_of_child(),
                    'items': [
                        get_child_of_child_item(False),
                        get_child1_item(True),
                        get_new_item('3' * 24, True),
                        get_base_item1(True, True),
                        get_new_item('4' * 24, True),
                        get_base_item2(True, False),
                        get_new_item('5' * 24, True),
                    ],
                    'params': [
                        get_base_parameter1(True, True),
                        get_base_parameter2(True, False),
                        get_child1_parameter(True),
                        get_child_of_child_parameter(),
                    ],
                    'requests': [
                        get_base_request1(True, True),
                        get_base_request2(True, False),
                        get_child1_request(True),
                        get_new_request(True),
                    ],
                },
            ],
            http.HTTPStatus.OK,
            id='insert items between base ones',
        ),
        pytest.param(
            {
                'name': 'n',
                'description': 'd',
                'params': [
                    get_base_parameter1(False, True),
                    get_base_parameter2(False, False),
                    get_new_parameter(False, True),
                ],
                'items': [
                    get_base_item1(False, True),
                    get_base_item2(False, False),
                ],
                'requests': [
                    get_base_request1(False, True),
                    get_base_request2(False, False),
                ],
            },
            [
                {
                    **get_child1(),
                    'items': [
                        get_base_item1(True, True),
                        get_base_item2(True, False),
                        get_child1_item(False),
                    ],
                    'params': [
                        get_base_parameter1(True, True),
                        get_base_parameter2(True, False),
                        get_child1_parameter(False),
                        get_new_parameter(True, True),
                    ],
                    'requests': [
                        get_base_request1(True, True),
                        get_base_request2(True, False),
                        get_child1_request(False),
                    ],
                },
                {
                    **get_child2(),
                    'items': [
                        get_base_item1(True, False),
                        get_base_item2(True, True),
                        get_child2_item(),
                    ],
                    'params': [
                        get_base_parameter1(True, False),
                        get_base_parameter2(True, True),
                        get_new_parameter(True, True),
                    ],
                    'requests': [
                        get_base_request1(True, False),
                        get_base_request2(True, True),
                    ],
                },
                {
                    **get_child_of_child(),
                    'items': [
                        get_base_item1(True, True),
                        get_base_item2(True, False),
                        get_child_of_child_item(False),
                        get_child1_item(True),
                    ],
                    'params': [
                        get_base_parameter1(True, True),
                        get_base_parameter2(True, False),
                        get_child1_parameter(True),
                        get_child_of_child_parameter(),
                        get_new_parameter(True, True),
                    ],
                    'requests': [
                        get_base_request1(True, True),
                        get_base_request2(True, False),
                        get_child1_request(True),
                    ],
                },
            ],
            http.HTTPStatus.OK,
            id='insert params',
        ),
        pytest.param(
            {
                'name': 'n',
                'description': 'd',
                'items': [
                    get_base_item2(False, False),
                    get_base_item1(False, True),
                ],
            },
            [
                {
                    **get_child1(),
                    'items': [
                        get_base_item2(True, False),
                        get_child1_item(),
                        get_base_item1(True, True),
                    ],
                    'params': [get_child1_parameter(False)],
                    'requests': [get_child1_request(False)],
                },
                {
                    **get_child2(),
                    'items': [
                        get_base_item2(True, True),
                        get_child2_item(),
                        get_base_item1(True, False),
                    ],
                },
                {
                    **get_child_of_child(),
                    'items': [
                        get_base_item2(True, False),
                        get_child_of_child_item(False),
                        get_child1_item(True),
                        get_base_item1(True, True),
                    ],
                    'params': [
                        get_child1_parameter(True),
                        get_child_of_child_parameter(),
                    ],
                    'requests': [get_child1_request(True)],
                },
            ],
            http.HTTPStatus.OK,
            id='swap base items',
        ),
    ],
)
async def test_put_base_template_modifying_children(
        api_app_client, body, expected_status, expected_data_list,
):
    with mock.patch(
            'document_templator.models.template.generate_item_persistent_id',
    ) as generate_item_id_mock:
        generate_item_id_mock.side_effect = ['3' * 24, '4' * 24, '5' * 24]
        with mock.patch('datetime.datetime.utcnow', return_value=MODIFIED_AT):
            response = await api_app_client.put(
                '/v1/template/',
                params={'id': '1ff4901c583745e089e55be0', 'version': 0},
                json=body,
                headers={'X-Yandex-Login': 'russhakirov'},
            )
    assert response.status == expected_status, await response.json()
    responses = []
    for expected_data in expected_data_list:
        response = await api_app_client.get(
            '/v1/template/', params={'id': expected_data['id']},
        )
        responses.append(await response.json())
    assert responses == expected_data_list
