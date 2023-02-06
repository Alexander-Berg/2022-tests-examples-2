from tests_eats_retail_business_alerts.periodics.import_places_from_core import (
    constants,
)


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(constants.PERIODIC_NAME, is_distlock=True)
