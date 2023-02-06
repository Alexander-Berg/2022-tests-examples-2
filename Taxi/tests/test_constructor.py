from taxi_dashboards import constructor


def test_assign_coordinates():
    input_panels = [
        {'type': 'row'},
        {'type': 'graph'},
        {'type': 'graph'},
        {'type': 'row'},
        {'type': 'graph'},
        {'type': 'graph'},
        {'type': 'graph'},
        {'type': 'row', '$ROW_PANELS': 1},
        {'type': 'graph'},
        {'type': 'graph'},
        {'type': 'row', '$ROW_PANELS': 3},
        {'type': 'graph'},
        {'type': 'graph'},
        {'type': 'graph'},
        {'type': 'graph'},
        {'type': 'graph'},
    ]
    expected_coord = [
        {'h': 1, 'w': 24, 'x': 0, 'y': 0},
        {'h': 7, 'w': 8, 'x': 0, 'y': 1},
        {'h': 7, 'w': 8, 'x': 8, 'y': 1},
        {'h': 1, 'w': 24, 'x': 0, 'y': 8},
        {'h': 7, 'w': 8, 'x': 0, 'y': 9},
        {'h': 7, 'w': 8, 'x': 8, 'y': 9},
        {'h': 7, 'w': 8, 'x': 16, 'y': 9},
        {'h': 1, 'w': 24, 'x': 0, 'y': 16},
        {'h': 7, 'w': 24, 'x': 0, 'y': 17},
        {'h': 7, 'w': 24, 'x': 0, 'y': 24},
        {'h': 1, 'w': 24, 'x': 0, 'y': 31},
        {'h': 7, 'w': 8, 'x': 0, 'y': 32},
        {'h': 7, 'w': 8, 'x': 8, 'y': 32},
        {'h': 7, 'w': 8, 'x': 16, 'y': 32},
        {'h': 7, 'w': 8, 'x': 0, 'y': 39},
        {'h': 7, 'w': 8, 'x': 8, 'y': 39},
    ]
    constructor.assign_coordinates(input_panels)

    assert [panel['gridPos'] for panel in input_panels] == expected_coord
