from tests_eats_nomenclature_viewer.periodics.update_places_from_core import (
    constants,
)
from tests_eats_nomenclature_viewer import models


async def test_core_handler_batching(
        taxi_eats_nomenclature_viewer,
        mockserver,
        mock_core_handler,
        testpoint_periodic_ok,
        sql,
        update_taxi_config,
):
    batch_size = 2
    update_taxi_config(
        'EATS_NOMENCLATURE_VIEWER_EXTERNAL_HANDLER_SETTINGS',
        {'core_brand_places_retrieve_batch_size': batch_size},
    )

    brand_id = sql.save(models.Brand())

    places = [
        models.Place(brand_id=brand_id) for _ in range(0, batch_size * 3 + 1)
    ]

    @mockserver.json_handler(constants.CORE_PLACES_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        nonlocal places

        limit = request.query.get('limit')
        cursor = int(request.query.get('cursor', '0'))
        places_to_mock = places[cursor:limit]
        cursor += len(places_to_mock)
        return mock_core_handler.generate_mock_data(
            places_to_mock, cursor=str(cursor) if places_to_mock else None,
        )

    # save the same data
    await taxi_eats_nomenclature_viewer.run_distlock_task(
        constants.PERIODIC_NAME,
    )
    assert testpoint_periodic_ok.has_calls

    db_places = sql.load_all(models.Place)
    assert sorted([i.place_id for i in db_places]) == sorted(
        [i.place_id for i in places],
    )
