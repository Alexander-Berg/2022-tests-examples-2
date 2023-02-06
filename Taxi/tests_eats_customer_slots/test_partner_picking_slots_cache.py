import datetime

import pytest

from tests_eats_customer_slots import utils


@pytest.mark.now('2021-10-20T09:00:00+00:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@pytest.mark.config(EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': ['0']})
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize('place_id', [0, 1, 2, 3, 4, 5, 6, 7, 8, 666])
async def test_partner_picking_slots_cache(
        taxi_eats_customer_slots,
        testpoint,
        taxi_config,
        now,
        catalog_storage_cache,
        partner_picking_slots,
        place_id,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    order = utils.make_order(place_id=place_id, estimated_picking_time=200)
    brand_ids = {
        int(brand_id)
        for brand_id in taxi_config.get('EATS_PARTNER_SLOTS_BRANDS_SETTINGS')[
            'brand_ids'
        ]
    }

    @testpoint('partner_picking_slots')
    def partner_picking_slots_tp(data):
        assert place_id in partner_picking_slots
        assert data['place_id'] == place_id
        slots = partner_picking_slots[place_id]['slots']
        slots = [
            slot
            for slot in slots
            if datetime.datetime.fromisoformat(slot['from']) > now
        ]
        assert data['partner_picking_slots'] == slots

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200

    if place_id in catalog_storage_cache:
        place = catalog_storage_cache[place_id]
        assert partner_picking_slots_tp.times_called == int(
            'brand' in place
            and place['brand']['id'] in brand_ids
            and 'origin_id' in place
            and place_id in partner_picking_slots
            and bool(partner_picking_slots[place_id]['slots']),
        )
    else:
        assert partner_picking_slots_tp.times_called == 0


@pytest.mark.config(EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': ['0']})
@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 200},
    },
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 0,
            'brand': {
                'id': 0,
                'name': 'lenta',
                'picture_scale_type': 'aspect_fit',
                'slug': '0',
            },
            'enabled': True,
            'revision_id': 1,
            'origin_id': 'origin_id_0',
            'updated_at': '2021-11-02T20:00:00+03:00',
        },
    ],
)
@pytest.mark.parametrize(
    'status, response_json, updated_metric',
    [
        (400, {'code': '400', 'message': 'Bad Request'}, 'http_error_400'),
        (404, {'code': '404', 'message': 'Not Found'}, 'http_error_404'),
        (
            500,
            {'code': '500', 'message': 'Internal Server Error'},
            'unknown_error',
        ),
        (200, {'picking_slots': []}, 'empty_slots'),
        (
            200,
            {
                'picking_slots': [
                    {
                        'duration': 1800,
                        'from': '2021-10-20T12:00:00+00:00',
                        'slot_id': 'slot_0',
                        'to': '2021-10-20T13:00:00+00:00',
                    },
                ],
            },
            None,
        ),
    ],
)
async def test_partner_picking_slots_cache_metrics(
        taxi_eats_customer_slots,
        mockserver,
        taxi_eats_customer_slots_monitor,
        status,
        response_json,
        updated_metric,
):
    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-picking-slots',
    )
    def mock_get_picking_slots(request):
        return mockserver.make_response(status=status, json=response_json)

    await taxi_eats_customer_slots.tests_control(reset_metrics=True)
    metrics = await taxi_eats_customer_slots_monitor.get_metric(
        'partner-picking-slots-cache-metrics',
    )

    expected_metrics = {
        'http_error_400': 0,
        'http_error_404': 0,
        'unknown_error': 0,
        'empty_slots': 0,
    }
    if updated_metric:
        expected_metrics[updated_metric] = 1

    assert mock_get_picking_slots.times_called == 1
    assert metrics == expected_metrics
