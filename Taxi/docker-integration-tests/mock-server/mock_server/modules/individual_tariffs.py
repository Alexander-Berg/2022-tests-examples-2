import json
import os

from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/internal/v1/tariffs/list', self.v1_tariffs_list)

    @staticmethod
    async def v1_tariffs_list(request):
        return Application._respond_json('static/tariffs.json')

    @staticmethod
    def _respond_json(json_filename):
        dir_ = os.path.dirname(__file__)
        with open(os.path.join(dir_, json_filename)) as file_:
            return web.json_response(json.load(file_))
