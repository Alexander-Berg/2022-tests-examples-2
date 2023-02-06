import pytest

OLD_UPDATED_AT = '2021-01-01T00:45:00+00:00'
TEST_CORE_REQUEST_LIMIT = 2


def _create_place(place_id, slug, place_group_id, stop_list_enabled=None):
    if stop_list_enabled is None:
        return {
            'id': place_id,
            'slug': slug,
            'place_group_id': place_group_id,
            'enabled': True,
            'parser_enabled': True,
        }
    return {
        'id': place_id,
        'slug': slug,
        'place_group_id': place_group_id,
        'enabled': True,
        'parser_enabled': True,
        'stop_list_enabled': stop_list_enabled,
    }


def _create_response(places, limit, cursor=None):
    data = {'places': list(places), 'meta': {'limit': limit}}
    if cursor:
        data['meta']['cursor'] = cursor
    return data


def sql_get_places(pgsql, to_utc_datetime):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select
            id,
            slug,
            brand_id,
            place_group_id,
            is_enabled,
            is_parser_enabled,
            stop_list_enabled,
            updated_at
        from eats_nomenclature_collector.places order by id
        """,
    )
    return [
        {
            'id': place[0],
            'slug': place[1],
            'brand_id': place[2],
            'place_group_id': place[3],
            'is_enabled': place[4],
            'is_parser_enabled': place[5],
            'stop_list_enabled': place[6],
            'updated_at': to_utc_datetime(place[7]).strftime('%Y-%m-%dT%H:%M'),
        }
        for place in cursor
    ]


def sql_get_brand_tasks(pgsql):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select brand_id, status
        from eats_nomenclature_collector.nomenclature_brand_tasks
        order by brand_id
        """,
    )
    return [(row[0], row[1]) for row in cursor]


def sql_get_place_tasks(pgsql):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select place_id, brand_id, npt.status
        from eats_nomenclature_collector.nomenclature_place_tasks npt
            join eats_nomenclature_collector.nomenclature_brand_tasks nbt
            on npt.nomenclature_brand_task_id = nbt.id
        order by place_id, brand_id
        """,
    )
    return [(row[0], row[1], row[2]) for row in cursor]


def sql_get_price_tasks(pgsql):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select place_id
        from eats_nomenclature_collector.price_tasks
        order by place_id
        """,
    )
    return [row[0] for row in cursor]


@pytest.mark.parametrize(
    'core_integrations_status', [200, 400, 401, 403, 404, 409, 500],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_COLLECTOR_SYNCHRONIZERS_SETTINGS={
        'brands': {'chunk_size': 1000, 'enabled': True, 'period_in_sec': 300},
        'groups': {'chunk_size': 1000, 'enabled': True, 'period_in_sec': 300},
        'places': {
            'chunk_size': 1000,
            'enabled': True,
            'period_in_sec': 300,
            'core_request_limit': TEST_CORE_REQUEST_LIMIT,
        },
    },
)
async def test_places_synchronizer(
        taxi_eats_nomenclature_collector,
        mockserver,
        testpoint,
        pgsql,
        load_json,
        mock_integrations,
        to_utc_datetime,
        # parametrize params
        core_integrations_status,
):
    integrations_mock = mock_integrations(
        core_integrations_status, ['nomenclature', 'price'],
    )

    # pylint: disable=unused-variable
    @mockserver.json_handler('/eats-core-retail/v1/brand/places/retrieve')
    def eats_core_retail(request):
        brand_id = request.query['brand_id']
        core_request_limit = TEST_CORE_REQUEST_LIMIT
        assert request.json['limit'] == core_request_limit
        assert brand_id in {'1', '2', '3', '4'}
        if brand_id == '1':
            return _create_response(
                places=[
                    _create_place(
                        '1', 'new_place1', '1', stop_list_enabled=False,
                    ),
                    _create_place(
                        '999', 'place999', None, stop_list_enabled=True,
                    ),
                    _create_place(
                        '998', 'place998', '', stop_list_enabled=True,
                    ),
                    _create_place(
                        '100', 'place100', '1', stop_list_enabled=True,
                    ),
                    _create_place('101', 'place101', '1'),
                ],
                limit=core_request_limit,
            )
        if brand_id == '2':
            if 'cursor' not in request.json:
                return _create_response(
                    places=[
                        _create_place(
                            '2', 'new_place2', '3', stop_list_enabled=True,
                        ),
                        _create_place(
                            '6', 'new_place6', '3', stop_list_enabled=True,
                        ),
                    ],
                    limit=core_request_limit,
                    cursor='7',
                )
            if request.json['cursor'] == '7':
                return _create_response(
                    places=[
                        _create_place(
                            '7', 'new_place7', '3', stop_list_enabled=True,
                        ),
                        _create_place(
                            '102', 'place102', '1', stop_list_enabled=True,
                        ),
                        _create_place(
                            '8',
                            'remain_enabled8',
                            '3',
                            stop_list_enabled=True,
                        ),
                        _create_place('9', 'enabled9', '3'),
                    ],
                    limit=core_request_limit,
                )
        if brand_id == '4':
            return _create_response(
                places=[_create_place('4', 'place_of_disabled_brand', '1')],
                limit=core_request_limit,
            )
        return _create_response(places=[], limit=core_request_limit)

    @testpoint('eats_nomenclature_collector::places-synchronizer')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'places-synchronizer',
    )
    handle_finished.next_call()

    sql_places = sql_get_places(pgsql, to_utc_datetime)
    expected_places = load_json('expected_places.json')
    not_updated_place_groups_ids = ['8', '10']
    old_date = to_utc_datetime(OLD_UPDATED_AT).strftime('%Y-%m-%dT%H:%M')
    for updated_place, expected_place in zip(sql_places, expected_places):
        for field in [
                'id',
                'slug',
                'brand_id',
                'place_group_id',
                'is_enabled',
                'is_parser_enabled',
                'stop_list_enabled',
        ]:
            assert updated_place[field] == expected_place[field]
        if updated_place['id'] in not_updated_place_groups_ids:
            assert updated_place['updated_at'] == old_date
        else:
            assert updated_place['updated_at'] != old_date

    if core_integrations_status == 500:
        assert integrations_mock.times_called == 12
    else:
        assert integrations_mock.times_called == 6

    if core_integrations_status == 200:
        assert sql_get_brand_tasks(pgsql) == [
            ('1', 'created'),
            ('2', 'created'),
        ]
        assert sql_get_place_tasks(pgsql) == [
            ('100', '1', 'created'),
            ('101', '1', 'created'),
            ('102', '2', 'created'),
        ]
        assert sql_get_price_tasks(pgsql) == ['100', '101', '102']
    else:
        assert sql_get_brand_tasks(pgsql) == [
            ('1', 'creation_failed'),
            ('2', 'creation_failed'),
        ]
        assert sql_get_place_tasks(pgsql) == [
            ('100', '1', 'creation_failed'),
            ('101', '1', 'creation_failed'),
            ('102', '2', 'creation_failed'),
        ]
