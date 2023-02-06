async def test_update_retail_place_periodic(
        taxi_eats_full_text_search_indexer, pgsql, stq,
):
    """
    Проверяем что stq таски ставятся периодиком в очередь
    """

    place_slug = 'place_slug'

    cursor = pgsql['eats_full_text_search_indexer'].cursor()

    cursor.execute(
        """
        INSERT INTO
            fts_indexer.place_state (
                place_id,
                place_slug,
                business,
                enabled
            ) values (
                1,
                %s,
                'shop',
                true
            ), (
                2,
                'disabled_slug',
                'shop',
                false
            ), (
                3,
                'rest_slug',
                'restaurant',
                true
            );
    """,
        (place_slug,),
    )

    await taxi_eats_full_text_search_indexer.run_task(
        'update-retail-place-periodic',
    )

    queue = stq.eats_full_text_search_indexer_update_retail_place

    assert queue.times_called == 1
    task = queue.next_call()
    task.pop('eta', None)
    assert 'kwargs' in task
    task['kwargs'].pop('log_extra', None)
    assert task == {
        'queue': 'eats_full_text_search_indexer_update_retail_place',
        'id': 'update_retail_place_{}'.format(place_slug),
        'args': [],
        'kwargs': {'place_slug': place_slug},
    }
