# pylint: disable=import-error, no-name-in-module
import json

import fbs.heatmap_sample_storage.Samples as FbsSamples
from heatmaps import GeoPoint
from heatmaps import HexGridValueMap
from heatmaps.cell.extra.surge import PinInfo
from heatmaps.grid.extra.surge import GridExtra


def build_sample(
        longitude,
        latitude,
        sample_type,
        map_name,
        value,
        weight,
        meta,
        created=1552003200000,
):
    result = json.dumps(
        {
            'created': created,
            'sample': {
                'map_name': map_name,
                'meta': meta,
                'point': {'lat': latitude, 'lon': longitude},
                'type': sample_type,
                'value': value,
                'weight': weight,
            },
        },
    )
    return result


def parse_samples(data):
    response = FbsSamples.Samples.GetRootAsSamples(data, 0)
    samples = []
    for i in range(0, response.SamplesLength()):
        samples.append(response.Samples(i))
    return samples


def parse_pin_info(pin_info_bytes):
    pin_info_fb = PinInfo.PinInfo.GetRootAsPinInfo(pin_info_bytes, 0)
    return {
        'avg_cost': pin_info_fb.AvgCost(),
        'cost_count': pin_info_fb.CostCount(),
        'pins': pin_info_fb.Pins(),
        'free': pin_info_fb.Free(),
        'free_chain': pin_info_fb.FreeChain(),
        'total': pin_info_fb.Total(),
        'found_share': pin_info_fb.FoundShare(),
    }


def parse_grid_extra(grid_extra_bytes):
    if isinstance(grid_extra_bytes, int):
        return None
    grid_extra_fb = GridExtra.GridExtra.GetRootAsGridExtra(grid_extra_bytes, 0)
    return {
        'base_class': grid_extra_fb.BaseClass(),
        'pins': round(grid_extra_fb.Pins(), 3),
        'pins_order': round(grid_extra_fb.PinsOrder(), 3),
        'pins_driver': round(grid_extra_fb.PinsDriver(), 3),
        'free': round(grid_extra_fb.Free(), 3),
        'free_chain': round(grid_extra_fb.FreeChain(), 3),
        'total': round(grid_extra_fb.Total(), 3),
        'surge': round(grid_extra_fb.Surge(), 3),
    }


def parse_value_grid(grid_fb):
    hex_grid = grid_fb.HexGrid()
    values = []
    for i in range(grid_fb.ValuesLength()):
        value_fb = grid_fb.Values(i)
        value = {
            'x': value_fb.X(),
            'y': value_fb.Y(),
            'value': round(value_fb.Value(), 3),
            'weight': round(value_fb.Weight(), 3),
        }
        if not isinstance(value_fb.ExtraAsNumpy(), int):
            value['pin_info'] = parse_pin_info(value_fb.ExtraAsNumpy())
        values.append(value)
    values.sort(key=lambda val: 1000 * val['x'] + val['y'])
    tl_fb = GeoPoint.GeoPoint()
    tl_fb = hex_grid.Envelope().Tl(tl_fb)
    br_fb = GeoPoint.GeoPoint()
    br_fb = hex_grid.Envelope().Br(br_fb)

    legend_measurement_units = ''
    if hex_grid.LegendMeasurementUnits():
        legend_measurement_units = hex_grid.LegendMeasurementUnits().decode(
            'utf-8',
        )

    return {
        'hex_grid': {
            'cells_size': hex_grid.CellSizeMeter(),
            'min_value': round(hex_grid.MinValue(), 3),
            'max_value': round(hex_grid.MaxValue(), 3),
            'legend': hex_grid.Legend().decode('utf-8'),
            'legend_precision': hex_grid.LegendPrecision(),
            'legend_measurement_units': legend_measurement_units,
            'tl': {'lon': round(tl_fb.Lon(), 3), 'lat': round(tl_fb.Lat(), 3)},
            'br': {'lon': round(br_fb.Lon(), 3), 'lat': round(br_fb.Lat(), 3)},
            'extra': parse_grid_extra(hex_grid.ExtraAsNumpy()),
        },
        'values': values,
    }


def parse_map(map_fbs):
    value_map = HexGridValueMap.HexGridValueMap.GetRootAsHexGridValueMap(
        map_fbs, 0,
    )
    grids = []
    for i in range(value_map.GridsLength()):
        grids.append(parse_value_grid(value_map.Grids(i)))
    return grids


def diff_calc_surge_cells_stats(lhs, rhs):
    for key, value in rhs['arg'].items():
        lhs['arg'][key] -= value
