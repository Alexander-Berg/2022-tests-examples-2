import pytest

from tests_persey_core import utils


@pytest.mark.parametrize('full_update', [True, False])
async def test_bound_uids_cache(
        taxi_persey_core, persey_core_internal, pgsql, full_update,
):
    # Simple initial test:
    cursor = pgsql['persey_payments'].cursor()
    utils.fill_db(
        cursor,
        {
            'persey_payments.bound_uids': [
                {
                    'phonish_yandex_uid': '100',
                    'portal_yandex_uid': '101',
                    'updated_at': '2022-02-01T00:00:00+00:00',
                },
                {
                    'phonish_yandex_uid': '200',
                    'portal_yandex_uid': '201',
                    'updated_at': '2022-02-01T00:00:00+00:00',
                },
                {
                    'phonish_yandex_uid': '300',
                    'portal_yandex_uid': '301',
                    'updated_at': '2022-02-05T00:00:00+03:00',
                },
            ],
        },
    )
    expected_cache = {'100': 101, '200': 201, '300': 301}
    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['bound-uids-cache'],
    )
    result = await persey_core_internal.call('GetEntireBoundUidsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetBoundUidsCacheMaxUpdatedAt')
    assert result == '2022-02-04T21:00:00+00:00'

    # Add a new entry (same timestamp):
    utils.fill_db(
        cursor,
        {
            'persey_payments.bound_uids': [
                {
                    'phonish_yandex_uid': '400',
                    'portal_yandex_uid': '401',
                    'updated_at': '2022-02-05T01:00:00+04:00',
                },
            ],
        },
    )
    expected_cache.update({'400': 401})
    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['bound-uids-cache'],
    )
    result = await persey_core_internal.call('GetEntireBoundUidsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetBoundUidsCacheMaxUpdatedAt')
    assert result == '2022-02-04T21:00:00+00:00'

    # Add a new item (past timestamp):
    utils.fill_db(
        cursor,
        {
            'persey_payments.bound_uids': [
                {
                    'phonish_yandex_uid': '500',
                    'portal_yandex_uid': '501',
                    'updated_at': '2021-10-01T00:00:00+00:00',
                },
            ],
        },
    )
    if full_update:
        expected_cache.update({'500': 501})
    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['bound-uids-cache'],
    )
    result = await persey_core_internal.call('GetEntireBoundUidsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetBoundUidsCacheMaxUpdatedAt')
    assert result == '2022-02-04T21:00:00+00:00'

    # Add a new item (future timestamp):
    utils.fill_db(
        cursor,
        {
            'persey_payments.bound_uids': [
                {
                    'phonish_yandex_uid': '600',
                    'portal_yandex_uid': '601',
                    'updated_at': '2024-01-01T10:00:00+00:00',
                },
            ],
        },
    )
    expected_cache.update({'600': 601})
    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['bound-uids-cache'],
    )
    result = await persey_core_internal.call('GetEntireBoundUidsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetBoundUidsCacheMaxUpdatedAt')
    assert result == '2024-01-01T10:00:00+00:00'

    # Add a new item (older than max_updated_at, but should still be
    # thanks to the "update-correction" config setting):
    utils.fill_db(
        cursor,
        {
            'persey_payments.bound_uids': [
                {
                    'phonish_yandex_uid': '700',
                    'portal_yandex_uid': '701',
                    'updated_at': '2024-01-01T12:59:59+03:00',
                },
            ],
        },
    )
    expected_cache.update({'700': 701})
    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['bound-uids-cache'],
    )
    result = await persey_core_internal.call('GetEntireBoundUidsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetBoundUidsCacheMaxUpdatedAt')
    assert result == '2024-01-01T10:00:00+00:00'

    # Now modify some items:
    cursor.execute(
        'DELETE FROM persey_payments.bound_uids '
        'WHERE phonish_yandex_uid IN (\'100\',\'300\',\'600\')',
    )
    utils.fill_db(
        cursor,
        {
            'persey_payments.bound_uids': [
                {
                    'phonish_yandex_uid': '100',
                    'portal_yandex_uid': '102',
                    'updated_at': '2022-02-01T00:00:00+00:00',
                },
                {
                    'phonish_yandex_uid': '300',
                    'portal_yandex_uid': '501',
                    'updated_at': '2024-01-01T11:00:00+00:00',
                },
                {
                    'phonish_yandex_uid': '600',
                    'portal_yandex_uid': '602',
                    'updated_at': '2024-01-01T09:59:58+00:00',
                },
            ],
        },
    )
    if full_update:
        expected_cache.update({'100': 102})
    expected_cache.update({'300': 501, '600': 602})
    await taxi_persey_core.invalidate_caches(
        clean_update=full_update, cache_names=['bound-uids-cache'],
    )
    result = await persey_core_internal.call('GetEntireBoundUidsCache')
    assert result == expected_cache
    result = await persey_core_internal.call('GetBoundUidsCacheMaxUpdatedAt')
    assert result == '2024-01-01T11:00:00+00:00'


async def test_bound_uids_cache_dump_empty(
        taxi_persey_core, persey_core_internal,
):
    await taxi_persey_core.write_cache_dumps(names=['bound-uids-cache'])
    await taxi_persey_core.read_cache_dumps(names=['bound-uids-cache'])
    result = await persey_core_internal.call('GetEntireBoundUidsCache')
    assert result == {}
    result = await persey_core_internal.call('GetBoundUidsCacheMaxUpdatedAt')
    assert result == '1970-01-01T00:00:00+00:00'


async def test_bound_uids_cache_dump(
        taxi_persey_core, persey_core_internal, pgsql,
):
    cursor = pgsql['persey_payments'].cursor()
    utils.fill_db(
        cursor,
        {
            'persey_payments.bound_uids': [
                {
                    'phonish_yandex_uid': '100',
                    'portal_yandex_uid': '101',
                    'updated_at': '2022-02-01T00:00:00+00:00',
                },
                {
                    'phonish_yandex_uid': '200',
                    'portal_yandex_uid': '201',
                    'updated_at': '2022-02-01T00:00:00+00:00',
                },
                {
                    'phonish_yandex_uid': '300',
                    'portal_yandex_uid': '301',
                    'updated_at': '2022-02-05T00:00:00+03:00',
                },
            ],
        },
    )
    await taxi_persey_core.invalidate_caches(
        clean_update=True, cache_names=['bound-uids-cache'],
    )
    await taxi_persey_core.write_cache_dumps(names=['bound-uids-cache'])
    cursor.execute('DELETE FROM persey_payments.bound_uids')
    await taxi_persey_core.invalidate_caches(
        clean_update=True, cache_names=['bound-uids-cache'],
    )
    result = await persey_core_internal.call('GetEntireBoundUidsCache')
    assert result == {}
    await taxi_persey_core.read_cache_dumps(names=['bound-uids-cache'])
    result = await persey_core_internal.call('GetEntireBoundUidsCache')
    assert result == {'100': 101, '200': 201, '300': 301}
    result = await persey_core_internal.call('GetBoundUidsCacheMaxUpdatedAt')
    assert result == '2022-02-04T21:00:00+00:00'
