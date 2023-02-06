import json
import os

from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/api/v3', self.handle_api_v3)
        self.router.add_get('/hosts', self.handle_hosts)
        self.router.add_put('/api/v3/lookup_rows', self.handle_lookup_rows)

    @staticmethod
    def handle_api_v3(request):
        dir_ = os.path.dirname(__file__)
        with open(os.path.join(dir_, 'static/yt_api_v3.json')) as fle:
            return web.json_response(json.load(fle))

    @staticmethod
    def handle_hosts(request):
        return web.json_response(['seneca-man.yt.yandex.net'])

    @staticmethod
    def handle_lookup_rows(request):
        return web.Response()
