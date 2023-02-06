from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/v1/service/get/', self.service_get)
        self.router.add_get('/balancers/v1/service/get/', self.service_get)

    @staticmethod
    def service_get(request):
        return web.json_response({'namespaces': []})
