# pylint: disable=redefined-outer-name, unused-variable
import pytest

RETAIL_QUEUE_LENGTH_CONFIG = pytest.mark.config(
    UMLAAS_EATS_RETAILQUEUELENGTH_ENABLED=True,
)


@RETAIL_QUEUE_LENGTH_CONFIG
async def test_retail_queue_length(
        taxi_umlaas_eats,
        retail_queue_length,
        retail_queue_length_filter,
        load_json,
        testpoint,
):
    @testpoint('queue-length-cache')
    def queue_length_tp(data):
        pass

    await taxi_umlaas_eats.enable_testpoints()
    response = await queue_length_tp.wait_call()

    data = response['data']
    assert data['num_items_loaded'] == 1
    assert data['num_pickers_info_items_loaded'] == 1
    assert data['loaded_orders'] == [
        {
            'place_id': '919191',
            'eats_id': '9366',
            'status': 'new',
            'estimated_picking_time': 1200,
            'status_created_at': '2021-07-28T15:15:00+00:00',
            'estimated_dispatch_attempt_time': '2021-07-28T15:15:00+00:00',
        },
    ]
    assert data['loaded_pickers_info'] == {
        'place_id': 919191,
        'brand_id': 100500,
        'country_id': 1,
        'region_id': 1,
        'time_zone': 'Moscow/Europe',
        'city': 'Moscow',
        'enabled': True,
        'working_intervals': [
            {
                'start': '2021-07-28T06:00:00+00:00',
                'end': '2021-07-28T21:00:00+00:00',
            },
        ],
        'estimated_waiting_time': 600,
        'free_pickers_count': 2,
        'total_pickers_count': 3,
        'is_place_closed': False,
        'is_place_overloaded': False,
    }
