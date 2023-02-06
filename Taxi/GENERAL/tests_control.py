# pylint: disable=too-many-lines
# pylint: disable=invalid-string-quote
# pylint: disable=wildcard-import
# pylint: disable=ungrouped-imports
# pylint: disable=unused-wildcard-import
# pylint: disable=redefined-builtin
# pylint: disable=unused-variable
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name

# pylint: disable=bad-whitespace
# flake8: noqa

from aiohttp import web

from taxi.util import dates


# pylint: disable=protected-access
async def handle(request: web.Request) -> web.Response:
    data = await request.json()
    if data.get('now'):
        dates._set_now_stamp(dates.parse_timestring(data['now']))
    else:
        dates._set_now_stamp()
    if data.get('invalidate_caches', False):
        if data.get('cache_clean_update', False):
            await request.app['context'].clean_caches()
        await request.app['context'].refresh_caches()
    return web.json_response({})
