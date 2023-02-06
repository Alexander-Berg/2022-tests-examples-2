# pylint: disable=E0401,C5521
import pytest

# pylint: disable=W0612,C0103
from eats_content_filters.filters import ExcludeCategoryFilter


@pytest.mark.parametrize(
    'black_list, file_name, result_file_name',
    [
        (
            [
                'Насадка SESITIVE для PICOBELLO XL',
                'Кувшин БАРЬЕР Чемпион, 4 л',
            ],
            'menu_category.json',
            'result_category_all_black_list.json',
        ),
        (['нет совпадений'], 'menu_category.json', 'menu_category.json'),
    ],
)
async def test_exclude_category_filter(
        load_json, black_list, file_name, result_file_name,
):
    menu = load_json(file_name)
    handler = ExcludeCategoryFilter(black_list)
    handler.content_filter(menu)
    assert menu == load_json(result_file_name)
