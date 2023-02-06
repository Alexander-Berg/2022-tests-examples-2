from eats_menu_processor.components import menu_processor


async def test_validate_filters(stq3_context, load_json):
    origin_menu = load_json('origin_menu.json')
    handler = menu_processor.ValidateFiltersHandler(stq3_context)

    processed_menu = load_json('processed_menu.json')
    assert processed_menu == await handler.handle(origin_menu)
