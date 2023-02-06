from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v1/locks/acquire/', self.acquire)
        self.router.add_post('/v1/locks/release/', self.release)

    async def acquire(self, request):
        data = await request.json()
        return web.json_response(
            {
                'status': 'acquired',
                'namespace': data['namespace'],
                'name': data['name'],
                'owner': data['owner'],
            },
        )

    async def release(self, _):
        return web.json_response({})
