import datetime as dt

import pytest
import pytz


MOCK_NOW = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
PERIODIC_NAME = 'snapshots-checker-periodic'


@pytest.mark.parametrize(
    'old_snapshot_table_name', [None, '2021-01-01', '2021-03-01'],
)
@pytest.mark.parametrize('skip_snapshot', [True, False])
@pytest.mark.parametrize(
    'snapshot_name_to_skip',
    [
        'products',
        'places_products',
        'categories',
        'categories_products',
        'categories_relations',
        'default_assortments',
    ],
)
@pytest.mark.parametrize(
    'snapshot_name_to_skip_status', ['no_table', 'empty_table'],
)
@pytest.mark.now(MOCK_NOW.isoformat())
async def test_periodic(
        taxi_eats_nomenclature,
        testpoint,
        taxi_config,
        mocked_time,
        pgsql,
        yt_apply,
        yt_client,
        old_snapshot_table_name,
        skip_snapshot,
        snapshot_name_to_skip,
        snapshot_name_to_skip_status,
):
    new_snapshot_table_name = (
        mocked_time.now() - dt.timedelta(days=1)
    ).strftime('%Y-%m-%d')
    snapshot_prefixes = get_snapshot_prefixes()

    if old_snapshot_table_name:
        fill_last_sent_ready_snapshot(old_snapshot_table_name, pgsql)

    fill_yt_tables(
        snapshot_prefixes,
        skip_snapshot,
        snapshot_name_to_skip,
        snapshot_name_to_skip_status,
        new_snapshot_table_name,
        yt_client,
    )

    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_SNAPSHOTS_CHECKER': {
                'snapshot_prefixes': snapshot_prefixes,
            },
            'EATS_NOMENCLATURE_PERIODICS': {
                PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 600},
            },
        },
    )

    @testpoint('yt-logger-snapshot-ready')
    def yt_logger(data):
        for name, prefix in snapshot_prefixes.items():
            assert data[f'{name}_table_name'] == build_yt_path(
                prefix, new_snapshot_table_name,
            )

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    should_log = should_log_ready_snapshot(
        skip_snapshot, old_snapshot_table_name, new_snapshot_table_name,
    )
    assert yt_logger.has_calls == should_log

    expected_last_sent_snapshot = (
        new_snapshot_table_name if should_log else old_snapshot_table_name
    )
    assert get_last_sent_ready_snapshot(pgsql) == expected_last_sent_snapshot


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def fill_last_sent_ready_snapshot(snapshot_table_name, pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.last_sent_ready_snapshot(
            snapshot_table_name
        ) values ('{snapshot_table_name}')
        """,
    )


def get_last_sent_ready_snapshot(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select snapshot_table_name from
        eats_nomenclature.last_sent_ready_snapshot
        """,
    )
    rows = list(cursor)
    return rows[0][0] if rows else None


def get_snapshot_prefixes():
    return {
        'products': '//home/logfeller/logs/products-snapshot/1d',
        'places_products': '//home/logfeller/logs/places-products-snapshot/1d',
        'categories': '//home/logfeller/logs/categories-snapshot/1d',
        'categories_products': (
            '//home/logfeller/logs/categories-products-snapshot/1d'
        ),
        'categories_relations': (
            '//home/logfeller/logs/categories-relations-snapshot/1d'
        ),
        'default_assortments': (
            '//home/logfeller/logs/default-assortments-snapshot/1d'
        ),
    }


def build_yt_path(prefix, new_snapshot_table_name):
    return f'{prefix}/{new_snapshot_table_name}'


def fill_yt_tables(
        snapshot_prefixes,
        skip_snapshot,
        snapshot_name_to_skip,
        snapshot_name_to_skip_status,
        new_snapshot_table_name,
        yt_client,
):
    tables_schemas = {
        'products': [
            {'name': 'brand_id', 'type': 'int64'},
            {'name': 'public_id', 'type': 'string'},
        ],
        'places_products': [
            {'name': 'place_id', 'type': 'int64'},
            {'name': 'product_public_id', 'type': 'string'},
        ],
        'categories': [
            {'name': 'place_id', 'type': 'int64'},
            {'name': 'public_id', 'type': 'string'},
        ],
        'categories_products': [
            {'name': 'place_id', 'type': 'int64'},
            {'name': 'product_public_id', 'type': 'string'},
            {'name': 'category_public_id', 'type': 'string'},
        ],
        'categories_relations': [
            {'name': 'place_id', 'type': 'int64'},
            {'name': 'category_public_id', 'type': 'string'},
            {'name': 'parent_category_public_id', 'type': 'string'},
        ],
        'default_assortments': [
            {'name': 'place_id', 'type': 'int64'},
            {'name': 'assortment_name', 'type': 'string'},
        ],
    }
    place_id = 1
    brand_id = 1
    category_public_id = '10'
    product_public_id = '100'
    assortment_name = 'default_assortment'
    tables_data = {
        'products': {'brand_id': brand_id, 'public_id': product_public_id},
        'places_products': {
            'place_id': place_id,
            'product_public_id': product_public_id,
        },
        'categories': {'place_id': place_id, 'public_id': category_public_id},
        'categories_products': {
            'place_id': place_id,
            'product_public_id': product_public_id,
            'category_public_id': category_public_id,
        },
        'categories_relations': {
            'place_id': place_id,
            'category_public_id': category_public_id,
        },
        'default_assortments': {
            'place_id': place_id,
            'assortment_name': assortment_name,
        },
    }
    for name, prefix in snapshot_prefixes.items():
        path = build_yt_path(prefix, new_snapshot_table_name)
        # Remove all tables that are left from previous test.
        if yt_client.exists(path):
            yt_client.remove(path)

        if skip_snapshot and name == snapshot_name_to_skip:
            if snapshot_name_to_skip_status == 'empty_table':
                yt_client.create_table(
                    path,
                    attributes={
                        'schema': tables_schemas[name],
                        'dynamic': False,
                    },
                    recursive=True,
                )
            continue

        yt_client.create_table(
            path,
            attributes={'schema': tables_schemas[name], 'dynamic': False},
            recursive=True,
        )
        yt_client.write_table(path, [tables_data[name]])


def should_log_ready_snapshot(
        skip_snapshot, old_snapshot_table_name, new_snapshot_table_name,
):
    return not skip_snapshot and (
        old_snapshot_table_name != new_snapshot_table_name
    )
