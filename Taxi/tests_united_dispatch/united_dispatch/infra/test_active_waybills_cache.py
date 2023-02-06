import pytest


@pytest.fixture(name='invalidate_waybills_cache')
async def _invalidate_waybills_cache(united_dispatch_unit):
    async def wrapper(*, update_type):
        assert update_type in {'full', 'incremental'}
        if update_type == 'full':
            await united_dispatch_unit.invalidate_caches(
                clean_update=True, cache_names=['active-waybills-cache'],
            )
        else:
            await united_dispatch_unit.invalidate_caches(
                clean_update=False, cache_names=['active-waybills-cache'],
            )

    return wrapper


async def test_waybill_update(
        create_segment,
        state_waybill_proposed,
        get_single_waybill,
        testpoint,
        invalidate_waybills_cache,
        increment_waybill_revision,
        update_type='incremental',
):
    """
        Check new waybill inserted in cache on update.
        Then check updated waybill updated in cache on update.
    """
    create_segment(crutches={'force_crutch_builder': True})

    await state_waybill_proposed()

    waybill = get_single_waybill()

    waybill_id = waybill['id']
    expected_waybill_revision = waybill['revision']

    @testpoint('active-waybills-cache::result')
    async def update_result(data):
        assert data['update_type'] == 'incremental'
        assert data['waybills'] == [
            {'id': waybill_id, 'revision': expected_waybill_revision},
        ]

    # check new waybill in cache
    await invalidate_waybills_cache(update_type=update_type)

    assert update_result.times_called == 1

    # check update waybill updates in cache
    update_result.flush()
    expected_waybill_revision = increment_waybill_revision(waybill_id)

    await invalidate_waybills_cache(update_type=update_type)

    assert update_result.times_called == 1


async def test_waybill_resolved(
        create_segment,
        state_waybill_proposed,
        get_single_waybill,
        testpoint,
        run_waybill_reader,
        invalidate_waybills_cache,
        cargo_dispatch,
        update_type='incremental',
):
    """
        Check resolved waybill deleted from cache on incremental update.
    """
    create_segment(crutches={'force_crutch_builder': True})

    await state_waybill_proposed()

    waybill = get_single_waybill()

    waybill_id = waybill['id']
    expected_waybills = [{'id': waybill_id, 'revision': waybill['revision']}]

    @testpoint('active-waybills-cache::result')
    async def update_result(data):
        assert data['update_type'] == update_type
        assert data['waybills'] == expected_waybills

    # check new waybill in cache
    await invalidate_waybills_cache(update_type=update_type)

    assert update_result.times_called == 1

    # check resolved waybill removed from cache
    expected_waybills = []

    cargo_dispatch.waybills.set_resolved(waybill_id)
    await run_waybill_reader()
    update_result.flush()

    await invalidate_waybills_cache(update_type=update_type)

    assert update_result.times_called == 1


@pytest.mark.config(
    UNITED_DISPATCH_WAYBILL_CACHE={
        'full': {'full_chunk_size': 2},
        'incremental': {'full_chunk_size': 2},
    },
)
async def test_chunks(
        state_waybill_proposed,
        create_segment,
        get_waybill_by_segment,
        testpoint,
        invalidate_waybills_cache,
        update_type='incremental',
):
    """
        Check cache updated by chunks.
        5 waybills, chunk size is 2.
    """

    segments = []
    for _ in range(5):
        segments.append(
            create_segment(crutches={'force_crutch_builder': True}),
        )

    await state_waybill_proposed()

    waybills = []
    for seg in segments:
        waybills.append(get_waybill_by_segment(seg.id))
    waybills.sort(key=lambda waybill: waybill['id'])

    @testpoint('active-waybills-cache::result')
    async def update_result(data):
        assert data['update_type'] == update_type
        data['waybills'].sort(key=lambda waybill: waybill['id'])
        assert data['waybills'] == [
            {'id': w['id'], 'revision': w['revision']} for w in waybills
        ]

    # check all waybills in cache
    await invalidate_waybills_cache(update_type=update_type)

    assert update_result.times_called == 1
