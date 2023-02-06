import pytest

from eats_retail_globus_parser.components.workers import quantum


@pytest.mark.parametrize(
    'config_value_piece_volume, config_value_order_step, expected_response',
    [
        [True, False, 'response_not_order_step_and_piece_volume.json'],
        [False, True, 'response_order_step_and_not_piece_volume.json'],
        [True, True, 'response_order_step_and_piece_volume.json'],
        [False, False, 'response_not_order_step_and_not_piece_volume.json'],
    ],
)
async def test_work_quantum(
        stq3_context,
        mds_mocks,
        config_value_piece_volume,
        config_value_order_step,
        expected_response,
        load_json,
):
    stq3_context.config.EATS_RETAIL_GLOBUS_PARSER_PIECE_VOLUME = (
        config_value_piece_volume
    )
    stq3_context.config.EATS_RETAIL_GLOBUS_PARSER_ACTIVE_ORDER_STEP = (
        config_value_order_step
    )

    worker = quantum.Quantum(stq3_context)
    data = await worker.perform('1', '1')

    assert mds_mocks.has_calls
    assert len(data) == 3
    assert data == load_json(expected_response)
