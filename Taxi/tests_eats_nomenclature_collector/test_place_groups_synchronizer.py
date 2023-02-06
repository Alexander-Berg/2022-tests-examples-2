OLD_UPDATED_AT = '2021-01-01T00:45:00+00:00'


async def test_place_groups_synchronizer(
        mockserver,
        testpoint,
        taxi_eats_nomenclature_collector,
        to_utc_datetime,
        pg_cursor,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/eats-core-retail/v1/brand/place-groups/retrieve',
    )
    def eats_core_retail(request):
        brand_id = request.query['brand_id']
        return _get_core_response(brand_id)

    _sql_fill_data(pg_cursor)

    @testpoint('eats_nomenclature_collector::place-groups-synchronizer')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'place-groups-synchronizer',
    )

    handle_finished.next_call()
    old_date = to_utc_datetime(OLD_UPDATED_AT).strftime('%Y-%m-%dT%H:%M')

    place_groups_from_db = _sql_get_place_groups_from_db(
        pg_cursor, to_utc_datetime,
    )
    not_updated_place_groups_ids = ['1', '5']
    expected_place_groups = _get_expected_place_groups()
    for updated_place_group, expected_place_group in zip(
            place_groups_from_db, expected_place_groups,
    ):
        for field in [
                'id',
                'name',
                'parser_days_of_week',
                'parser_hours',
                'price_parser_hours',
                'stop_list_enabled',
                'is_vendor',
                'is_enabled',
                'stock_reset_limit',
        ]:
            assert updated_place_group[field] == expected_place_group[field]
        if updated_place_group['id'] in not_updated_place_groups_ids:
            assert updated_place_group['updated_at'] == old_date
        else:
            assert updated_place_group['updated_at'] != old_date

    brands_place_groups_from_db = _sql_get_brands_place_groups_from_db(
        pg_cursor, to_utc_datetime,
    )
    expected_brands_place_groups = _get_expected_brands_place_groups()
    for updated_bpg, expected_bpg in zip(
            brands_place_groups_from_db, expected_brands_place_groups,
    ):
        for field in ['brand_id', 'place_group_id', 'is_enabled']:
            assert updated_bpg[field] == expected_bpg[field]
        if updated_bpg['place_group_id'] in not_updated_place_groups_ids:
            assert updated_bpg['updated_at'] == old_date
        else:
            assert updated_bpg['updated_at'] != old_date


async def test_periodic_metrics(mockserver, verify_periodic_metrics):
    @mockserver.json_handler(
        '/eats-core-retail/v1/brand/place-groups/retrieve',
    )
    def _eats_core_retail(request):
        brand_id = request.query['brand_id']
        assert brand_id in {'1', '2', '3'}
        if brand_id == '1':
            return _create_response(
                [
                    _create_place_group('3', 'aa', is_vendor=True),
                    _create_place_group('4', 'bb', stock_reset_limit=5),
                    _create_place_group('5', 'cc'),
                    _create_place_group('8', 'ff'),
                ],
            )
        if brand_id == '2':
            return _create_response(
                [
                    _create_place_group('6', 'dd'),
                    _create_place_group('7', 'ee'),
                    _create_place_group('8', 'ff'),
                ],
            )
        return _create_response([])

    await verify_periodic_metrics(
        'place-groups-synchronizer', is_distlock=True,
    )


def _create_response(place_groups):
    return {'place_groups': place_groups}


def _create_brands_place_group(brand_id, place_group_id, is_enabled):
    return {
        'brand_id': brand_id,
        'place_group_id': place_group_id,
        'is_enabled': is_enabled,
    }


def _create_place_group(
        place_group_id,
        name,
        parser_days_of_week='1111100',
        parser_hours='8:00,16:00',
        price_parser_hours='',
        stop_list_enabled=True,
        is_vendor=False,
        stock_reset_limit=0,
        is_enabled=True,
):
    return {
        'id': place_group_id,
        'name': name,
        'parser_days_of_week': parser_days_of_week,
        'parser_hours': parser_hours,
        'price_parser_hours': price_parser_hours,
        'stop_list_enabled': stop_list_enabled,
        'is_vendor': is_vendor,
        'stock_reset_limit': stock_reset_limit,
        'is_enabled': is_enabled,
    }


def _get_core_response(brand_id):
    brand_id_to_response = {
        '1': [
            _create_place_group('1', 'remain_unchanged'),
            _create_place_group(
                '2',
                'changed_params',
                parser_days_of_week='1000000',
                price_parser_hours='8:00,12:00',
            ),
        ],
        '2': [
            _create_place_group('3', 'enabled'),
            _create_place_group('6', 'new'),
        ],
        '3': [_create_place_group('7', 'disabled_brand')],
    }
    return _create_response(brand_id_to_response[brand_id])


def _get_expected_brands_place_groups():
    return [
        _create_brands_place_group('1', '1', True),
        _create_brands_place_group('1', '2', True),
        _create_brands_place_group('2', '3', True),
        _create_brands_place_group('2', '4', False),
        _create_brands_place_group('2', '5', False),
        _create_brands_place_group('2', '6', True),
    ]


def _get_expected_place_groups():
    return [
        _create_place_group('1', 'remain_unchanged'),
        _create_place_group(
            '2',
            'changed_params',
            parser_days_of_week='1000000',
            price_parser_hours='8:00,12:00',
        ),
        _create_place_group('3', 'enabled'),
        _create_place_group(
            '4', 'disabled', is_enabled=False, stop_list_enabled=False,
        ),
        _create_place_group(
            '5', 'remain_disabled', is_enabled=False, stop_list_enabled=False,
        ),
        _create_place_group('6', 'new'),
    ]


def _sql_get_brands_place_groups_from_db(pg_cursor, to_utc_datetime):
    pg_cursor.execute(
        """
        select brand_id, place_group_id, is_enabled, updated_at
        from eats_nomenclature_collector.brands_place_groups
        order by place_group_id
        """,
    )
    rows = list(pg_cursor)
    for row in rows:
        row['updated_at'] = to_utc_datetime(row['updated_at']).strftime(
            '%Y-%m-%dT%H:%M',
        )
    return rows


def _sql_get_place_groups_from_db(pg_cursor, to_utc_datetime):
    pg_cursor.execute(
        """
        select
            id,
            name,
            parser_days_of_week,
            parser_hours,
            price_parser_hours,
            stop_list_enabled,
            is_vendor,
            stock_reset_limit,
            is_enabled,
            updated_at
        from eats_nomenclature_collector.place_groups
        order by id
        """,
    )
    rows = list(pg_cursor)
    for row in rows:
        row['updated_at'] = to_utc_datetime(row['updated_at']).strftime(
            '%Y-%m-%dT%H:%M',
        )
    return rows


def _sql_fill_data(pg_cursor, old_updated_at=OLD_UPDATED_AT):
    brands = [
        {'id': '1', 'slug': '1', 'is_enabled': True},
        {'id': '2', 'slug': '2', 'is_enabled': True},
        {'id': '3', 'slug': '3_disabled', 'is_enabled': False},
    ]
    for brand in brands:
        pg_cursor.execute(
            """
                insert into eats_nomenclature_collector.brands
                    (id, slug, is_enabled)
                values (%s, %s, %s)
                """,
            (brand['id'], brand['slug'], brand['is_enabled']),
        )

    place_groups = [
        _create_place_group('1', 'remain_unchanged'),
        _create_place_group('2', 'changed_params'),
        _create_place_group('3', 'enabled', is_enabled=False),
        _create_place_group('4', 'disabled'),
        _create_place_group(
            '5', 'remain_disabled', is_enabled=False, stop_list_enabled=False,
        ),
    ]

    for place_group in place_groups:
        pg_cursor.execute(
            """
                insert into eats_nomenclature_collector.place_groups(
                    id,
                    name,
                    parser_days_of_week,
                    parser_hours,
                    price_parser_hours,
                    stop_list_enabled,
                    stock_reset_limit,
                    is_vendor,
                    is_enabled,
                    created_at,
                    updated_at
                ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
            (
                place_group['id'],
                place_group['name'],
                place_group['parser_days_of_week'],
                place_group['parser_hours'],
                place_group['price_parser_hours'],
                place_group['stop_list_enabled'],
                place_group['stock_reset_limit'],
                place_group['is_vendor'],
                place_group['is_enabled'],
                old_updated_at,
                old_updated_at,
            ),
        )

    brands_place_groups = [
        # remain enabled
        _create_brands_place_group('1', '1', True),
        # to enable
        _create_brands_place_group('1', '2', False),
        _create_brands_place_group('2', '3', False),
        # to disable
        _create_brands_place_group('2', '4', True),
        # remain disabled
        _create_brands_place_group('2', '5', False),
    ]

    for brands_place_group in brands_place_groups:
        pg_cursor.execute(
            """
                insert into eats_nomenclature_collector.brands_place_groups
                    (brand_id, place_group_id, is_enabled, created_at,
                    updated_at)
                values (%s, %s, %s, %s, %s)
                """,
            (
                brands_place_group['brand_id'],
                brands_place_group['place_group_id'],
                brands_place_group['is_enabled'],
                old_updated_at,
                old_updated_at,
            ),
        )
