import pytest


@pytest.mark.config(
    UNITED_DISPATCH_TYPED_GEOAREAS=['united_dispatch_geoareas'],
)
@pytest.mark.geoareas(tg_filename='geoareas.json')
async def test_cache(
        mock_typed_geoareas, state_waybill_proposed, create_segment, testpoint,
):
    @testpoint('dispatch::geoareas_cache')
    def batch_properties(data):
        assert data == 2

    create_segment()
    await state_waybill_proposed()

    assert mock_typed_geoareas.times_called
    assert batch_properties.times_called


@pytest.mark.config(
    UNITED_DISPATCH_TYPED_GEOAREAS=['united_dispatch_geoareas'],
)
@pytest.mark.geoareas(tg_filename='geoareas.json')
async def test_scoring_context(
        mock_typed_geoareas,
        state_waybill_proposed,
        create_segment,
        testpoint,
        exp_delivery_configs,
):
    @testpoint('delivery_planner::batch_properties')
    def batch_properties(data):
        batch_segments = data['batch_properties']['segments']

        for batch_segment in batch_segments:
            assert batch_segment['geoareas'] == [
                {
                    'name': 'moscow_activation',
                    'type': 'united_dispatch_geoareas',
                },
                {'name': 'moscow', 'type': 'united_dispatch_geoareas'},
            ]

    await exp_delivery_configs()
    create_segment()
    await state_waybill_proposed()
    assert mock_typed_geoareas.times_called
    assert batch_properties.times_called
