from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/blocklist/v1/list', self.handle_list)

    @staticmethod
    def handle_list(request):
        return web.json_response({'blocks': [], 'revision': '0'})
