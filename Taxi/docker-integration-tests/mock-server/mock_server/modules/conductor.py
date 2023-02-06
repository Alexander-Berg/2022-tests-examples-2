from aiohttp import web

_REPOSITION_HOST = 'reposition.taxi.yandex.net'
_DRIVER_DISPATCHER_HOST = 'driver-dispatcher.taxi.yandex.net'


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/api/hosts/' + _REPOSITION_HOST,
                            self.handle_api_hosts)
        self.router.add_get('/api/hosts/' + _DRIVER_DISPATCHER_HOST,
                            self.handle_api_hosts)

    @staticmethod
    def handle_api_hosts(request):
        return web.json_response([{
            'fqdn': 'test.fqdn',
            'root_datacenter_name': 'test',
        }])
