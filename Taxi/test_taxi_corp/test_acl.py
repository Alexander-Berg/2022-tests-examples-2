from aiohttp import web
import pytest

from taxi_corp import corp_web
from taxi_corp.api import acl


dbcachemethod = corp_web.DbCacheFactory(False)  # pylint: disable=invalid-name
EXPECTED_DOC = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
OTHER_DOC = {'key1': 'other1', 'key2': 'other2', 'key3': 'other3'}

CLIENT_PERMISSIONS = [
    'taxi',
    'taxi_client',
    'taxi_department_create',
    'taxi_department_part',
    'taxi_department_full',
    'taxi_other',
    'logistics',
]

DEPARTMENT_SECRETARY_PERMISSIONS = [
    'taxi',
    'taxi_department_part',
    'taxi_other',
]


class Cache(dict):
    def __init__(self, request):
        super(Cache, self).__init__()

        self.request = request

    @property
    async def access_data(self):
        return acl.AccessData(
            yandex_uid='uid',
            role='',
            client_id='client_id',
            department_id='department_id',
            permissions=self.request.permissions,
        )

    @dbcachemethod('method', linked_keys=['key1', 'key2'])
    def method(self, key1=None, key2=None, key3=None):
        # pylint: disable=no-self-use

        if key1 == 'value1':
            return EXPECTED_DOC
        return OTHER_DOC


class Request(web.Request):

    # pylint: disable=super-init-not-called

    def __init__(self, permissions):
        self.permissions = permissions
        self.log_extra = None
        self._state = {}
        self.cache = Cache(self)


@pytest.mark.parametrize(
    'permissions, handler_permission',
    [
        (CLIENT_PERMISSIONS, acl.Permission.taxi_client),
        (CLIENT_PERMISSIONS, acl.Permission.taxi_other),
        (CLIENT_PERMISSIONS, acl.Permission.taxi_department_full),
        (
            DEPARTMENT_SECRETARY_PERMISSIONS,
            acl.Permission.taxi_department_part,
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_access_permission(permissions, handler_permission):
    @acl.access_permission(handler_permission)
    async def handler(request):
        return True

    assert await handler(Request(permissions=permissions))


def test_cache_linked_attrs():
    cache = Request(permissions=CLIENT_PERMISSIONS).cache
    assert (
        cache.method(key1='value1') == EXPECTED_DOC
    ), 'should put doc to the cache and return'
    assert (
        cache.method(key2='value2') == EXPECTED_DOC
    ), 'should get the document from cache'
    assert (
        cache.method(key2='other2') == OTHER_DOC
    ), 'should not get the same document from the cache'
    with pytest.raises(ValueError):
        cache.method(key2='somethingelse')
