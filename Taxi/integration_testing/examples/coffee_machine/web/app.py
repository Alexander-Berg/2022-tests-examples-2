import aiohttp
from aiohttp import web


def main():
    async def ping(request):
        return web.Response(text='OK')

    async def echo(request):
        msg = request.query.get('msg')
        return web.Response(text=str(msg))

    async def post_cups_dispose(request):
        async with aiohttp.ClientSession(base_url='http://coffee-cups.test.yandex.net') as session:
            response = await session.post('/cups/dispose')
            response.raise_for_status()

        return web.Response(status=204)

    app = web.Application()
    app.router.add_get('/ping', ping)
    app.router.add_get('/echo', echo)
    app.router.add_post('/cups/dispose', post_cups_dispose)
    web.run_app(app, port=80)


if __name__ == '__main__':
    main()
