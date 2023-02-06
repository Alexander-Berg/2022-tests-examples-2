from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/1/track/', self.handle_track)
        self.router.add_post('/1/bundle/phone/confirm/submit/',
                             self.handle_confirm_submit)
        self.router.add_post('/1/bundle/phone/confirm/commit/',
                             self.handle_confirm_commit)

    async def handle_track(self, request):
        return web.json_response(
            {
                'status': 'ok',
                'id': '1',
            },
        )

    async def handle_confirm_submit(self, request):
        return web.json_response(
            {
                'status': 'ok',
                'track_id': '1',
                'number': {
                    'e164': '+70000000000',
                    'original': '+7000000000',
                },
            },
        )

    async def handle_confirm_commit(self, request):
        return web.json_response(
            {
                'status': 'ok',
                'number': {
                    'e164': '+70000000000',
                    'original': '+7000000000',
                },
            },
        )
