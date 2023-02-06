# pylint: disable=E0401,C5521
import pytest

# pylint: disable=W0612,C0103
from eats_content_filters.filters import ExcludeItemNameContainsFilter


@pytest.mark.parametrize(
    'black_list, file_name, result_file_name',
    [
        (
            [
                'Насадка SESITIVE для PICOBELLO XL',
                'Кувшин БАРЬЕР Чемпион, 4 л',
            ],
            'menu_item.json',
            'result_item_all_black_list.json',
        ),
        (['нет совпадений'], 'menu_item.json', 'menu_item.json'),
    ],
)
async def test_exclude_item_name_contains_filter(
        load_json, black_list, file_name, result_file_name,
):
    menu = load_json(file_name)
    handler = ExcludeItemNameContainsFilter(black_list)
    handler.content_filter(menu)
    assert menu == load_json(result_file_name)
