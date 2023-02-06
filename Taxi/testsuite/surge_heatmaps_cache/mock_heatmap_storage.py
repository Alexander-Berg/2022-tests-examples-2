# pylint: disable=unused-import, import-only-modules, import-error
# pylint: disable=invalid-name, unused-variable, wrong-import-order
# pylint: disable=too-many-statements
import copy
import datetime

import flatbuffers
from heatmaps import Box
from heatmaps import HexGrid
from heatmaps import HexGridValueMap
from heatmaps import ValueCell
from heatmaps import ValueHexGrid
from heatmaps.cell.extra.surge import PinInfo
from heatmaps.grid.extra.surge import GridExtra
from lxml import etree
import pytest

DEFAULT_SURGE_MAP = {
    'grids': [
        {
            'hex_grid': {
                'cell_size_meter': 500.123,
                'envelope': {'br': [35.15, 58.12], 'tl': [32.15, 51.12]},
            },
            'values': [],
        },
    ],
}
S3MOCKHANDLE = '/heatmap-mds-s3'

_SURGE_HEATMAP_MARKER = 'surge_heatmap'


def _to_basic_iso(dt: datetime.datetime):
    td = dt.utcoffset() or datetime.timedelta()
    return dt.strftime(
        '%Y-%m-%dT%H:%M:%S{}{:02d}{:02d}'.format(
            '-' if td < datetime.timedelta() else '+',
            td.seconds // 3600,
            td.seconds // 60,
        ),
    )


def create_surge_map(values, envelope, cell_size_meter, grid_extra=None):
    result = copy.deepcopy(DEFAULT_SURGE_MAP)
    grid = result['grids'][0]
    hex_grid = grid['hex_grid']
    hex_grid['cell_size_meter'] = cell_size_meter
    hex_grid['envelope'] = envelope
    grid['values'] = values
    if grid_extra:
        grid['grid_extra'] = grid_extra
    return result


class SurgeHeatmapsContext:
    def __init__(self):
        self.surge_map = DEFAULT_SURGE_MAP
        self.layer_suffix = ''
        self.created = datetime.datetime.utcnow()

    def set_surge_map(self, surge_map):
        self.surge_map = surge_map

    def build_and_set_surge_map(
            self,
            values,
            envelope,
            cell_size_meter,
            created=None,
            grid_extra=None,
    ):
        self.surge_map = create_surge_map(
            values, envelope, cell_size_meter, grid_extra,
        )
        if isinstance(created, datetime.datetime):
            self.created = created

    def reset_surge_map(self):
        self.set_surge_map(DEFAULT_SURGE_MAP)

    def set_layer_suffix(self, suffix: str):
        self.layer_suffix = suffix


def _serialize_pin_info(pin_info):
    builder = flatbuffers.Builder(0)

    PinInfo.PinInfoStart(builder)
    PinInfo.PinInfoAddAvgCost(builder, pin_info['avg_cost'])
    PinInfo.PinInfoAddCostCount(builder, pin_info['cost_count'])
    PinInfo.PinInfoAddPins(builder, pin_info['pins_count'])
    obj = PinInfo.PinInfoEnd(builder)
    builder.Finish(obj)

    return bytes(builder.Output())


def _serialize_grid_extra(grid_extra):
    builder = flatbuffers.Builder(0)

    base_class_fbs = builder.CreateString(
        grid_extra.get('base_class', 'econom'),
    )
    GridExtra.GridExtraStart(builder)
    GridExtra.GridExtraAddBaseClass(builder, base_class_fbs)
    GridExtra.GridExtraAddPins(builder, grid_extra.get('pins', 0))
    GridExtra.GridExtraAddPinsOrder(builder, grid_extra.get('pins_order', 0))
    GridExtra.GridExtraAddPinsDriver(builder, grid_extra.get('pins_driver', 0))
    GridExtra.GridExtraAddFree(builder, grid_extra.get('free', 0))
    GridExtra.GridExtraAddFreeChain(builder, grid_extra.get('free_chain', 0))
    GridExtra.GridExtraAddTotal(builder, grid_extra.get('total', 0))
    GridExtra.GridExtraAddSurge(builder, grid_extra.get('surge', 0))
    obj = GridExtra.GridExtraEnd(builder)
    builder.Finish(obj)

    return bytes(builder.Output())


def pytest_configure(config):
    config.addinivalue_line(
        'markers', f'{_SURGE_HEATMAP_MARKER}: surge heatmap',
    )


@pytest.fixture(autouse=True)
def enumerate_crutch_fixture(mockserver):
    @mockserver.json_handler('/heatmap-storage/v1/enumerate_keys')
    def _mock_enumerate_keys(request):
        return 'not implemented'


@pytest.fixture(name='heatmap_storage')
def _heatmap_storage(mockserver, request):
    maps_context = SurgeHeatmapsContext()

    def _build_surge_map_fb(data):
        builder = flatbuffers.Builder(0)
        grids = data['grids']
        for grid in grids:
            for val in grid['values']:
                fbs_pin_info = None
                if 'pin_info' in val:
                    data = _serialize_pin_info(val['pin_info'])
                    data_len = len(data)

                    ValueCell.ValueCellStartExtraVector(builder, data_len)
                    for i in reversed(data):
                        builder.PrependByte(i)
                    fbs_pin_info = builder.EndVector(data_len)

                ValueCell.ValueCellStart(builder)
                ValueCell.ValueCellAddX(builder, val['x'])
                ValueCell.ValueCellAddY(builder, val['y'])
                ValueCell.ValueCellAddValue(builder, val['surge'])
                ValueCell.ValueCellAddWeight(builder, val['weight'])
                if fbs_pin_info:
                    ValueCell.ValueCellAddExtra(builder, fbs_pin_info)

                val['fbs'] = ValueCell.ValueCellEnd(builder)

            ValueHexGrid.ValueHexGridStartValuesVector(
                builder, len(grid['values']),
            )
            for value in grid['values']:
                builder.PrependUOffsetTRelative(value['fbs'])

            grid['fbs_values'] = builder.EndVector(len(grid['values']))

        for grid in grids:
            fbs_grid_extra = None
            if 'grid_extra' in grid:
                data = _serialize_grid_extra(grid['grid_extra'])
                data_len = len(data)

                HexGrid.HexGridStartExtraVector(builder, data_len)
                for i in reversed(data):
                    builder.PrependByte(i)
                fbs_grid_extra = builder.EndVector(data_len)

            HexGrid.HexGridStart(builder)
            HexGrid.HexGridAddEnvelope(
                builder,
                Box.CreateBox(
                    builder,
                    grid['hex_grid']['envelope']['tl'][0],
                    grid['hex_grid']['envelope']['tl'][1],
                    grid['hex_grid']['envelope']['br'][0],
                    grid['hex_grid']['envelope']['br'][1],
                ),
            )
            HexGrid.HexGridAddCellSizeMeter(
                builder, grid['hex_grid']['cell_size_meter'],
            )
            if fbs_grid_extra:
                HexGrid.HexGridAddExtra(builder, fbs_grid_extra)

            grid['fbs_hex_grid'] = HexGrid.HexGridEnd(builder)

        for grid in grids:
            ValueHexGrid.ValueHexGridStart(builder)
            ValueHexGrid.ValueHexGridAddHexGrid(builder, grid['fbs_hex_grid'])
            ValueHexGrid.ValueHexGridAddValues(builder, grid['fbs_values'])
            grid['fbs'] = ValueHexGrid.ValueHexGridEnd(builder)

        HexGridValueMap.HexGridValueMapStartGridsVector(builder, len(grids))

        for grid in grids:
            builder.PrependUOffsetTRelative(grid['fbs'])
        grids = builder.EndVector(len(grids))

        HexGridValueMap.HexGridValueMapStart(builder)
        HexGridValueMap.HexGridValueMapAddGrids(builder, grids)
        surge_value_map = HexGridValueMap.HexGridValueMapEnd(builder)
        builder.Finish(surge_value_map)
        return builder.Output()

    def s3_list_objects_xml(content_keys, max_keys, marker):
        result = etree.Element('ListBucketResult')

        is_truncated = etree.Element('IsTruncated')
        is_truncated.text = 'false'
        result.append(is_truncated)

        marker_elem = etree.Element('Marker')
        marker_elem.text = marker
        result.append(marker_elem)

        max_keys_elem = etree.Element('MaxKeys')
        max_keys_elem.text = str(max_keys)
        result.append(max_keys_elem)

        name = etree.Element('Name')
        name.text = 'heatmap'
        result.append(name)

        for key in content_keys:
            contents = etree.Element('Contents')

            key_elem = etree.Element('Key')
            key_elem.text = key
            contents.append(key_elem)

            # s3api library reads Size
            size_elem = etree.Element('Size')
            size_elem.text = '1'
            contents.append(size_elem)

            result.append(contents)

        return etree.tostring(result, xml_declaration=True, encoding='UTF-8')

    def s3_list_objects(request):
        assert request.method == 'GET'

        # list objects
        assert request.path[len(f'{S3MOCKHANDLE}/') :] == ''

        max_keys = int(request.query.get('max_keys', '1000'))
        assert max_keys <= 1000

        marker = request.query.get('marker', '')

        suffix = maps_context.layer_suffix
        content_type = request.query['prefix']

        assert content_type and content_type[-1] == '/'
        content_type = content_type[:-1]

        keys = [
            f'taxi_surge_{content_type}/econom/default{suffix}',
            f'taxi_surge_{content_type}/__default__/default{suffix}',
        ]

        return mockserver.make_response(
            response=s3_list_objects_xml(keys, max_keys, marker), status=200,
        )

    def s3_get(request):
        if request.method == 'GET':
            return mockserver.make_response(
                response=_build_surge_map_fb(maps_context.surge_map),
                status=200,
                headers={
                    'X-Amz-Meta-Heatmapcompression': 'none',
                    'X-Amz-Meta-Heatmaptype': 'hex_grid',
                    'X-Amz-Meta-Created': _to_basic_iso(maps_context.created),
                    'X-Amz-Meta-Expires': '2119-01-02T04:00:00+0000',
                    'X-Amz-Version-Id': '1',
                },
            )

        assert request.method == 'HEAD'

        return mockserver.make_response(
            headers={
                'X-Amz-Meta-Heatmapcompression': 'none',
                'X-Amz-Meta-Heatmaptype': 'hex_grid',
                'X-Amz-Meta-Created': _to_basic_iso(maps_context.created),
                'X-Amz-Meta-Expires': '2119-01-02T04:00:00+0000',
                'X-Amz-Version-Id': '1',
            },
        )

    @mockserver.handler(S3MOCKHANDLE, prefix=True)
    def _mock_request_s3(request):
        if request.method == 'GET' or request.method == 'HEAD':
            if request.path == f'{S3MOCKHANDLE}/':
                return s3_list_objects(request)

            return s3_get(request)

        return mockserver.make_response('No suitable handler', 500)

    @mockserver.json_handler('/heatmap-storage/v1/enumerate_keys')
    def _mock_enumerate_keys(request):
        suffix = maps_context.layer_suffix
        content_type = request.query['content_type']
        return mockserver.make_response(
            json={
                'content_keys': [
                    f'taxi_surge_{content_type}/econom/default{suffix}',
                    f'taxi_surge_{content_type}/__default__/default{suffix}',
                ],
            },
        )

    @mockserver.json_handler('/heatmap-storage/v1/get_actual_map_metadata')
    def _mock_get_actual_map_metadata(request):
        return mockserver.make_response(
            json={
                'id': 1,
                'created': _to_basic_iso(maps_context.created),
                'expires': '2119-01-02T00:00:00+0000',
                'heatmap_type': 'hex_grid',
            },
        )

    @mockserver.handler('/heatmap-storage/v1/get_map')
    def _mock_hs_get_map(request):
        key = f'taxi_surge_full/econom/default{maps_context.layer_suffix}'
        return mockserver.make_response(
            _build_surge_map_fb(maps_context.surge_map),
            headers={
                'Created': _to_basic_iso(maps_context.created),
                'Expires': '2119-01-02T04:00:00+0000',
                'X-YaTaxi-Heatmap-Type': 'hex_grid',
                'X-YaTaxi-Heatmap-Content-Key': key,
            },
            content_type='application/x-flatbuffers',
        )

    return maps_context


@pytest.fixture(name='heatmap_storage_fixture', autouse=False)
def _heatmap_storage_fixture(heatmap_storage, s3_heatmap_storage, request):
    marker = request.node.get_closest_marker(_SURGE_HEATMAP_MARKER)
    if marker:
        if marker.name == _SURGE_HEATMAP_MARKER:
            heatmap_storage.build_and_set_surge_map(**marker.kwargs)
        else:
            print('MARKER: ', marker)
            assert False

    yield heatmap_storage
