import collections

import pytest

from tests_heatmap_renderer import common


@pytest.fixture(name='heatmap_storage', autouse=True)
def _heatmap_storage(mockserver):
    MapData = collections.namedtuple(
        'MapData',
        [
            'map_id',
            'created',
            'expires',
            'map_type',
            'content_key',
            'map_data',
        ],
    )

    class StorageContext:
        def __init__(self):
            self.actual_maps = {}
            self.maps = {}

        def get_actual_map(self, content_key):
            actual_map_id = self.actual_maps.get(content_key)
            if actual_map_id is None:
                return None
            return self.maps.get(int(actual_map_id))

        def add_map(
                self,
                content,
                map_id,
                created,
                expires,
                map_type,
                map_data=None,
                serialized_map=None,
        ):
            if map_data is None:
                map_data = common.DEFAULT_HEX_MAP
            self.maps[int(map_id)] = MapData(
                map_id,
                created,
                expires,
                map_type,
                content,
                serialized_map or common.build_hex_grid_fb(map_data),
            )
            self.actual_maps[content] = int(map_id)

        def get_map(self, map_id):
            return self.maps.get(int(map_id))

    context = StorageContext()

    @mockserver.handler('/heatmap-storage/v1/get_actual_map_metadata')
    def _mock_get_actual_map_metadata(request):
        content = request.args['content_key']

        actual_map = context.get_actual_map(content)
        if actual_map is None:
            return mockserver.make_response(
                json={
                    'message': 'No map of type {}'.format(content),
                    'code': 'NOT_FOUND',
                },
                headers={'X-YaTaxi-Error-Code': 'NOT_FOUND'},
                status=404,
            )

        return mockserver.make_response(
            json={
                'id': actual_map.map_id,
                'created': actual_map.created,
                'expires': actual_map.expires,
                'heatmap_type': actual_map.map_type,
            },
            status=200,
        )

    @mockserver.handler('/heatmap-storage/v1/get_map')
    def _mock_get_map(request):
        map_id = request.args['id']

        res = context.get_map(map_id)
        if res is None:
            return mockserver.make_response(
                response='NOT_FOUND_{}'.format(map_id), status=404,
            )

        return mockserver.make_response(
            response=res.map_data,
            status=200,
            headers={
                'Created': res.created,
                'Expires': res.expires,
                'X-YaTaxi-Heatmap-Type': res.map_type,
                'X-YaTaxi-Heatmap-Content-Key': res.content_key,
                'Content-Type': 'application/x-flatbuffers',
            },
        )

    return context
