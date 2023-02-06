# pylint: disable=redefined-outer-name,unused-variable
import collections
import http

from aiohttp import web
import pytest

from taxi.util import permissions


@pytest.fixture
async def admin_groups_without_countries(db):
    await db.admin_groups.insert_many(
        [
            {
                '_id': 'group_1',
                'permissions': ['perm_1', 'perm_2'],
                'name': '1',
            },
            {'_id': 'group_2', 'permissions': ['perm_3'], 'name': '2'},
        ],
    )


@pytest.fixture
async def admin_groups_with_countries(db):
    await db.admin_groups.insert_many(
        [
            {
                '_id': 'group_3',
                'permissions': [{'id': 'perm_3', 'mode': 'unrestricted'}],
                'name': '3',
            },
            {
                '_id': 'group_4',
                'permissions': [
                    {
                        'id': 'perm_3',
                        'mode': 'countries_filter',
                        'countries_filter': ['rus', 'blr'],
                    },
                    {
                        'id': 'perm_4',
                        'mode': 'countries_filter',
                        'countries_filter': ['rus'],
                    },
                ],
                'name': '4',
            },
        ],
    )


@pytest.mark.parametrize(
    'permission,user_groups,status,expected',
    [
        (
            'perm_1',
            ['group_1'],
            http.HTTPStatus.OK,
            permissions.unrestricted_perm(),
        ),
        (
            'perm_3',
            ['group_2'],
            http.HTTPStatus.OK,
            permissions.unrestricted_perm(),
        ),
        (
            'perm_4',
            ['group_3', 'group_4'],
            http.HTTPStatus.OK,
            permissions.countries_perm(['rus']),
        ),
        (
            'perm_4',
            ['group_1', 'group_4'],
            http.HTTPStatus.OK,
            permissions.countries_perm(['rus']),
        ),
        ('perm_5', ['group_2', 'group_4'], http.HTTPStatus.FORBIDDEN, None),
    ],
)
@pytest.mark.mongodb_collections('admin_groups')
async def test_permissions(
        db,
        permission,
        user_groups,
        status,
        expected,
        admin_groups_without_countries,
        admin_groups_with_countries,
):
    @permissions.perm_required(permission)
    async def test_handler(request):
        return web.json_response({})

    class DummyHandler:
        class DummyRequest:
            superuser = False
            groups = user_groups
            app = collections.namedtuple('app', 'db')(db)
            login = 'test_login'

            def __getitem__(self, item):
                # request log_extra
                return {}

        request = DummyRequest()

    handler = DummyHandler()

    try:
        result = await test_handler(handler)
    except web.HTTPForbidden as exc:
        result = exc

    assert result.status == status

    if status == http.HTTPStatus.OK:
        assert getattr(handler.request, 'authorized_permission') == expected
