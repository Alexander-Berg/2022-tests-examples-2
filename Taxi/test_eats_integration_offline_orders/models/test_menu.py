from eats_integration_offline_orders.models import menu as menu_models


async def test_menu_save(web_context, place_id):

    menu_data = menu_models.MenuData(
        items={
            'menu_item_id__1': menu_models.MenuItem(
                id='menu_item_id__1',
                category_id='category_id__1',
                title='Кукуруза',
                price=1.20,
            ),
        },
        categories={
            'category_id__1': menu_models.MenuCategory(
                id='category_id__1', title='Бакалея',
            ),
        },
    )

    await web_context.queries.menu.upsert_menu_data(
        place_id, menu_data.json(ensure_ascii=False),
    )

    from_db = await web_context.queries.menu.get_by_place_id(place_id)

    assert from_db
    assert from_db.place_id == place_id
    assert isinstance(from_db.menu, menu_models.MenuData)
    assert isinstance(from_db.menu.items, dict)
    assert isinstance(from_db.menu.categories, dict)
    assert isinstance(from_db.updates, dict)
    assert isinstance(from_db.stop_list, dict)
    assert len(from_db.menu.items) == 1
    assert len(from_db.menu.categories) == 1
    assert isinstance(
        from_db.menu.items['menu_item_id__1'], menu_models.MenuItem,
    )
    assert isinstance(
        from_db.menu.categories['category_id__1'], menu_models.MenuCategory,
    )
