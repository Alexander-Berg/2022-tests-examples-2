import pytest


@pytest.mark.config(EATS_RETAIL_GLOBUS_PARSER_AVAILABILITY_LIMIT=500)
async def test_should_correct_parse_availability_with_limit(
        parse_task_stq_runner,
        stq3_context,
        procaas_parsed_mocks,
        mds_mocks,
        parser_mocks,
        proxy_mocks,
):
    await parse_task_stq_runner('availability', 'availability')
    assert procaas_parsed_mocks.has_calls
    assert mds_mocks.has_calls
    assert not parser_mocks['get_availabilities'].has_calls
    assert not parser_mocks['get_prices'].has_calls
    assert not parser_mocks['get_stocks'].has_calls


@pytest.mark.config(EATS_RETAIL_GLOBUS_PARSER_AVAILABILITY_LIMIT=0)
async def test_should_correct_parse_availability_without_limit(
        parse_task_stq_runner,
        stq3_context,
        procaas_parsed_mocks,
        mds_mocks,
        parser_mocks,
        proxy_mocks,
):
    await parse_task_stq_runner('availability', 'availability')
    assert procaas_parsed_mocks.has_calls
    assert mds_mocks.has_calls
    assert not parser_mocks['get_availabilities'].has_calls
    assert not parser_mocks['get_prices'].has_calls
    assert not parser_mocks['get_stocks'].has_calls


async def test_should_correct_parse_stocks(
        parse_task_stq_runner,
        stq3_context,
        procaas_parsed_mocks,
        mds_mocks,
        parser_mocks,
        proxy_mocks,
):
    await parse_task_stq_runner('stocks', 'stock')
    assert procaas_parsed_mocks.has_calls
    assert mds_mocks.has_calls
    assert not parser_mocks['get_availabilities'].has_calls
    assert not parser_mocks['get_prices'].has_calls
    assert not parser_mocks['get_stocks'].has_calls


async def test_should_correct_parse_prices(
        parse_task_stq_runner,
        stq3_context,
        procaas_parsed_mocks,
        mds_mocks,
        parser_mocks,
        proxy_mocks,
):
    await parse_task_stq_runner('prices', 'price')
    assert procaas_parsed_mocks.has_calls
    assert mds_mocks.has_calls
    assert not parser_mocks['get_availabilities'].has_calls
    assert not parser_mocks['get_prices'].has_calls
    assert not parser_mocks['get_stocks'].has_calls


@pytest.mark.config(
    EATS_RETAIL_GLOBUS_PARSER_SETTINGS={'enable_marking_type': True},
)
@pytest.mark.config(EATS_RETAIL_GLOBUS_PARSER_MARKING_TYPE={'0': 'test'})
async def test_should_correct_parse_nomenclature(
        parse_task_stq_runner,
        stq3_context,
        procaas_parsed_mocks,
        mds_mocks,
        parser_mocks,
        proxy_mocks,
):
    await parse_task_stq_runner('nomenclature', 'nomenclature')
    assert procaas_parsed_mocks.has_calls
    assert mds_mocks.has_calls
    assert not parser_mocks['get_availabilities'].has_calls
    assert not parser_mocks['get_prices'].has_calls
    assert not parser_mocks['get_stocks'].has_calls
    assert not parser_mocks['get_products'].has_calls
