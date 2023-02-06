"""This is to test @corp_web.from_authproxy decorator, not used in deploy.

"""
from aiohttp import web

from taxi_corp import corp_web
from taxi_corp.api import acl
from taxi_corp.util import json_util


@corp_web.from_authproxy
async def fetch_access_data(request: corp_web.Request) -> web.Response:
    access_data: acl.AccessData = await request.cache.access_data
    return json_util.response(
        {
            'yandex_uid': access_data.yandex_uid,
            'client_id': access_data.client_id,
            'role': access_data.role,
            'department_id': access_data.department_id,
            'permissions': access_data.permissions,
        },
    )
