import random
import pytest


def split_to_lines(grid):
    result = []
    current_line = []
    current_width = 0
    for cell in grid.cells:
        current_width += cell.size.width
        current_line.append(cell)
        assert current_width <= grid.width
        if current_width == grid.width:
            result.append(current_line)
            current_line = []
            current_width = 0
    return result


def get_layout(grid):
    return [
        [cell.size.width for cell in line] for line in split_to_lines(grid)
    ]


class LayoutChecker:
    def __init__(self):
        pass

    def check(self, grid, backoff=3):
        layout = get_layout(grid)
        for l_index in range(len(layout)):
            for shift in range(1, backoff + 1):
                if l_index - shift >= 0:
                    assert layout[l_index] != layout[l_index - shift]


@pytest.fixture
def layout_checker():
    return LayoutChecker()


class RankSwitchChecker:
    def __init__(self):
        pass

    def check(self, grid, scenario, max_rank_switch):
        lines = split_to_lines(grid)
        for i in range(len(lines)):
            ranks_before_line = [
                cell.shortcut.rank
                for j in range(i)
                for cell in lines[j]
                if cell.shortcut.scenario == scenario
            ]
            line_ranks = [
                cell.shortcut.rank
                for cell in lines[i]
                if cell.shortcut.scenario == scenario
            ]

            if not ranks_before_line or not line_ranks:
                continue

            assert min(line_ranks) + max_rank_switch >= max(ranks_before_line)


@pytest.fixture
def rank_switch_checker():
    return RankSwitchChecker()


class RandomRequestGenerator:
    def __init__(self):
        pass

    def __call__(self, number):
        random.seed(42)
        for i in range(number):
            yield {
                'tops': [
                    {
                        'scenario': scenario,
                        'shortcuts': [
                            {
                                'id': f'{scenario}:{rank}',
                                'scenario': scenario,
                                'rank': rank,
                                'min_width': random.randint(2, 4),
                                'min_height': 1,
                                'max_width': 6,
                            }
                            for rank in range(random.randint(1, 6))
                        ],
                    }
                    for scenario in [
                        'taxi_expected_destination',
                        'eats_place',
                        'grocery_category',
                    ]
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


@pytest.fixture
def random_request_generator():
    return RandomRequestGenerator()
