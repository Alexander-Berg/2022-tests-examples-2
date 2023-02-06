import pytest

from . import utils


@utils.send_order_events_config()
@pytest.mark.parametrize('enabled', [False, True])
async def test_processing_events_config3(
        taxi_eats_picker_orders,
        experiments3,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_processing,
        enabled,
):
    experiments3.add_experiment3_from_marker(
        utils.send_order_events_config(enabled), None,
    )
    item_data = generate_order_item_data(measure_v1=False)
    order_data = generate_order_data(items=[item_data])

    mock_eatspickeritemcategories(order_data['place_id'])
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200
    assert mock_processing.times_called == int(enabled)
