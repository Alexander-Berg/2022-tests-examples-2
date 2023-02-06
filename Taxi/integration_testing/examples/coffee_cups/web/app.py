from aiohttp import web


def main():
    num_cups = 3

    async def get_ping(request):
        return web.Response(text='OK')

    async def get_echo(request):
        msg = request.query.get('msg')
        return web.Response(text=str(msg))

    async def get_cups(request):
        nonlocal num_cups
        return web.json_response({
            'num_cups': num_cups
        })

    async def post_cups_dispose(request):
        nonlocal num_cups
        num_cups -= 1
        return web.Response(status=204)

    app = web.Application()
    app.router.add_get('/ping', get_ping)
    app.router.add_get('/echo', get_echo)
    app.router.add_get('/cups', get_cups)
    app.router.add_post('/cups/dispose', post_cups_dispose)
    web.run_app(app, port=80)


if __name__ == '__main__':
    main()
