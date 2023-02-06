from eats_menu_processor.components import menu_processor


async def test_filtered_categories(stq3_context, load_json):

    cases = load_json('origin_menu.json')
    results = load_json('processed_menu.json')
    handler = menu_processor.FilteredCategoriesHandler(stq3_context)

    for case_name, menu in cases.items():
        assert results[case_name] == await handler.handle(menu)


async def test_filtered_categories_with_delete_filtered(
        stq3_context, load_json,
):

    origin_menu = load_json('origin_menu.json')['case_1']
    results = load_json('processed_menu_with_delete_filtered.json')
    handler = menu_processor.FilteredCategoriesHandler(stq3_context)
    assert results == await handler.handle(origin_menu)


async def test_is_filtered_handler(stq3_context, load_json, patch):
    @patch('eats_menu_processor.components.menu_logging.CsvPushHandler.push')
    async def _log_handle(data):
        return

    origin_menu = load_json('origin_menu.json')['case_1']
    results = load_json('processed_menu_with_is_filtered.json')
    handler = menu_processor.FilteredCategoriesHandler(stq3_context)
    categories_handler_data = await handler.handle(origin_menu)
    handler = menu_processor.FilteredHandler(
        stq3_context, s3_link='test', delete_filtered=True,
    )
    answer = await handler.handle(categories_handler_data)
    assert results == answer
