# flake8: noqa
# pylint: disable=import-error,wildcard-import
# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint:disable= unused-variable, redefined-builtin, invalid-name
# pylint:disable= global-statement, no-else-return

import pytest

PLACES = [
    {
        'id': 0,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [10.0, 10.0]},
        'region': {
            'id': 2,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
        'enabled': True,
    },
    {
        'id': 1,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [20.0, 20.0]},
        'region': {
            'id': 2,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
        'enabled': True,
    },
    {
        'id': 2,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [20.0, 20.0]},
        'region': {
            'id': 2,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
        'enabled': True,
    },
    {
        'id': 3,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
        'region': {
            'id': 2,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'marketplace',
        'enabled': True,
    },
]


def clear_db(cursor):
    cursor.execute(
        """
        ALTER SEQUENCE taxi_surger_revisions_id_seq RESTART WITH 1
        """,
    )


@pytest.mark.eats_catalog_storage_cache(PLACES)
@pytest.mark.now('2021-05-11T23:45:30+00:00')
@pytest.mark.parametrize(
    'surge_limit, requests_size',
    (
        pytest.param(1, [(0,), (1, 2)]),
        pytest.param(2, [(0,), (1, 2)]),
        pytest.param(3, [(0, 1, 2)]),
    ),
)
async def test_surger(
        taxi_eats_surge_planner,
        pgsql,
        mockserver,
        taxi_config,
        surge_limit,
        requests_size,
):
    cursor = pgsql['surge'].cursor()

    clear_db(cursor)

    taxi_config.set(
        EATS_SURGE_PLANNER_MAIN={
            'enable_surge_worker': True,
            'get_places_static_limit': 800,
            'get_surge_calculator_limit': surge_limit,
            'number_of_threads': 2,
            'insert_db_limit': 500,
            'add_time_revision': 0,
            'db_settings': {
                'network_timeout_ms': 300,
                'statement_timeout_ms': 200,
            },
        },
    )

    surge_requests = []

    @mockserver.json_handler('/eda-surge-calculator/v1/calc-surge')
    def calc_surge(request):
        ids = request.json['place_ids']

        surge_requests.append(tuple(sorted(ids)))

        values = []
        for id in ids:
            values.append({'place_id': id, 'result': {'some_value': id}})
        return {
            'results': [{'calculator_name': 'calc_eats', 'results': values}],
            'errors': [],
        }

    await taxi_eats_surge_planner.run_distlock_task('surge-worker')

    cursor.execute(
        """
        SELECT
            place_id, calculator_name, result, revision_id, request_id, rest_type
        FROM
            taxi_surger_parts_22
        ORDER BY place_id;
    """,
    )

    assert list(cursor) == [
        (0, 'calc_eats', '{"some_value":0}', 1, 'surge', 'native'),
        (1, 'calc_eats', '{"some_value":1}', 1, 'surge', 'native'),
        (2, 'calc_eats', '{"some_value":2}', 1, 'surge', 'native'),
        (
            3,
            'calc_eats',
            '{"surge_level":0,"load_level":0,"additional_time_percents":0}',
            1,
            'surge',
            'marketplace',
        ),
    ]

    assert set(surge_requests) == set(requests_size)


@pytest.mark.eats_catalog_storage_cache(PLACES)
@pytest.mark.now('2021-05-11T01:00:30+00:00')
async def test_cleaner(taxi_eats_surge_planner, pgsql, mockserver):
    @mockserver.json_handler('/eda-surge-calculator/v1/calc-surge')
    def calc_surge(request):
        ids = request.json['place_ids']

        assert len(ids) <= 2

        values = []
        for id in ids:
            values.append({'place_id': id, 'result': {'some_value': id}})
        return {
            'results': [{'calculator_name': 'calc_eats', 'results': values}],
            'errors': [],
        }

    cursor = pgsql['surge'].cursor()

    cursor.execute(
        """
        INSERT INTO taxi_surger_revisions (partition_name) VALUES ('taxi_surger_parts_04') RETURNING id

    """,
    )

    cursor.execute(
        """
        INSERT INTO taxi_surger_parts_04
            (place_id, calculator_name, result, revision_id)
        SELECT 1, 2, 'hello', 1;
    """,
    )

    def get_size_surges(pgsql):
        cursor = pgsql['surge'].cursor()

        cursor.execute(
            """
            SELECT
                *
            FROM
                "taxi_surger_parts_04";
        """,
        )
        return len(list(cursor))

    def get_size_revisions(pgsql):
        cursor = pgsql['surge'].cursor()

        cursor.execute(
            """
            SELECT
                *
            FROM
                "taxi_surger_revisions";
        """,
        )
        return len(list(cursor))

    assert get_size_surges(pgsql) == 1
    assert get_size_revisions(pgsql) == 1

    await taxi_eats_surge_planner.run_distlock_task('clean-worker')

    assert get_size_surges(pgsql) == 0
    assert get_size_revisions(pgsql) == 0
