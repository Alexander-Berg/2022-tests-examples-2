import logging

from aiohttp import web

from libstall import log
from stall.client.httpx import BaseClient
from stall.middlewares.aab_logging import middleware


async def test_common(tap, ext_api, caplog, cfg):
    async def handle(request):
        return web.json_response({
            'code': 'OK',
            'req': await request.text()
        })

    with tap, caplog.at_level(logging.INFO, logger=log.name):
        cfg.set('log.log_ok_responses', True)

        async with await ext_api(
                BaseClient(), handle,
                middlewares=[middleware]
        ) as cl:
            res = await cl.req()
            tap.ok(res, 'got response')

            tap.eq(len(caplog.records), 2, 'there are two records')
            rec1, rec2 = caplog.records

            tap.eq(rec1.type, 'request', 'request type')
            tap.eq(rec1.log_type, '/', 'request log_type')
            tap.eq(rec1.ctx['method'], 'GET', 'request method')
            tap.eq(rec1.ctx['uri'], '/', 'request uri')
            tap.eq(rec1.ctx['body'], '', 'request body')

            tap.eq(rec2.message, 'api response', 'response')
            tap.eq(rec2.log_type, '/', 'response log_type')
            tap.eq(rec2.ctx['method'], 'GET', 'response method')
            tap.eq(rec2.ctx['uri'], '/', 'response uri')
            tap.ok(rec2.ctx['meta_code'], 200, 'response code')
            tap.ok(rec2.ctx['total_time'], 'response time')
            tap.eq(rec2.ctx['body'], '{"code": "OK", "req": ""}',
                   'response body')

            tap.eq(rec1.ctx['link'], rec2.ctx['link'], 'links are equal')


async def test_params(tap, ext_api, caplog, cfg):
    async def handle(request):
        return web.json_response({
            'code': 'OK',
            'req': await request.text()
        })

    with tap, caplog.at_level(logging.INFO, logger=log.name):
        cfg.set('log.log_ok_responses', True)

        async with await ext_api(
                BaseClient(), handle,
                middlewares=[middleware]
        ) as cl:
            res = await cl.req('GET', '/path', params={'q': 123})
            tap.ok(res, 'got response')

            tap.eq(len(caplog.records), 2, 'there are two records')
            rec1, rec2 = caplog.records

            tap.eq(rec1.type, 'request', 'request type')
            tap.eq(rec1.log_type, '/path', 'request log_type')
            tap.eq(rec1.ctx['method'], 'GET', 'request method')
            tap.eq(rec1.ctx['uri'], '/path?q=123', 'request uri')
            tap.eq(rec1.ctx['body'], '', 'request body')

            tap.eq(rec2.message, 'api response', 'response')
            tap.eq(rec2.log_type, '/path', 'response log_type')
            tap.eq(rec2.ctx['method'], 'GET', 'response method')
            tap.eq(rec2.ctx['uri'], '/path?q=123', 'response uri')
            tap.ok(rec2.ctx['meta_code'], 200, 'response code')
            tap.ok(rec2.ctx['total_time'], 'response time')
            tap.eq(rec2.ctx['body'], '{"code": "OK", "req": ""}',
                   'response body')

            tap.eq(rec1.ctx['link'], rec2.ctx['link'], 'links are equal')


async def test_post(tap, ext_api, caplog, cfg):
    async def handle(request):
        return web.json_response({
            'code': 'OK',
            'req': await request.text()
        })

    with tap, caplog.at_level(logging.INFO, logger=log.name):
        cfg.set('log.log_ok_responses', True)

        async with await ext_api(
                BaseClient(), handle,
                middlewares=[middleware]
        ) as cl:
            res = await cl.req('POST', json={'a': 1})
            tap.ok(res, 'got response')

            tap.eq(len(caplog.records), 2, 'there are two records')
            rec1, rec2 = caplog.records

            tap.eq(rec1.type, 'request', 'request type')
            tap.eq(rec1.log_type, '/', 'request log_type')
            tap.eq(rec1.ctx['method'], 'POST', 'request method')
            tap.eq(rec1.ctx['uri'], '/', 'request uri')
            tap.eq(rec1.ctx['body'], '{"a":1}', 'request body')

            tap.eq(rec2.message, 'api response', 'response')
            tap.eq(rec2.log_type, '/', 'response log_type')
            tap.eq(rec2.ctx['method'], 'POST', 'response method')
            tap.eq(rec2.ctx['uri'], '/', 'response uri')
            tap.ok(rec2.ctx['meta_code'], 200, 'response code')
            tap.ok(rec2.ctx['total_time'], 'response time')
            tap.eq(rec2.ctx['body'], '{"code": "OK", "req": "{\\"a\\":1}"}',
                   'response body')

            tap.eq(rec1.ctx['link'], rec2.ctx['link'], 'links are equal')


async def test_400(tap, ext_api, caplog):
    async def handle(request):  # pylint: disable=unused-argument
        return web.json_response({
            'code': 'ER_BAD_REQUEST'
        }, status=400)

    with tap, caplog.at_level(logging.INFO, logger=log.name):
        async with await ext_api(
                BaseClient(), handle,
                middlewares=[middleware]
        ) as cl:
            res = await cl.req('POST', json={'a': 1})
            tap.ok(res, 'got response')

            tap.eq(len(caplog.records), 2, 'there are two records')
            rec1, rec2 = caplog.records

            tap.eq(rec1.type, 'request', 'request type')
            tap.eq(rec1.log_type, '/', 'request log_type')
            tap.eq(rec1.ctx['method'], 'POST', 'request method')
            tap.eq(rec1.ctx['uri'], '/', 'request uri')
            tap.eq(rec1.ctx['body'], '{"a":1}', 'request body')

            tap.eq(rec2.message, 'api response', 'response')
            tap.eq(rec2.log_type, '/', 'response log_type')
            tap.eq(rec2.ctx['method'], 'POST', 'response method')
            tap.eq(rec2.ctx['uri'], '/', 'response uri')
            tap.ok(rec2.ctx['meta_code'], 400, 'response code')
            tap.ok(rec2.ctx['total_time'], 'response time')
            tap.eq(rec2.ctx['body'], '{"code": "ER_BAD_REQUEST"}',
                   'response body')

            tap.eq(rec1.ctx['link'], rec2.ctx['link'], 'links are equal')


async def test_500(tap, ext_api, caplog):
    async def handle(request):  # pylint: disable=unused-argument
        return web.json_response({
            'code': 'ER_INTERNAL_ERROR'
        }, status=500)

    with tap, caplog.at_level(logging.INFO, logger=log.name):
        async with await ext_api(
                BaseClient(), handle,
                middlewares=[middleware]
        ) as cl:
            res = await cl.req('POST', json={'a': 1})
            tap.ok(res, 'got response')

            tap.eq(len(caplog.records), 2, 'there are two records')
            rec1, rec2 = caplog.records

            tap.eq(rec1.type, 'request', 'request type')
            tap.eq(rec1.log_type, '/', 'request log_type')
            tap.eq(rec1.ctx['method'], 'POST', 'request method')
            tap.eq(rec1.ctx['uri'], '/', 'request uri')
            tap.eq(rec1.ctx['body'], '{"a":1}', 'request body')

            tap.eq(rec2.message, 'api response', 'response')
            tap.eq(rec2.log_type, '/', 'response log_type')
            tap.eq(rec2.ctx['method'], 'POST', 'response method')
            tap.eq(rec2.ctx['uri'], '/', 'response uri')
            tap.ok(rec2.ctx['meta_code'], 500, 'response code')
            tap.ok(rec2.ctx['total_time'], 'response time')
            tap.eq(rec2.ctx['body'], '{"code": "ER_INTERNAL_ERROR"}',
                   'response body')

            tap.eq(rec1.ctx['link'], rec2.ctx['link'], 'links are equal')


async def test_disabled_for_ok(tap, ext_api, caplog, cfg):
    async def handle(request):
        return web.json_response({
            'code': 'OK',
            'req': await request.text()
        })

    with tap, caplog.at_level(logging.INFO, logger=log.name):
        cfg.set('log.log_ok_responses', False)

        async with await ext_api(
                BaseClient(), handle,
                middlewares=[middleware]
        ) as cl:
            res = await cl.req()
            tap.ok(res, 'got response')

            tap.eq(len(caplog.records), 0, 'there are no records')


# small but correct PNG file
PNG_FILE = (
    b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A\x00\x00\x00\x0D\x49\x48\x44\x52'
    b'\x00\x00\x01\x00\x00\x00\x01\x00\x01\x03\x00\x00\x00\x66\xBC\x3A'
    b'\x25\x00\x00\x00\x03\x50\x4C\x54\x45\xB5\xD0\xD0\x63\x04\x16\xEA'
    b'\x00\x00\x00\x1F\x49\x44\x41\x54\x68\x81\xED\xC1\x01\x0D\x00\x00'
    b'\x00\xC2\xA0\xF7\x4F\x6D\x0E\x37\xA0\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\xBE\x0D\x21\x00\x00\x01\x9A\x60\xE1\xD5\x00\x00\x00\x00\x49'
    b'\x45\x4E\x44\xAE\x42\x60\x82'
)


async def test_picture(tap, ext_api, caplog, cfg):
    async def handle(request):  # pylint: disable=unused-argument
        return web.Response(body=PNG_FILE)

    with tap, caplog.at_level(logging.INFO, logger=log.name):
        cfg.set('log.log_ok_responses', True)

        async with await ext_api(
                BaseClient(), handle,
                middlewares=[middleware]
        ) as cl:
            res = await cl.req('POST', data=PNG_FILE)
            tap.ok(res, 'got response')

            tap.eq(len(caplog.records), 2, 'there are two records')
            rec1, rec2 = caplog.records

            tap.eq(rec1.type, 'request', 'request type')
            tap.eq(rec1.log_type, '/', 'request log_type')
            tap.eq(rec1.ctx['method'], 'POST', 'request method')
            tap.eq(rec1.ctx['uri'], '/', 'request uri')
            tap.eq(rec1.ctx['body'], '<cannot parse body>', 'request body')

            tap.eq(rec2.message, 'api response', 'response')
            tap.eq(rec2.log_type, '/', 'response log_type')
            tap.eq(rec2.ctx['method'], 'POST', 'response method')
            tap.eq(rec2.ctx['uri'], '/', 'response uri')
            tap.ok(rec2.ctx['meta_code'], 200, 'response code')
            tap.ok(rec2.ctx['total_time'], 'response time')
            tap.eq(rec2.ctx['body'], '<cannot parse body>', 'response body')

            tap.eq(rec1.ctx['link'], rec2.ctx['link'], 'links are equal')


async def test_long_body(tap, ext_api, caplog, cfg):
    async def handle(request):  # pylint: disable=unused-argument
        return web.json_response('a' * 20000)

    with tap, caplog.at_level(logging.INFO, logger=log.name):
        cfg.set('log.log_ok_responses', True)

        async with await ext_api(
                BaseClient(), handle,
                middlewares=[middleware]
        ) as cl:
            res = await cl.req('POST', data='b' * 20000)
            tap.ok(res, 'got response')

            tap.eq(len(caplog.records), 2, 'there are two records')
            rec1, rec2 = caplog.records

            tap.eq(rec1.type, 'request', 'request type')
            tap.eq(rec1.log_type, '/', 'request log_type')
            tap.eq(rec1.ctx['method'], 'POST', 'request method')
            tap.eq(rec1.ctx['uri'], '/', 'request uri')
            tap.eq(rec1.ctx['body'], 'b' * 5 * 1024, 'request body')

            tap.eq(rec2.message, 'api response', 'response')
            tap.eq(rec2.log_type, '/', 'response log_type')
            tap.eq(rec2.ctx['method'], 'POST', 'response method')
            tap.eq(rec2.ctx['uri'], '/', 'response uri')
            tap.ok(rec2.ctx['meta_code'], 200, 'response code')
            tap.ok(rec2.ctx['total_time'], 'response time')
            tap.eq(
                # json_response добавляет кавычки
                rec2.ctx['body'],
                '"' + 'a' * (5 * 1024 - 1),
                'response body'
            )

            tap.eq(rec1.ctx['link'], rec2.ctx['link'], 'links are equal')
