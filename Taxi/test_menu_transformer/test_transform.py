async def test_init_different_dev_filer(library_context, load_json, patch):
    menu = library_context.menu_transformer.transform(
        load_json('menu_data_base.json'), load_json('dev_filter_empty.json'),
    )
    assert menu == load_json('menu_data_base.json')

    menu = library_context.menu_transformer.transform(
        load_json('menu_data_base.json'), load_json('dev_filter.json'),
    )
    assert menu == load_json('menu_data.json')
