from ctaxi_pyml.blender import v1 as blender
from ctaxi_pyml.blender.v1 import organic

import json


def cell_to_str(cell):
    return '{scenario}[{rank}]:{width}:({min_width})'.format(
        scenario=cell.shortcut.scenario,
        rank=cell.shortcut.rank,
        width=cell.size.width,
        min_width=cell.shortcut.min_width,
    )


def print_line(cells):
    print('   '.join(map(cell_to_str, cells)))


def print_grid(grid):
    cur_line = []
    cur_line_width = 0
    for cell in grid.cells:
        cur_line.append(cell)
        cur_line_width += cell.size.width
        assert cur_line_width <= grid.width
        if cur_line_width == grid.width:
            print_line(cur_line)
            cur_line = []
            cur_line_width = 0


def test_smoke(load):
    prev_state = blender.State.from_json(load('request.json'))
    alg = organic.Organic(organic.OrganicConfig.from_json(load('config.json')))

    next_state = alg(prev_state)
    blender.validate_blending(prev_state, next_state)
    assert len(next_state.grid.cells) != len(prev_state.grid.cells)


def gen_request(scenario_to_min_widths):
    return {
        'tops': [
            {
                'scenario': scenario,
                'shortcuts': [
                    {
                        'id': f'{scenario}:{rank}',
                        'scenario': scenario,
                        'rank': rank,
                        'min_width': min_width,
                        'min_height': 1,
                        'max_width': 6,
                    }
                    for rank, min_width in enumerate(min_widths)
                ],
            }
            for scenario, min_widths in scenario_to_min_widths.items()
        ],
        'grid': {
            'id': 'grid_id',
            'width': 6,
            'supported_cell_widths': [2, 3, 4],
            'cells': [],
            'blocks': [],
        },
        'context': {
            'scenario_predictions': [],
            'pin_position': [0, 0],
            'time': '2020-01-09T17:18:19.000000Z',
            'known_orders': [],
        },
        'meta': {},
    }


def test_easy_request(load, layout_checker):
    req = json.dumps(
        gen_request(
            {
                'taxi_expected_destination': [2, 2, 4],
                'eats_place': [2, 2],
                'grocery_category': [2, 2],
            },
        ),
    )
    prev_state = blender.State.from_json(req)
    alg = organic.Organic(organic.OrganicConfig.from_json(load('config.json')))

    next_state = alg(prev_state)
    blender.validate_blending(prev_state, next_state)
    assert len(next_state.grid.cells) != len(prev_state.grid.cells)

    layout_checker.check(next_state.grid)


def test_mass_random(
        load, layout_checker, rank_switch_checker, random_request_generator,
):
    for request in random_request_generator(100):
        prev_state = blender.State.from_json(json.dumps(request))
        alg = organic.Organic(
            organic.OrganicConfig.from_json(load('config.json')),
        )

        next_state = alg(prev_state)
        blender.validate_blending(prev_state, next_state)
        assert len(next_state.grid.cells) != len(prev_state.grid.cells)

        layout_checker.check(next_state.grid)
        rank_switch_checker.check(
            next_state.grid, 'taxi_expected_destination', 0,
        )
        rank_switch_checker.check(next_state.grid, 'eats_place', 2)
        rank_switch_checker.check(next_state.grid, 'grocery_category', 2)
