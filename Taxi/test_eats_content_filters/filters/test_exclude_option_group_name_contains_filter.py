# pylint: disable=E0401,C5521
import pytest

# pylint: disable=W0612,C0103
from eats_content_filters.filters import ExcludeOptionGroupNameContainsFilter


@pytest.mark.parametrize(
    'black_list, file_name, result_file_name',
    [
        (
            ['Двигается очень быстро', 'Крепкая ручка'],
            'menu_option.json',
            'result_option_all_black_list.json',
        ),
        (['нет совпадений'], 'menu_option.json', 'menu_option.json'),
    ],
)
async def test_exclude_option_group_name_contains_filter(
        load_json, black_list, file_name, result_file_name,
):
    menu = load_json(file_name)
    handler = ExcludeOptionGroupNameContainsFilter(black_list)
    handler.content_filter(menu)
    assert menu == load_json(result_file_name)
