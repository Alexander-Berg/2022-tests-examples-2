import http

import pytest


@pytest.mark.parametrize(
    'headers, query, body, expected_status, expected_content',
    [
        pytest.param(
            {'X-Yandex-Login': 'new_robot'},
            {'id': '000000000000000000000003'},
            {
                'name': 'updated',
                'description': 'updated description',
                'parent_id': '000000000000000000000001',
            },
            http.HTTPStatus.OK,
            {
                'description': 'updated description',
                'id': '000000000000000000000003',
                'name': 'updated',
                'parent_id': '000000000000000000000001',
            },
            id='ok',
        ),
        pytest.param(
            {'X-Yandex-Login': 'new_robot'},
            {'id': '000000000000000000000000'},
            {'name': 'updated', 'description': 'updated description'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'GROUP_NOT_FOUND',
                'details': {},
                'message': 'Group with id=000000000000000000000000 not found',
            },
            id='not_found',
        ),
        pytest.param(
            {'X-Yandex-Login': 'new_robot'},
            {'id': '000000000000000000000001'},
            {
                'name': 'updated',
                'description': 'updated description',
                'parent_id': '000000000000000000000000',
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'GROUP_NOT_FOUND',
                'details': {},
                'message': 'Group with id=000000000000000000000000 not found',
            },
            id='parent_not_found',
        ),
        pytest.param(
            {'X-Yandex-Login': 'new_robot'},
            {'id': '000000000000000000000003'},
            {
                'name': 'sub main',
                'description': 'updated description',
                'parent_id': '000000000000000000000001',
            },
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
            id='already_exist',
        ),
        pytest.param(
            {'X-Yandex-Login': 'new_robot'},
            {'id': '000000000000000000000002'},
            {'name': 'main', 'description': 'updated description'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'GROUP_ALREADY_EXISTS',
                'details': {'name': 'main', 'parent_id': None},
                'message': (
                    'Group with name="main" '
                    'and parent_id="None" already exist'
                ),
            },
            id='already_exist_without_parent',
        ),
        pytest.param(
            {'X-Yandex-Login': 'new_robot'},
            {'id': '000000000000000000000001'},
            {
                'name': 'updated',
                'description': 'updated description',
                'parent_id': '000000000000000000000003',
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'CIRCULAR_DEPENDENCY_IN_GROUP',
                'details': {},
                'message': 'Circular dependency in group',
            },
            id='circylar_dependency',
        ),
        pytest.param(
            {'X-Yandex-Login': 'new_robot'},
            {},
            {'name': 'updated', 'description': 'updated description'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'id is required parameter'},
                'message': 'Some parameters are invalid',
            },
            id='without_id',
        ),
        pytest.param(
            {},
            {'id': '000000000000000000000001'},
            {'name': 'updated', 'description': 'updated description'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'MISSING_LOGIN',
                'details': {},
                'message': 'X-Yandex-Login or login must be given',
            },
            id='without_yandex_loginlogin',
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
async def test_put_group(
        api_app_client,
        headers,
        query,
        body,
        expected_status,
        expected_content,
        url,
):
    response_get_before_updating = await api_app_client.get(url, params=query)
    content_before_updating = await response_get_before_updating.json()

    response = await api_app_client.put(
        url, json=body, headers=headers, params=query,
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content

    response_get = await api_app_client.get(url, params=query)
    if expected_status == http.HTTPStatus.OK:
        assert response_get.status == http.HTTPStatus.OK
        assert await response_get.json() == content
    else:
        assert response_get.status == response_get_before_updating.status
        assert await response_get.json() == content_before_updating
