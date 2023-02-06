import pytest

from fleet_enums.utils import order_category


@pytest.mark.config(
    OPTEUM_PARK_SPECIFICATION_CATEGORIES={
        'delivery': ['express', 'courier', 'cargo', 'eda', 'lavka'],
    },
)
async def test_specification_and_eda_lavka_false(library_context):
    categories = await order_category.list_filtered(
        library_context, ['delivery'], False,
    )

    assert [category.name for category in categories] == [
        'cargo',
        'courier',
        'express',
        'none',
    ]


@pytest.mark.config(
    OPTEUM_PARK_SPECIFICATION_CATEGORIES={
        'delivery': ['express', 'courier', 'cargo', 'eda', 'lavka'],
    },
)
async def test_specification_and_eda_lavka_true(library_context):
    categories = await order_category.list_filtered(
        library_context, ['delivery'], True,
    )

    assert [category.name for category in categories] == [
        'cargo',
        'courier',
        'eda',
        'express',
        'lavka',
        'none',
    ]


@pytest.mark.parametrize('use_eda_lavka', [True, False])
@pytest.mark.parametrize('use_selfdriving', [True, False])
@pytest.mark.parametrize('use_scooters', [True, False])
@pytest.mark.parametrize('use_child_tariff', [True, False])
async def test_use(
        library_context,
        use_eda_lavka,
        use_selfdriving,
        use_scooters,
        use_child_tariff,
):
    filtered_categories = await order_category.list_filtered(
        library_context,
        [],
        use_eda_lavka,
        use_selfdriving,
        use_scooters,
        use_child_tariff,
        [],
    )

    categories = await order_category.get_all_categories(library_context)

    if not use_eda_lavka:
        categories.remove('eda')
        categories.remove('lavka')
    if not use_selfdriving:
        categories.remove('selfdriving')
    if not use_scooters:
        categories.remove('scooters')
    if not use_child_tariff:
        categories.remove('child_tariff')

    assert {category.name for category in filtered_categories} == categories
