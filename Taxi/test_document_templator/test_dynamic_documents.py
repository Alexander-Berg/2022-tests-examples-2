# pylint: disable=C0302
import http

import pytest

from test_document_templator import common


def update_data(
        name: str,
        description: str,
        template_id=None,
        params=None,
        requests_params=None,
) -> dict:
    if not requests_params:
        requests_params = common.REQUESTS_PARAMS
    if not template_id:
        template_id = '5ff4901c583745e089e55be1'
    return {
        'name': name,
        'description': description,
        'template_id': template_id,
        'params': params if params else common.PARAMS,
        'requests_params': requests_params,
    }


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            {'id': '5ff4901c583745e089e55bf1'},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'version': 1,
                        'name': 'test',
                        'description': 'some text',
                        'template_id': '5ff4901c583745e089e55be1',
                        'params': common.PARAMS,
                        'requests_params': common.REQUESTS_PARAMS,
                        'modified_by': 'venimaster',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'is_valid': True,
                    },
                    {
                        'version': 0,
                        'name': 'test',
                        'description': 'some text',
                        'template_id': '5ff4901c583745e089e55be1',
                        'params': [
                            {
                                'name': 'dynamic document parameter1',
                                'value': (
                                    'dynamic document ' 'parameter1 value'
                                ),
                            },
                            {
                                'name': 'dynamic document parameter2',
                                'value': 1,
                            },
                        ],
                        'modified_by': 'russhakirov',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'is_valid': True,
                    },
                ],
            },
        ),
        (
            {'id': '5ff4901c583745e089e55bf2'},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'version': 1,
                        'is_valid': True,
                        'name': 'text',
                        'description': 'some',
                        'template_id': '5ff4901c583745e089e55be2',
                        'modified_by': 'russhakirov',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                    },
                ],
            },
        ),
        (
            {'id': '5ff4901c583745e089e55bf6'},  # removed dynamic document
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=5ff4901c583745e089e55bf6 not found'
                ),
            },
        ),
        (
            {'id': '5ff4901c583745e089e55bf7'},  # missing dynamic document
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=5ff4901c583745e089e55bf7 not found'
                ),
            },
        ),
    ],
)
async def test_dynamic_documents_versions(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.get(
        '/v1/dynamic_documents/versions/', params=query, headers=headers,
    )
    assert response.status == expected_status, await response.text()
    content = await response.json()

    if expected_status == http.HTTPStatus.OK:
        items = content['items']
        expected_items = expected_content['items']
        assert items == expected_items
    else:
        assert content == expected_content


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            {'group_id': '000000000000000000000001', 'limit': 0},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'some text',
                        'generated_text': 'some generated text',
                        'group_id': '000000000000000000000001',
                        'id': '5ff4901c583745e089e55bf1',
                        'is_valid': True,
                        'modified_by': 'venimaster',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'name': 'test',
                        'outdated_at': '2018-07-02T01:00:00+03:00',
                        'template_id': '5ff4901c583745e089e55be1',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'generated based on child11 template',
                        'generated_text': '',
                        'group_id': '000000000000000000000001',
                        'id': '000009999988888777771111',
                        'is_valid': False,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'two last version is not valid',
                        'template_id': '111111111111111111111111',
                        'version': 4,
                    },
                ],
                'limit': 0,
                'offset': 0,
                'total': 2,
            },
        ),
        (
            {'search_string': 'test', 'offset': 0, 'limit': 0},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'some text',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf1',
                        'group_id': '000000000000000000000001',
                        'is_valid': True,
                        'modified_by': 'venimaster',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'name': 'test',
                        'outdated_at': '2018-07-02T01:00:00+03:00',
                        'template_id': '5ff4901c583745e089e55be1',
                        'version': 1,
                    },
                ],
                'limit': 0,
                'offset': 0,
                'total': 1,
            },
        ),
        (
            {'search_string': 'text', 'offset': 0, 'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'some text',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf1',
                        'group_id': '000000000000000000000001',
                        'is_valid': True,
                        'modified_by': 'venimaster',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'name': 'test',
                        'outdated_at': '2018-07-02T01:00:00+03:00',
                        'template_id': '5ff4901c583745e089e55be1',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'some',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf2',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'text',
                        'template_id': '5ff4901c583745e089e55be2',
                        'version': 1,
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 2,
            },
        ),
        (
            {'search_string': 'reSt', 'offset': 1, 'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'frost',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf3',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'Rest',
                        'template_id': '5ff4901c583745e089e55be3',
                        'version': 1,
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
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'rEsT cost',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf4',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'most',
                        'template_id': '5ff4901c583745e089e55be4',
                        'version': 1,
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
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'frost',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf3',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'Rest',
                        'template_id': '5ff4901c583745e089e55be3',
                        'version': 1,
                    },
                ],
                'limit': 1,
                'offset': 1,
                'total': 3,
            },
        ),
        (
            {'search_string': '', 'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'just document',
                        'generated_text': '---1---1.1; param=1',
                        'id': '000009999988888777772222',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'just document',
                        'template_id': '000000000000000000000002',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'rEsT cost',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf4',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'most',
                        'template_id': '5ff4901c583745e089e55be4',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'd',
                        'generated_text': '',
                        'id': '5ff4901c583745e089e55bf8',
                        'is_valid': False,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'outdated_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'venimaster',
                        'name': 'n',
                        'template_id': '5ff4901c583745e089e55be5',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'generated based on child11 template',
                        'generated_text': 'not valid data',
                        'id': '1ff4901c583745e089e55bf0',
                        'is_valid': False,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'n11',
                        'template_id': '1ff4901c583745e089e55be3',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'frost',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf3',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'Rest',
                        'template_id': '5ff4901c583745e089e55be3',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'some text',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf1',
                        'group_id': '000000000000000000000001',
                        'is_valid': True,
                        'modified_by': 'venimaster',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'name': 'test',
                        'outdated_at': '2018-07-02T01:00:00+03:00',
                        'template_id': '5ff4901c583745e089e55be1',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'some',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf2',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'text',
                        'template_id': '5ff4901c583745e089e55be2',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'post',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf5',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'Tost',
                        'template_id': '5ff4901c583745e089e55be5',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'generated based on child11 template',
                        'generated_text': '',
                        'id': '000009999988888777771111',
                        'group_id': '000000000000000000000001',
                        'is_valid': False,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'two last version is not valid',
                        'template_id': '111111111111111111111111',
                        'version': 4,
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 9,
            },
        ),
        (
            {'search_string': '', 'limit': 10, 'is_valid': 'true'},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'just document',
                        'generated_text': '---1---1.1; param=1',
                        'id': '000009999988888777772222',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'just document',
                        'template_id': '000000000000000000000002',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'rEsT cost',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf4',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'most',
                        'template_id': '5ff4901c583745e089e55be4',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'frost',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf3',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'Rest',
                        'template_id': '5ff4901c583745e089e55be3',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'some text',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf1',
                        'group_id': '000000000000000000000001',
                        'is_valid': True,
                        'modified_by': 'venimaster',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'name': 'test',
                        'outdated_at': '2018-07-02T01:00:00+03:00',
                        'template_id': '5ff4901c583745e089e55be1',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'some',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf2',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'text',
                        'template_id': '5ff4901c583745e089e55be2',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'post',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf5',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'Tost',
                        'template_id': '5ff4901c583745e089e55be5',
                        'version': 1,
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 6,
            },
        ),
        (
            {'search_string': '', 'limit': 10, 'is_valid': 'false'},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'd',
                        'generated_text': '',
                        'id': '5ff4901c583745e089e55bf8',
                        'is_valid': False,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'outdated_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'venimaster',
                        'name': 'n',
                        'template_id': '5ff4901c583745e089e55be5',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'generated based on child11 template',
                        'generated_text': 'not valid data',
                        'id': '1ff4901c583745e089e55bf0',
                        'is_valid': False,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'n11',
                        'template_id': '1ff4901c583745e089e55be3',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'generated based on child11 template',
                        'generated_text': '',
                        'id': '000009999988888777771111',
                        'group_id': '000000000000000000000001',
                        'is_valid': False,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'two last version is not valid',
                        'template_id': '111111111111111111111111',
                        'version': 4,
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 3,
            },
        ),
        (
            {
                'search_string': '',
                'limit': 10,
                'is_valid': 'false',
                'is_outdated': 'true',
            },
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'd',
                        'generated_text': '',
                        'id': '5ff4901c583745e089e55bf8',
                        'is_valid': False,
                        'outdated_at': '2018-07-01T01:00:00+03:00',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'venimaster',
                        'name': 'n',
                        'template_id': '5ff4901c583745e089e55be5',
                        'version': 1,
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 1,
            },
        ),
        (
            {
                'search_string': '',
                'limit': 10,
                'is_valid': 'false',
                'is_outdated': 'false',
            },
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'generated based on child11 template',
                        'generated_text': 'not valid data',
                        'id': '1ff4901c583745e089e55bf0',
                        'is_valid': False,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'n11',
                        'template_id': '1ff4901c583745e089e55be3',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'generated based on child11 template',
                        'generated_text': '',
                        'id': '000009999988888777771111',
                        'group_id': '000000000000000000000001',
                        'is_valid': False,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'two last version is not valid',
                        'template_id': '111111111111111111111111',
                        'version': 4,
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 2,
            },
        ),
        (
            {'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'just document',
                        'generated_text': '---1---1.1; param=1',
                        'id': '000009999988888777772222',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'just document',
                        'template_id': '000000000000000000000002',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'rEsT cost',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf4',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'most',
                        'template_id': '5ff4901c583745e089e55be4',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'd',
                        'generated_text': '',
                        'id': '5ff4901c583745e089e55bf8',
                        'is_valid': False,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'outdated_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'venimaster',
                        'name': 'n',
                        'template_id': '5ff4901c583745e089e55be5',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'generated based on child11 template',
                        'generated_text': 'not valid data',
                        'id': '1ff4901c583745e089e55bf0',
                        'is_valid': False,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'n11',
                        'template_id': '1ff4901c583745e089e55be3',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'frost',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf3',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'Rest',
                        'template_id': '5ff4901c583745e089e55be3',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'some text',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf1',
                        'group_id': '000000000000000000000001',
                        'is_valid': True,
                        'modified_by': 'venimaster',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'name': 'test',
                        'outdated_at': '2018-07-02T01:00:00+03:00',
                        'template_id': '5ff4901c583745e089e55be1',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'some',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf2',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'text',
                        'template_id': '5ff4901c583745e089e55be2',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'post',
                        'generated_text': 'some generated text',
                        'id': '5ff4901c583745e089e55bf5',
                        'is_valid': True,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'Tost',
                        'template_id': '5ff4901c583745e089e55be5',
                        'version': 1,
                    },
                    {
                        'created_at': '2018-07-01T00:00:00+03:00',
                        'created_by': 'venimaster',
                        'description': 'generated based on child11 template',
                        'generated_text': '',
                        'id': '000009999988888777771111',
                        'group_id': '000000000000000000000001',
                        'is_valid': False,
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'modified_by': 'russhakirov',
                        'name': 'two last version is not valid',
                        'template_id': '111111111111111111111111',
                        'version': 4,
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 9,
            },
        ),
    ],
)
async def test_dynamic_documents_search(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.get(
        '/v1/dynamic_documents/search/', params=query, headers=headers,
    )
    assert response.status == expected_status, await response.json()
    content = await response.json()
    assert content == expected_content


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            # 2nd version specified, document with 2 versions
            {'id': '5ff4901c583745e089e55bf1', 'version': 1},
            http.HTTPStatus.OK,
            {
                'name': 'test',
                'id': '5ff4901c583745e089e55bf1',
                'version': 1,
                'group_id': '000000000000000000000001',
                'description': 'some text',
                'generated_text': 'some generated text',
                'template_id': '5ff4901c583745e089e55be1',
                'params': common.PARAMS,
                'requests_params': common.REQUESTS_PARAMS,
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_by': 'venimaster',
                'modified_at': '2018-07-01T01:00:00+03:00',
                'outdated_at': '2018-07-02T01:00:00+03:00',
                'is_valid': True,
            },
        ),
        pytest.param(
            {
                'id': '5ff4901c583745e089e55bf1',
                'group_id': '000000000000000000000001',
            },
            http.HTTPStatus.OK,
            {
                'name': 'test',
                'id': '5ff4901c583745e089e55bf1',
                'version': 1,
                'group_id': '000000000000000000000001',
                'description': 'some text',
                'generated_text': 'some generated text',
                'template_id': '5ff4901c583745e089e55be1',
                'params': common.PARAMS,
                'requests_params': common.REQUESTS_PARAMS,
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_by': 'venimaster',
                'modified_at': '2018-07-01T01:00:00+03:00',
                'outdated_at': '2018-07-02T01:00:00+03:00',
                'is_valid': True,
            },
            id='with_group_id',
        ),
        pytest.param(
            {
                'id': '5ff4901c583745e089e55bf1',
                'group_id': '000000000000000000000002',
            },
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=5ff4901c583745e089e55bf1 not found'
                ),
            },
            id='with_invalid_group_id',
        ),
        (
            # version not specified, document with 2 versions
            {'id': '5ff4901c583745e089e55bf1'},
            http.HTTPStatus.OK,
            {
                'name': 'test',
                'id': '5ff4901c583745e089e55bf1',
                'version': 1,
                'group_id': '000000000000000000000001',
                'description': 'some text',
                'generated_text': 'some generated text',
                'template_id': '5ff4901c583745e089e55be1',
                'params': common.PARAMS,
                'requests_params': common.REQUESTS_PARAMS,
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_at': '2018-07-01T01:00:00+03:00',
                'modified_by': 'venimaster',
                'outdated_at': '2018-07-02T01:00:00+03:00',
                'is_valid': True,
            },
        ),
        (
            # 1st version specified, document with 2 versions
            {'id': '5ff4901c583745e089e55bf1', 'version': 0},
            http.HTTPStatus.OK,
            {
                'name': 'test',
                'id': '5ff4901c583745e089e55bf1',
                'version': 0,
                'description': 'some text',
                'generated_text': 'some generated text',
                'template_id': '5ff4901c583745e089e55be1',
                'params': [
                    {
                        'name': 'dynamic document parameter1',
                        'value': 'dynamic document parameter1 value',
                    },
                    {'name': 'dynamic document parameter2', 'value': 1},
                ],
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_by': 'russhakirov',
                'modified_at': '2018-07-01T01:00:00+03:00',
                'is_valid': True,
            },
        ),
        (
            # version specified, document with 1 version
            {'id': '5ff4901c583745e089e55bf2', 'version': 1},
            http.HTTPStatus.OK,
            {
                'name': 'text',
                'id': '5ff4901c583745e089e55bf2',
                'version': 1,
                'is_valid': True,
                'description': 'some',
                'generated_text': 'some generated text',
                'template_id': '5ff4901c583745e089e55be2',
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_by': 'russhakirov',
                'modified_at': '2018-07-01T01:00:00+03:00',
            },
        ),
        (
            # invalid document
            {'id': '5ff4901c583745e089e55bf8'},
            http.HTTPStatus.OK,
            {
                'name': 'n',
                'id': '5ff4901c583745e089e55bf8',
                'version': 1,
                'description': 'd',
                'generated_text': '',
                'template_id': '5ff4901c583745e089e55be5',
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_by': 'venimaster',
                'outdated_at': '2018-07-01T01:00:00+03:00',
                'modified_at': '2018-07-01T01:00:00+03:00',
                'is_valid': False,
            },
        ),
        (
            # version not specified, document with 1 version
            {'id': '5ff4901c583745e089e55bf2'},
            http.HTTPStatus.OK,
            {
                'name': 'text',
                'id': '5ff4901c583745e089e55bf2',
                'version': 1,
                'is_valid': True,
                'description': 'some',
                'generated_text': 'some generated text',
                'template_id': '5ff4901c583745e089e55be2',
                'created_by': 'venimaster',
                'created_at': '2018-07-01T00:00:00+03:00',
                'modified_by': 'russhakirov',
                'modified_at': '2018-07-01T01:00:00+03:00',
            },
        ),
        # version not specified, removed dynamic document with 2 versions
        (
            {'id': '5ff4901c583745e089e55bf6'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=5ff4901c583745e089e55bf6 not found'
                ),
            },
        ),
        # 1st version specified, removed dynamic document with 2 versions
        (
            {'id': '5ff4901c583745e089e55bf6', 'version': 0},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=5ff4901c583745e089e55bf6 not found'
                ),
            },
        ),
        # 2nd version specified, removed dynamic document with 2 versions
        (
            {'id': '5ff4901c583745e089e55bf6', 'version': 1},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=5ff4901c583745e089e55bf6 not found'
                ),
            },
        ),
        # version not specified, missing dynamic document
        (
            {'id': '5ff4901c583745e089e55bf7'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=5ff4901c583745e089e55bf7 not found'
                ),
            },
        ),
        # version specified, missing dynamic document
        (
            {'id': '5ff4901c583745e089e55bf7', 'version': 100},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=5ff4901c583745e089e55bf7 not found'
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
        ),  # invalid query
    ],
)
async def test_get_dynamic_document(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.get(
        '/v1/dynamic_documents/', params=query, headers=headers,
    )
    assert response.status == expected_status, await response.text()
    content = await response.json()
    assert content == expected_content


@pytest.mark.parametrize(
    'body, headers, expected_status, expected_content',
    [
        pytest.param(
            {
                'name': 'new dynamic document',
                'update_schedules': [
                    {
                        'times': ['22:00'],
                        'weekdays': ['mon'],
                        'timezone': 'UTC',
                    },
                ],
                'description': 'description new dynamic document',
                'template_id': '000000000000000000000002',
                'group_id': '000000000000000000000001',
                'generate_text_immediately': True,
                'requests_params': [
                    {
                        'id': '123451234512345123451234',
                        'name': 'request',
                        'query': {'number': 11},
                    },
                ],
                'params': [{'name': 'param', 'value': 'test'}],
            },
            {'X-Yandex-Login': 'yandex-login'},
            http.HTTPStatus.OK,
            {
                'created_by': 'yandex-login',
                'description': 'description new dynamic document',
                'generated_text': '---1---1.1; param=test',
                'generated_by': 'yandex-login',
                'group_id': '000000000000000000000001',
                'is_valid': True,
                'modified_by': 'yandex-login',
                'name': 'new dynamic document',
                'params': [{'name': 'param', 'value': 'test'}],
                'requests_params': [
                    {
                        'id': '123451234512345123451234',
                        'name': 'request',
                        'query': {'number': 11},
                    },
                ],
                'update_schedules': [
                    {
                        'times': ['22:00'],
                        'weekdays': ['mon'],
                        'timezone': 'UTC',
                    },
                ],
                'template_id': '000000000000000000000002',
                'version': 0,
            },
            id='ok',
        ),
        pytest.param(
            update_data('test', 'some text'),
            {'X-Yandex-Login': 'venimaster'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DYNAMIC_DOCUMENT_WITH_NAME_ALREADY_EXIST',
                'details': {},
                'message': (
                    'dynamic document with name "test" already exists: '
                ),
            },
            id='already_exist',
        ),
        pytest.param(
            {
                'name': 'new dynamic document',
                'update_schedules': [
                    {
                        'times': ['22:00'],
                        'weekdays': ['mon'],
                        'timezone': 'UTC',
                    },
                ],
                'description': 'description new dynamic document',
                'template_id': '000000000000000000000002',
                'group_id': '000000000000000000000002',
                'generate_text_immediately': True,
                'requests_params': [
                    {
                        'id': '123451234512345123451234',
                        'name': 'request',
                        'query': {'number': 11},
                    },
                ],
                'params': [{'name': 'param', 'value': 'test'}],
            },
            {'X-Yandex-Login': 'yandex-login'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'GROUP_NOT_FOUND',
                'details': {},
                'message': 'Group with id=000000000000000000000002 not found',
            },
            id='group_not_found',
        ),
    ],
)
@pytest.mark.parametrize(
    'is_async',
    (
        pytest.param(False, id='is_not_async'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                DOCUMENT_TEMPLATOR_USE_ASYNC_UPSERT_DOCUMENTS={
                    '__default__': True,
                },
            ),
            id='is_async',
        ),
    ),
)
@pytest.mark.usefixtures('requests_handlers')
@pytest.mark.config(**common.REQUEST_CONFIG)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_post_dynamic_document(
        api_app_client,
        body,
        headers,
        expected_status,
        expected_content,
        is_async,
        stq,
        stq_runner,
):
    response = await api_app_client.post(
        '/v1/dynamic_documents/', json=body, headers=headers,
    )
    if is_async:
        assert response.status == 202
        id_ = (await response.json())['id']
        headers['X-Idempotency-Token'] = id_
        call = stq.document_templator_upsert_documents.next_call()

        await stq_runner.document_templator_upsert_documents.call(
            task_id=call['id'], args=call['args'], kwargs=call['kwargs'],
        )
        response = await api_app_client.post(
            '/v1/dynamic_documents/', json=body, headers=headers,
        )
    assert response.status == expected_status, await response.text()
    content = await response.json()
    if expected_status == http.HTTPStatus.OK:
        dynamic_document_id = content.pop('id')
        assert dynamic_document_id is not None
        assert content.get('created_at') is not None
        created_at = content.pop('created_at')
        modified_at = content.pop('modified_at')
        generated_at = content.pop('generated_at')
        assert created_at == modified_at
        assert content == expected_content
        query_for_get = {
            'id': dynamic_document_id,
            'version': content['version'],
        }
        assert modified_at is not None
        response = await api_app_client.get(
            '/v1/dynamic_documents/', params=query_for_get,
        )
        content_from_get = await response.json()
        assert content_from_get.pop('modified_at') == modified_at
        assert content_from_get.pop('created_at') == created_at
        assert content_from_get.pop('generated_at') == generated_at
        assert content_from_get.pop('id') == dynamic_document_id
        assert content == content_from_get
    else:
        assert content == expected_content


@pytest.mark.parametrize(
    'query, body, headers, expected_status, expected_content',
    [
        pytest.param(
            {'id': '000009999988888777772222', 'version': 1},
            {
                'name': 'changed',
                'update_schedules': [
                    {
                        'times': ['23:00'],
                        'weekdays': ['tue'],
                        'timezone': 'UTC',
                    },
                ],
                'description': 'just document',
                'template_id': '000000000000000000000002',
                'params': [{'name': 'param', 'value': 1}],
                'requests_params': [
                    {'name': 'request', 'id': '5ff4901c583745e089e55bd3'},
                ],
            },
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.OK,
            {
                'created_at': '2018-07-01T00:00:00+03:00',
                'created_by': 'venimaster',
                'description': 'just document',
                'generated_text': '---1---1.1; param=1',
                'generated_by': 'russhakirov',
                'id': '000009999988888777772222',
                'is_valid': True,
                'modified_by': 'russhakirov',
                'name': 'changed',
                'update_schedules': [
                    {
                        'times': ['23:00'],
                        'weekdays': ['tue'],
                        'timezone': 'UTC',
                    },
                ],
                'params': [{'name': 'param', 'value': 1}],
                'requests_params': [
                    {'id': '5ff4901c583745e089e55bd3', 'name': 'request'},
                ],
                'template_id': '000000000000000000000002',
                'version': 2,
            },
            id='ok',
        ),
        pytest.param(
            {'id': '000009999988888777772222', 'version': 1},
            {
                'name': 'changed',
                'description': 'just document',
                'template_id': '000000000000000000000002',
                'group_id': '000000000000000000000002',
                'params': [{'name': 'param', 'value': 1}],
                'requests_params': [
                    {'name': 'request', 'id': '5ff4901c583745e089e55bd3'},
                ],
            },
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'GROUP_NOT_FOUND',
                'details': {},
                'message': 'Group with id=000000000000000000000002 not found',
            },
            id='group_not_found',
        ),
        pytest.param(
            {'id': '5ff4901c583745e089e55bf1', 'version': 1},
            update_data('text', 'some text'),
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DYNAMIC_DOCUMENT_WITH_NAME_ALREADY_EXIST',
                'details': {},
                'message': (
                    'dynamic document with name "text" already exists: '
                ),
            },
            id='document_already_exist',
        ),
        pytest.param(
            {'id': '5ff4901c583745e089e55bf6', 'version': 0},
            update_data('test22', 'some text'),
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=5ff4901c583745e089e55bf6 not found'
                ),
            },
            id='not_found',
        ),
        pytest.param(
            {'id': '5ff4901c583745e089e55bf1', 'version': 2},
            update_data('test', 'some text'),
            {'X-Yandex-Login': 'russhakirov'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document '
                    'with id=5ff4901c583745e089e55bf1 not found'
                ),
            },
            id='not_found_version_2',
        ),
    ],
)
@pytest.mark.parametrize(
    'is_async',
    (
        pytest.param(False, id='is_not_async'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                DOCUMENT_TEMPLATOR_USE_ASYNC_UPSERT_DOCUMENTS={
                    '__default__': True,
                },
            ),
            id='is_async',
        ),
    ),
)
@pytest.mark.usefixtures('requests_handlers')
@pytest.mark.config(**common.REQUEST_CONFIG)
async def test_put_dynamic_document(
        api_app_client,
        query,
        headers,
        body,
        expected_status,
        expected_content,
        is_async,
        stq,
        stq_runner,
):
    if expected_status == http.HTTPStatus.OK:
        expected_get_content = expected_content
    else:
        response = await api_app_client.get(
            '/v1/dynamic_documents/', params=query,
        )
        expected_get_content = await response.json()

    # Act
    response = await api_app_client.put(
        '/v1/dynamic_documents/', params=query, json=body, headers=headers,
    )
    if is_async:
        assert response.status == 202
        id_ = (await response.json())['id']
        headers['X-Idempotency-Token'] = id_
        call = stq.document_templator_upsert_documents.next_call()

        await stq_runner.document_templator_upsert_documents.call(
            task_id=call['id'], args=call['args'], kwargs=call['kwargs'],
        )
        response = await api_app_client.put(
            '/v1/dynamic_documents/', params=query, json=body, headers=headers,
        )

    assert response.status == expected_status, await response.text()
    content = await response.json()
    if expected_status == http.HTTPStatus.OK:
        expected_get_content['modified_at'] = content['modified_at']
        expected_get_content['generated_at'] = content['generated_at']
    if expected_status == http.HTTPStatus.OK:
        query_for_get = {'id': content['id'], 'version': content['version']}
    else:
        query_for_get = query
    response_from_get = await api_app_client.get(
        '/v1/dynamic_documents/', params=query_for_get,
    )
    assert await response_from_get.json() == expected_get_content
    assert content == expected_content


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            {'id': '5ff4901c583745e089e55bf1'},
            http.HTTPStatus.OK,
            {'id': '5ff4901c583745e089e55bf1'},
        ),
        (
            {'id': '5ff4901c583745e089e55bf6'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=5ff4901c583745e089e55bf6 not found'
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
async def test_delete_dynamic_document(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.delete(
        '/v1/dynamic_documents/', params=query, headers=headers,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_content
    if response.status == http.HTTPStatus.OK:
        query_for_get = {'id': content['id']}
        response = await api_app_client.get(
            '/v1/dynamic_documents/', params=query_for_get,
        )
        assert response.status == http.HTTPStatus.NOT_FOUND
