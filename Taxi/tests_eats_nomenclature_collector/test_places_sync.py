import pytest

CORE_INTEGRATIONS_HANDLER = (
    '/eats-core-integrations/integrations/nomenclature-collector/v1/tasks'
)


@pytest.mark.config(
    EDA_CATALOG_CLIENT_QOS={
        CORE_INTEGRATIONS_HANDLER: {'attempts': 1, 'timeout-ms': 1000},
    },
)
@pytest.mark.parametrize(
    'place_ids, expected_ids, mock_times,',
    [
        pytest.param(
            ['1', '2', '4', '5', '8888', '9999'],
            ['1', '2', '4', '5'],
            8,
            id='partially_valid',
        ),
        pytest.param(['8888'], [], 0, id='all_invalid'),
        pytest.param([], [], 0, id='empty'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature_collector',
    files=['pg_eats_nomenclature_collector.sql'],
)
async def test_places_sync(
        taxi_eats_nomenclature_collector,
        place_ids,
        expected_ids,
        mock_times,
        mockserver,
):
    @mockserver.json_handler(CORE_INTEGRATIONS_HANDLER)
    def eats_core_integrations(request):
        if request.json['place_id'] == '5':
            raise mockserver.TimeoutError()
        return {
            'id': request.json['id'],
            'type': 'nomenclature',
            'place_id': request.json['place_id'],
            'status': 'created',
            'data_file_url': '',
            'data_file_version': '',
            'reason': None,
        }

    response = await taxi_eats_nomenclature_collector.post(
        '/v1/place/sync', json={'place_ids': place_ids},
    )

    response_json = response.json()
    result_ids = response_json['place_ids']
    result_ids.sort()

    assert eats_core_integrations.times_called == mock_times

    assert response.status_code == 200
    assert result_ids == expected_ids


@pytest.mark.pgsql(
    'eats_nomenclature_collector',
    files=['pg_eats_nomenclature_collector_tasks.sql'],
)
async def test_sync_places_with_tasks_in_progress(
        taxi_eats_nomenclature_collector, mockserver, pg_cursor,
):
    @mockserver.json_handler(CORE_INTEGRATIONS_HANDLER)
    def eats_core_integrations(request):
        return {
            'id': request.json['id'],
            'type': 'nomenclature',
            'place_id': request.json['place_id'],
            'status': 'created',
            'data_file_url': '',
            'data_file_version': '',
            'reason': None,
        }

    place_ids = ['1', '2', '3', '4', '5', '6']

    places_with_old_price_tasks = _sql_get_place_ids_with_tasks(
        pg_cursor, 'price_tasks',
    )
    places_with_potential_new_price_tasks = (  # pylint: disable=invalid-name
        _sql_get_places_that_could_have_new_tasks(
            pg_cursor, 'price_tasks', place_ids,
        )
    )
    places_with_old_nmn_tasks = _sql_get_place_ids_with_tasks(
        pg_cursor, 'nomenclature_place_tasks',
    )
    places_with_potential_new_nmn_tasks = (  # pylint: disable=invalid-name
        _sql_get_places_that_could_have_new_tasks(
            pg_cursor, 'nomenclature_place_tasks', place_ids,
        )
    )

    response = await taxi_eats_nomenclature_collector.post(
        '/v1/place/sync', json={'place_ids': place_ids},
    )

    assert response.status_code == 200

    places_with_new_price_tasks = _sql_get_place_ids_with_tasks(
        pg_cursor, 'price_tasks',
    )
    expected_places_with_new_price_task = (  # pylint: disable=invalid-name
        _get_expected_places_with_new_task(
            place_ids, places_with_potential_new_price_tasks,
        )
    )
    assert sorted(places_with_new_price_tasks) == sorted(
        places_with_old_price_tasks + expected_places_with_new_price_task,
    )

    places_with_new_nmn_tasks = _sql_get_place_ids_with_tasks(
        pg_cursor, 'nomenclature_place_tasks',
    )
    expected_places_with_new_nmn_task = (  # pylint: disable=invalid-name
        _get_expected_places_with_new_task(
            place_ids, places_with_potential_new_nmn_tasks,
        )
    )
    assert sorted(places_with_new_nmn_tasks) == sorted(
        places_with_old_nmn_tasks + expected_places_with_new_nmn_task,
    )

    assert eats_core_integrations.times_called == len(
        expected_places_with_new_nmn_task,
    ) + len(expected_places_with_new_price_task)


def _sql_get_place_ids_with_tasks(pg_cursor, table_name):
    pg_cursor.execute(
        f"""
        select place_id
        from eats_nomenclature_collector.{table_name}
        """,
    )
    return [place['place_id'] for place in pg_cursor.fetchall()]


def _sql_get_places_that_could_have_new_tasks(
        pg_cursor, table_name, place_ids,
):
    pg_cursor.execute(
        f"""
        select distinct src.place_id
        from unnest(array{place_ids}) as src(place_id)
        where
            not exists (
                select 1 from eats_nomenclature_collector.{table_name} pt
                where src.place_id = pt.place_id
                and pt.status in ('created', 'started')
            )
        """,
    )
    return [place['place_id'] for place in pg_cursor.fetchall()]


def _create_response(places, limit, cursor=None):
    data = {'places': list(places), 'meta': {'limit': limit}}
    if cursor:
        data['meta']['cursor'] = cursor
    return data


def _get_expected_places_with_new_task(
        requested_place_ids, place_ids_with_potential_tasks,
):
    return [
        place_id
        for place_id in requested_place_ids
        if place_id in place_ids_with_potential_tasks
    ]


async def test_periodic_metrics(mockserver, verify_periodic_metrics):
    @mockserver.json_handler(CORE_INTEGRATIONS_HANDLER)
    def _eats_core_integrations(request):
        return {
            'id': request.json['id'],
            'type': 'nomenclature',
            'place_id': request.json['place_id'],
            'status': 'created',
            'data_file_url': '',
            'data_file_version': '',
            'reason': None,
        }

    @mockserver.json_handler('/eats-core-retail/v1/brand/places/retrieve')
    def _eats_core_retail(request):
        return _create_response(places=[], limit=1000)

    await verify_periodic_metrics('places-synchronizer', is_distlock=True)
