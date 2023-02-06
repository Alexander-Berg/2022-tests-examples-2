import json
import os

from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/zones/v2', self.handle_zones)
        self.router.add_get('/batch_zones_filter', self.handle_filter)
        self.router.add_get(
            '/zones/localize', self.handle_localize,
        )

    @staticmethod
    def handle_zones(request):
        return Application._respond_json('static/zones_empty_response.json')

    @staticmethod
    def handle_filter(request):
        data = json.loads(request.get_data())
        results = [{'in_zone': False} for _ in data['points']]
        return web.json_response({'results': results})

    @staticmethod
    def handle_localize(request):
        data = json.loads(request.get_data())
        results = [{} for _ in data['uris']]
        return web.json_response({'results': results})

    @staticmethod
    def _respond_json(json_filename):
        dir_ = os.path.dirname(__file__)
        with open(os.path.join(dir_, json_filename)) as file_:
            return web.json_response(json.load(file_))
