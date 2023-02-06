PERIODIC_NAME = 'place-info-updater-periodic'


async def test_periodic(
        stq,
        mocked_time,
        update_taxi_config,
        pg_cursor,
        taxi_eats_retail_market_integration,
):
    update_taxi_config(
        'EATS_RETAIL_MARKET_INTEGRATION_PERIODICS',
        {PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 60}},
    )
    place_info_update_delay_sec = 5
    update_taxi_config(
        'EATS_RETAIL_MARKET_INTEGRATION_PLACE_INFO_UPDATER',
        {place_info_update_delay_sec: place_info_update_delay_sec},
    )

    places = ['1', '2', '3', '4', '5']
    _sql_set_places(pg_cursor, places)

    await taxi_eats_retail_market_integration.run_distlock_task(PERIODIC_NAME)
    times_called = (
        stq.eats_retail_market_integration_update_places_info.times_called
    )
    assert times_called == len(places)

    called_places = []
    for _ in range(times_called):
        task_info = (
            stq.eats_retail_market_integration_update_places_info.next_call()
        )
        place_id = task_info['kwargs']['place_id']
        eta = task_info['eta']
        delay = (eta - mocked_time.now()).total_seconds()
        called_places.append({'place_id': place_id, 'delay': delay})

    assert set(places) == {place['place_id'] for place in called_places}

    called_places.sort(key=lambda item: item['delay'])
    for i, called_place in enumerate(called_places):
        assert called_place['delay'] == i * place_info_update_delay_sec


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _sql_set_places(pg_cursor, places):
    brand_id = '111'
    pg_cursor.execute(
        f"""
        insert into eats_retail_market_integration.brands (id, slug)
        values ('{brand_id}', 'brand_slug_{brand_id}')
        """,
    )
    for place_id in places:
        pg_cursor.execute(
            f"""
            insert into eats_retail_market_integration.places (
                id, slug, brand_id
            )
            values('{place_id}', 'place_slug_{place_id}', '{brand_id}')
            """,
        )
