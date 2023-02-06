import datetime
import json

import pytest

from tests_eats_customer_slots import utils


PERIODIC_NAME = 'partner-delivery-slots-cache-updater'
PLACES_COUNT = 101


@pytest.mark.now('2022-06-25T11:00:00+00:00')
@utils.partner_delivery_slots_config3(True, True, 'place', 42)
@utils.make_catalog_storage_cache(PLACES_COUNT)
async def test_partner_delivery_slots_cache(
        taxi_eats_customer_slots, redis_store, now,
):
    now = now.replace(tzinfo=datetime.timezone.utc)

    await taxi_eats_customer_slots.run_distlock_task(PERIODIC_NAME)

    for place_id in range(PLACES_COUNT):
        assert (
            json.loads(
                redis_store.get(
                    utils.make_partner_delivery_slots_redis_place_key(
                        place_id,
                    ),
                ),
            )
            == utils.make_partner_delivery_slots()
        )


@pytest.mark.now('2022-06-25T11:00:00+00:00')
@utils.partner_delivery_slots_config3(True, True, 'place', 42)
@utils.make_catalog_storage_cache(PLACES_COUNT)
async def test_partner_delivery_slots_cache_404(
        taxi_eats_customer_slots, mockserver, redis_store, now,
):
    now = now.replace(tzinfo=datetime.timezone.utc)

    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-average-delivery-slots',
    )
    # pylint: disable=invalid-name
    def mock_partner_average_delivery_slots(_):
        return mockserver.make_response(
            status=404, json={'code': 'NOT FOUND', 'message': 'Not found'},
        )

    await taxi_eats_customer_slots.run_distlock_task(PERIODIC_NAME)

    assert mock_partner_average_delivery_slots.times_called == 2

    for place_id in range(PLACES_COUNT):
        assert (
            redis_store.get(
                utils.make_partner_delivery_slots_redis_place_key(place_id),
            )
            is None
        )
