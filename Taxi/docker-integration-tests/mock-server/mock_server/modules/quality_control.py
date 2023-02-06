from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/api/v1/state/list', self.handle_state_list)

    @staticmethod
    def handle_state_list(request):
        return web.json_response({
            'cursor': 'cursor',
            'items': [],
            'modified': '2021-01-01T03:00:00+03:00',
        })
