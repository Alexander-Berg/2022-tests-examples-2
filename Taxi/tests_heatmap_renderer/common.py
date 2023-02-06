# pylint: disable=import-error

import flatbuffers
from heatmaps import Box
from heatmaps import HexGrid
from heatmaps import HexGridValueMap
from heatmaps import ValueCell
from heatmaps import ValueHexGrid

DEFAULT_HEX_MAP = {
    'grids': [
        {
            'hex_grid': {
                'cell_size_meter': 250,
                'envelope': {
                    'br': [38.077641704627929, 56.003460457113277],
                    'tl': [37.135591841918192, 55.472370163516132],
                },
                'min_value': 0.0,
                'max_value': 5.0,
                'legend': '0 - 5',
                'legend_measurement_units': 'RUR',
                'legend_precision': 0,
            },
            'values': [
                {'x': 182, 'y': 131, 'value': 5.0},
                {'x': 181, 'y': 131, 'value': 3.0},
                {'x': 180, 'y': 131, 'value': 2.0},
                {'x': 179, 'y': 131, 'value': 1.0},
                {'x': 178, 'y': 131, 'value': 0.0},
            ],
        },
    ],
}


def build_hex_grid_fb(data):
    builder = flatbuffers.Builder(0)
    grids = data['grids']
    for grid in grids:
        for value in grid['values']:
            ValueCell.ValueCellStart(builder)
            ValueCell.ValueCellAddX(builder, value['x'])
            ValueCell.ValueCellAddY(builder, value['y'])
            ValueCell.ValueCellAddValue(builder, value['value'])
            value['fbs'] = ValueCell.ValueCellEnd(builder)

        ValueHexGrid.ValueHexGridStartValuesVector(
            builder, len(grid['values']),
        )
        for value in grid['values']:
            builder.PrependUOffsetTRelative(value['fbs'])

        grid['fbs_values'] = builder.EndVector(len(grid['values']))

    for grid in grids:
        legend_fbs = builder.CreateString(grid['hex_grid']['legend'])
        legend_measurement_units_fbs = builder.CreateString(
            grid['hex_grid']['legend_measurement_units'],
        )
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
        HexGrid.HexGridAddMinValue(builder, grid['hex_grid']['min_value'])
        HexGrid.HexGridAddMaxValue(builder, grid['hex_grid']['max_value'])
        HexGrid.HexGridAddLegend(builder, legend_fbs)
        HexGrid.HexGridAddLegendMeasurementUnits(
            builder, legend_measurement_units_fbs,
        )
        HexGrid.HexGridAddLegendPrecision(
            builder, grid['hex_grid']['legend_precision'],
        )

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
    hex_grid_value_map = HexGridValueMap.HexGridValueMapEnd(builder)
    builder.Finish(hex_grid_value_map)
    return builder.Output()


# check if pixels are equal
def pixels_eq(px1, px2):
    assert len(px1) == len(px2) == 4
    # if pixels are fully transparent (alpha == 0)
    # then we should ignore its rgb values
    if px1[3] == px2[3] == 0:
        return True
    return px1 == px2


# calculates fraction of equal pixels
def images_similarity(img1, img2):
    assert img1.size == img2.size == (256, 256)
    assert img1.format == img2.format == 'PNG'
    img1 = img1.convert('RGBA')
    img2 = img2.convert('RGBA')

    cnt = 0
    for x in range(img1.size[0]):
        for y in range(img1.size[1]):
            px1 = img1.getpixel((x, y))
            px2 = img2.getpixel((x, y))
            cnt += 1 if pixels_eq(px1, px2) else 0
    return cnt / float(img1.size[0] * img1.size[1])
