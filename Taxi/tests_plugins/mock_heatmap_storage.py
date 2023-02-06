import copy

import flatbuffers
import pytest
import werkzeug

from fbs.heatmaps import Box as HeatmapBox
from fbs.heatmaps import HexGrid as HeatmapHexGrid
from fbs.heatmaps import HexGridValueMap as HeatmapHexGridValueMap
from fbs.heatmaps import ValueCell as HeatmapValueCell
from fbs.heatmaps import ValueHexGrid as HeatmapValueHexGrid
from fbs.heatmaps.cell.extra.surge import PinInfo as HeatmapPinInfo
from fbs.heatmaps.grid.extra.surge import GridExtra as HeatmapGridExtra

DEFAULT_SURGE_MAP = {
    'grids': [
        {
            'hex_grid': {
                'base_class': 'econom',
                'cell_size_meter': 500.123,
                'envelope': {'br': [35.15, 58.12], 'tl': [32.15, 51.12]},
            },
            'values': [{'category': '__default__', 'values': []}],
        },
    ],
}


def create_surge_map(values, envelope, cell_size_meter):
    result = copy.deepcopy(DEFAULT_SURGE_MAP)
    hex_grid = result['grids'][0]['hex_grid']
    hex_grid['cell_size_meter'] = cell_size_meter
    hex_grid['envelope'] = envelope
    result['grids'][0]['values'][0]['values'] = values
    return result


class SurgeMapsContext:
    def __init__(self):
        self.surge_map = DEFAULT_SURGE_MAP
        self.map_id = 7

    def set_surge_map(self, surge_map):
        self.surge_map = surge_map
        self.map_id += 1

    def build_and_set_surge_map(self, values, envelope, cell_size_meter):
        self.surge_map = create_surge_map(values, envelope, cell_size_meter)
        self.map_id += 1

    def reset_surge_map(self):
        self.set_surge_map(DEFAULT_SURGE_MAP)
        self.map_id += 1

    def reset_maps(self):
        self.reset_surge_map()


def _heatmap_serialize_pin_info(pin_info):
    builder = flatbuffers.Builder(0)

    HeatmapPinInfo.PinInfoStart(builder)
    HeatmapPinInfo.PinInfoAddAvgCost(builder, pin_info['avg_cost'])
    HeatmapPinInfo.PinInfoAddCostCount(builder, pin_info['cost_count'])
    HeatmapPinInfo.PinInfoAddPins(builder, pin_info['pins_count'])
    obj = HeatmapPinInfo.PinInfoEnd(builder)
    builder.Finish(obj)

    return bytes(builder.Output())


def _heatmap_serialize_grid_extra(grid_extra):
    builder = flatbuffers.Builder(0)

    base_class_fbs = builder.CreateString(
        grid_extra.get('base_class', 'econom'),
    )
    HeatmapGridExtra.GridExtraStart(builder)
    HeatmapGridExtra.GridExtraAddBaseClass(builder, base_class_fbs)
    HeatmapGridExtra.GridExtraAddPins(builder, grid_extra.get('pins', 0))
    HeatmapGridExtra.GridExtraAddPinsOrder(
        builder, grid_extra.get('pins_order', 0),
    )
    HeatmapGridExtra.GridExtraAddPinsDriver(
        builder, grid_extra.get('pins_driver', 0),
    )
    HeatmapGridExtra.GridExtraAddFree(builder, grid_extra.get('free', 0))
    HeatmapGridExtra.GridExtraAddFreeChain(
        builder, grid_extra.get('free_chain', 0),
    )
    HeatmapGridExtra.GridExtraAddTotal(builder, grid_extra.get('total', 0))
    HeatmapGridExtra.GridExtraAddSurge(builder, grid_extra.get('surge', 0))
    obj = HeatmapGridExtra.GridExtraEnd(builder)
    builder.Finish(obj)

    return bytes(builder.Output())


def _heatmap_build_surge_map_fb(data):
    builder = flatbuffers.Builder(0)
    grids = data['grids']
    for grid in grids:
        for val in grid['values'][0]['values']:
            fbs_pin_info = None
            if 'pin_info' in val:
                data = _heatmap_serialize_pin_info(val['pin_info'])
                data_len = len(data)

                HeatmapValueCell.ValueCellStartExtraVector(builder, data_len)
                for i in reversed(data):
                    builder.PrependByte(i)
                fbs_pin_info = builder.EndVector(data_len)

            HeatmapValueCell.ValueCellStart(builder)
            HeatmapValueCell.ValueCellAddX(builder, val['x'])
            HeatmapValueCell.ValueCellAddY(builder, val['y'])
            HeatmapValueCell.ValueCellAddValue(builder, val['surge'])
            HeatmapValueCell.ValueCellAddWeight(builder, val['weight'])
            if fbs_pin_info:
                HeatmapValueCell.ValueCellAddExtra(builder, fbs_pin_info)

            val['fbs'] = HeatmapValueCell.ValueCellEnd(builder)

        HeatmapValueHexGrid.ValueHexGridStartValuesVector(
            builder, len(grid['values'][0]['values']),
        )
        for value in grid['values'][0]['values']:
            builder.PrependUOffsetTRelative(value['fbs'])

        grid['fbs_values'] = builder.EndVector(
            len(grid['values'][0]['values']),
        )

    for grid in grids:
        fbs_grid_extra = None
        if 'grid_extra' in grid:
            data = _heatmap_serialize_grid_extra(grid['grid_extra'])
            data_len = len(data)

            HeatmapHexGrid.HexGridStartExtraVector(builder, data_len)
            for i in reversed(data):
                builder.PrependByte(i)
            fbs_grid_extra = builder.EndVector(data_len)

        HeatmapHexGrid.HexGridStart(builder)
        HeatmapHexGrid.HexGridAddEnvelope(
            builder,
            HeatmapBox.CreateBox(
                builder,
                grid['hex_grid']['envelope']['tl'][0],
                grid['hex_grid']['envelope']['tl'][1],
                grid['hex_grid']['envelope']['br'][0],
                grid['hex_grid']['envelope']['br'][1],
            ),
        )
        HeatmapHexGrid.HexGridAddCellSizeMeter(
            builder, grid['hex_grid']['cell_size_meter'],
        )
        if fbs_grid_extra:
            HeatmapHexGrid.HexGridAddExtra(builder, fbs_grid_extra)

        grid['fbs_hex_grid'] = HeatmapHexGrid.HexGridEnd(builder)

    for grid in grids:
        HeatmapValueHexGrid.ValueHexGridStart(builder)
        HeatmapValueHexGrid.ValueHexGridAddHexGrid(
            builder, grid['fbs_hex_grid'],
        )
        HeatmapValueHexGrid.ValueHexGridAddValues(builder, grid['fbs_values'])
        grid['fbs'] = HeatmapValueHexGrid.ValueHexGridEnd(builder)

    HeatmapHexGridValueMap.HexGridValueMapStartGridsVector(builder, len(grids))

    for grid in grids:
        builder.PrependUOffsetTRelative(grid['fbs'])
    grids = builder.EndVector(len(grids))

    HeatmapHexGridValueMap.HexGridValueMapStart(builder)
    HeatmapHexGridValueMap.HexGridValueMapAddGrids(builder, grids)
    surge_value_map = HeatmapHexGridValueMap.HexGridValueMapEnd(builder)
    builder.Finish(surge_value_map)
    return builder.Output()


@pytest.fixture(autouse=True)
def heatmap_storage(mockserver, request):
    maps_context = SurgeMapsContext()

    @mockserver.json_handler('/heatmap-storage/v1/enumerate_keys')
    def _mock_heatmap_storage_enumerate(request):
        return {
            'content_keys': [
                'taxi_surge_full/__default__/default_samples',
                'taxi_surge_full/econom/default_samples',
            ],
        }

    @mockserver.json_handler('/heatmap-storage/v1/get_actual_map_metadata')
    def _mock_heatmap_storage_meta(request):
        return {
            'id': maps_context.map_id,
            'created': '2020-01-01T01:00:00+0300',
            'expires': '2020-01-01T01:00:00+0300',
            'heatmap_type': 'hex_grid',
        }

    @mockserver.handler('/heatmap-storage/v1/get_map')
    def _mock_heatmap_storage_get_map(request):
        return werkzeug.Response(
            _heatmap_build_surge_map_fb(maps_context.surge_map),
            content_type='application/x-flatbuffers',
        )

    if request.node.get_marker('surge_value_map'):
        for marker in request.node.get_marker('surge_value_map'):
            maps_context.set_surge_map(create_surge_map(**marker.kwargs))

    return maps_context
