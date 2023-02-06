import pytest


@pytest.mark.config(
    EATS_RETAIL_GLOBUS_PARSER_CACHE_SETTINGS={
        'origin_ids': [1],
        'place_group_id': 1,
    },
)
@pytest.mark.parametrize(
    'cache_type,parser_mock',
    [
        ['availability', 'get_availabilities'],
        ['products', 'get_products'],
        ['categories', 'get_categories'],
        ['stocks', 'get_stocks'],
        ['prices', 'get_prices'],
    ],
)
async def test_should_cache(
        invalidate_cache_stq_runner,
        mds_mocks,
        parser_mocks,
        cache_type,
        parser_mock,
        proxy_mocks,
):
    await invalidate_cache_stq_runner(cache_type)
    assert mds_mocks.has_calls

    for mock in parser_mocks:
        if mock == parser_mock:
            assert parser_mocks[mock].has_calls
        else:
            assert not parser_mocks[mock].has_calls


@pytest.mark.parametrize(
    'cache_type',
    ['availability', 'products', 'categories', 'stocks', 'prices'],
)
async def test_should_not_cache_if_place_group_id_not_set(
        invalidate_cache_stq_runner, mds_mocks, parser_mocks, cache_type,
):
    await invalidate_cache_stq_runner(cache_type)
    assert not mds_mocks.has_calls

    for mock in parser_mocks:
        assert not parser_mocks[mock].has_calls


@pytest.mark.config(
    EATS_RETAIL_GLOBUS_PARSER_CACHE_SETTINGS={'place_group_id': 1},
)
@pytest.mark.parametrize(
    'cache_type',
    ['availability', 'categories', 'stocks', 'prices', 'quantum'],
)
async def test_should_not_cache_if_origin_ids_not_set(
        invalidate_cache_stq_runner, mds_mocks, parser_mocks, cache_type,
):
    await invalidate_cache_stq_runner(cache_type)
    assert not mds_mocks.has_calls

    for mock in parser_mocks:
        assert not parser_mocks[mock].has_calls


@pytest.mark.config(
    EATS_RETAIL_GLOBUS_PARSER_CACHE_SETTINGS={
        'origin_ids': [1],
        'place_group_id': 1,
    },
)
async def test_should_cache_quantum(invalidate_cache_stq_runner, mds_mocks):
    await invalidate_cache_stq_runner('quantum')
    assert mds_mocks.has_calls
