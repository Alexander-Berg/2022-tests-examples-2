CORE_REGIONS_HANDLER = '/eats-core/v1/export/regions'
PERIODIC_NAME = 'import-regions-from-core-periodic'


async def test_periodic_metrics(mockserver, verify_periodic_metrics):
    @mockserver.json_handler(CORE_REGIONS_HANDLER)
    def _mock_eats_core_retail_mapping(_):
        return {'payload': []}

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)
