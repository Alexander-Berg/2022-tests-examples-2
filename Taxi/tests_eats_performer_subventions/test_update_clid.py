import pytest

CLID_SETTINGS = {
    'period_sec': 30,
    'updated_period': 600,
    'parks_chunk_size': 100,
    'tasks_count': 1,
    'parks_per_task': 100,
    'write_chunk_size': 100,
}


@pytest.mark.config(
    EATS_PERFORMER_SUBVENTIONS_UPDATE_CLID_SETTINGS=CLID_SETTINGS,
)
async def test_update_clid(
        db_select_orders,
        taxi_eats_performer_subventions,
        mockserver,
        make_order,
):
    order_nr_1 = 'order-nr-1'
    park_id_1 = 'park-id-1'
    order_nr_2 = 'order-nr-2'
    park_id_2 = 'park-id-2'
    order_nr_3 = 'order-nr-3'
    order_status = 'created'

    make_order(
        eats_id=order_nr_1, order_status=order_status, park_id=park_id_1,
    )

    make_order(
        eats_id=order_nr_2, order_status=order_status, park_id=park_id_2,
    )

    make_order(eats_id=order_nr_3, order_status=order_status)

    city_id_1 = 'city-id-1'
    city_id_2 = 'city-id-2'
    clid_1 = 'clid-1'

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        return {
            'parks': [
                {
                    'id': park_id_1,
                    'login': 'login',
                    'is_active': True,
                    'city_id': city_id_1,
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': 'some park name',
                    'org_name': 'some park org name',
                    'provider_config': {'clid': clid_1, 'type': 'none'},
                    'geodata': {'lat': 0, 'lon': 1, 'zoom': 0},
                },
                {
                    'id': park_id_2,
                    'login': 'login',
                    'is_active': True,
                    'city_id': city_id_2,
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': 'some park name',
                    'org_name': 'some park org name',
                    'geodata': {'lat': 0, 'lon': 1, 'zoom': 0},
                },
            ],
        }

    task_name = 'update-clid-periodic'
    await taxi_eats_performer_subventions.run_periodic_task(task_name)

    assert _mock_parks_list.times_called == 1

    orders = db_select_orders()
    assert len(orders) == 3

    order = db_select_orders()[0]
    assert order['eats_id'] == order_nr_1
    assert order['park_id'] == park_id_1
    assert order['city_id'] == city_id_1
    assert order['clid'] == clid_1

    order = db_select_orders()[1]
    assert order['eats_id'] == order_nr_2
    assert order['park_id'] == park_id_2
    assert order['city_id'] == city_id_2
    assert order['clid'] is None

    order = db_select_orders()[2]
    assert order['eats_id'] == order_nr_3
    assert order['park_id'] is None
    assert order['city_id'] is None
    assert order['clid'] is None
