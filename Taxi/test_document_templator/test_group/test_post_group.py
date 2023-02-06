import http
from unittest import mock

import pytest

NEW_TEMPLATE_GROUP_ID = '100000000000000000000000'


@pytest.mark.parametrize(
    'headers, body, expected_status, expected_content',
    [
        pytest.param(
            {'X-Yandex-Login': 'robot'},
            {'name': 'sub main', 'description': 'sub main description'},
            http.HTTPStatus.OK,
            {
                'id': '100000000000000000000000',
                'name': 'sub main',
                'description': 'sub main description',
            },
            id='ok',
        ),
        pytest.param(
            {'X-Yandex-Login': 'robot'},
            {'name': 'new', 'parent_id': '000000000000000000000001'},
            http.HTTPStatus.OK,
            {
                'id': '100000000000000000000000',
                'name': 'new',
                'parent_id': '000000000000000000000001',
            },
            id='ok_with_parent',
        ),
        pytest.param(
            {'X-Yandex-Login': 'robot'},
            {'name': 'new', 'parent_id': '000000000000000000000000'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'GROUP_NOT_FOUND',
                'details': {},
                'message': 'Group with id=000000000000000000000000 not found',
            },
            id='parent_not_found',
        ),
        pytest.param(
            {'X-Yandex-Login': 'robot'},
            {'name': 'main'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'GROUP_ALREADY_EXISTS',
                'details': {'name': 'main', 'parent_id': None},
                'message': (
                    'Group with name="main" '
                    'and parent_id="None" already exist'
                ),
            },
            id='already_exist',
        ),
        pytest.param(
            {'X-Yandex-Login': 'robot'},
            {'name': 'sub main', 'parent_id': '000000000000000000000001'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'GROUP_ALREADY_EXISTS',
                'details': {
                    'name': 'sub main',
                    'parent_id': '000000000000000000000001',
                },
                'message': (
                    'Group with name="sub main" and '
                    'parent_id="000000000000000000000001" already exist'
                ),
            },
            id='already_exist_with_parent',
        ),
        pytest.param(
            {'X-Yandex-Login': 'robot'},
            {'parent_id': '000000000000000000000000'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'name is required property'},
                'message': 'Some parameters are invalid',
            },
            id='without_id',
        ),
        pytest.param(
            {},
            {'name': 'new', 'parent_id': '000000000000000000000001'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'MISSING_LOGIN',
                'details': {},
                'message': 'X-Yandex-Login or login must be given',
            },
            id='without_yandex_login',
        ),
    ],
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.param('/v1/dynamic_document_groups/', id='dynamic_document'),
        pytest.param('/v1/template_groups/', id='template'),
    ),
)
@pytest.mark.now('2019-12-02T01:00:00+03:00')
async def test_post_group(
        api_app_client, headers, body, expected_status, expected_content, url,
):
    with mock.patch(
            'document_templator.models.group.generate_group_id',
            return_value=NEW_TEMPLATE_GROUP_ID,
    ):
        response = await api_app_client.post(url, json=body, headers=headers)
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content

    response_get = await api_app_client.get(
        url, params={'id': NEW_TEMPLATE_GROUP_ID},
    )
    if expected_status == http.HTTPStatus.OK:
        assert response_get.status == http.HTTPStatus.OK
        assert await response_get.json() == content
    else:
        assert response_get.status == http.HTTPStatus.NOT_FOUND
        assert await response_get.json() == {
            'code': 'GROUP_NOT_FOUND',
            'details': {},
            'message': 'Group with id=100000000000000000000000 not found',
        }
