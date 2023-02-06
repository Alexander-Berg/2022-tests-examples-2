from eats_integration_workers.components.workers.metro import nomenclature


async def test_content_filters(stq3_context, load_json):
    handler = nomenclature.MetroNomenclatureWorker(stq3_context)
    menu = load_json('menu_data.json')
    handler.filter_menu(menu)
    assert menu == load_json('menu_data_result.json')
