import pytest

from eats_integration_offline_orders.components.menu import iiko_menu_fetcher

ORGANIZATION_ID = '00000000-0000-0000-orga-00000000001'
API_LOGIN = '77c54078bb024d39ad5cb8193fe62035'


@pytest.mark.skip
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['db_iiko_transport_meta.sql'],
)
async def test_iiko_menu_fetcher_cats_as_cats(
        web_context, iiko_transport_mocks, place_id, load_json, load,
):

    iiko_transport_mocks.iiko_cloud_nomenclature.result = load_json(
        'nomenclature.json',
    )

    fetcher = iiko_menu_fetcher.IIKOMenuFetcher(web_context)
    menu_data = await fetcher.get_menu_data_from_pos(place_id)

    assert menu_data.dict() == load_json(
        'menu_data_categories_as_categories.json',
    )


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['db_iiko_transport_meta.sql'],
)
async def test_iiko_menu_fetcher_cats_as_groups(
        web_context, iiko_transport_mocks, place_id, load_json,
):

    iiko_transport_mocks.iiko_cloud_nomenclature.result = load_json(
        'nomenclature_with_groups.json',
    )

    fetcher = iiko_menu_fetcher.IIKOMenuFetcher(web_context)
    menu_data = await fetcher.get_menu_data_from_pos(place_id)

    assert menu_data.dict() == load_json('menu_data_categories_as_groups.json')
