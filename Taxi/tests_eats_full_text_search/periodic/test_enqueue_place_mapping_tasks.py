async def test_enqueue_place_mapping_tasks(
        taxi_eats_full_text_search, pgsql, stq,
):
    """
    Проверяем что stq таски ставятся периодиком в очередь
    """

    cursor = pgsql['eats_full_text_search_indexer'].cursor()

    cursor.execute(
        """
        INSERT INTO
            fts.place (
                place_id,
                place_slug,
                enabled
            ) values (
                1,
                'place_slug',
                true
            );
    """,
    )

    cursor.execute(
        """
        INSERT INTO
            fts.place (
                place_id,
                place_slug,
                enabled,
                business
            ) values (
                2,
                'restaurant_place_slug',
                true,
                'restaurant'
            );
    """,
    )

    cursor.execute(
        """
        INSERT INTO
            fts.place (
                place_id,
                place_slug,
                enabled,
                business
            ) values (
                3,
                'shop_place_slug',
                true,
                'shop'
            );
    """,
    )

    await taxi_eats_full_text_search.run_task('place-mapping-update-periodic')

    queue = stq.eats_full_text_search_update_place_mapping

    assert queue.times_called == 2

    # ставится в stq поскольку значение поля business не указано
    # и по умолчанию оно ставится shop
    expected_place_slug = 'place_slug'

    task = queue.next_call()
    task.pop('eta', None)
    assert 'kwargs' in task
    task['kwargs'].pop('log_extra', None)
    assert task == {
        'queue': 'eats_full_text_search_update_place_mapping',
        'id': 'place_mapping_update_{}'.format(expected_place_slug),
        'args': [],
        'kwargs': {'place_slug': expected_place_slug},
    }

    expected_shop_place_slug = 'shop_place_slug'

    task = queue.next_call()
    task.pop('eta', None)
    assert 'kwargs' in task
    task['kwargs'].pop('log_extra', None)
    assert task == {
        'queue': 'eats_full_text_search_update_place_mapping',
        'id': 'place_mapping_update_{}'.format(expected_shop_place_slug),
        'args': [],
        'kwargs': {'place_slug': expected_shop_place_slug},
    }
