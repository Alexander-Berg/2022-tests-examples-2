from tests_eats_nomenclature_viewer.periodics.update_places_from_core import (
    constants,
)


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(constants.PERIODIC_NAME, is_distlock=True)
