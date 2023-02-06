import json
import os

from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/geoareas/v1/tariff-areas', self.handle_list)
        self.router.add_get(
            '/subvention-geoareas/v1/geoareas', self.handle_sg_list,
        )

    @staticmethod
    def handle_list(request):
        return Application._respond_json('static/geoareas.json')

    @staticmethod
    def handle_sg_list(request):
        return Application._respond_json('static/subvention_geoareas.json')

    @staticmethod
    def _respond_json(json_filename):
        dir_ = os.path.dirname(__file__)
        with open(os.path.join(dir_, json_filename)) as file_:
            return web.json_response(json.load(file_))
