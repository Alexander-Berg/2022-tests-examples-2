from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/v1/transport-available/updates', self.empty_json)
        self.router.add_get('/v1/transport-active/updates', self.empty_json)
        self.router.add_post(
            '/v1/transport-active/retrieve-by-contractor-id', self.empty_json,
        )

    @staticmethod
    def empty_json(request):
        return web.json_response(
            {'contractors_transport': [], 'cursor': '1234567_4'},
        )
