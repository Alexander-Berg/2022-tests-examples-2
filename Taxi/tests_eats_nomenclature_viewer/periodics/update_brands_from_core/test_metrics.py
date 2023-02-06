CORE_BRANDS_HANDLER = '/eats-core-retail/v1/brands/retrieve'
PERIODIC_NAME = 'update-brands-from-core-periodic'


async def test_periodic_metrics(mockserver, verify_periodic_metrics):
    @mockserver.json_handler(CORE_BRANDS_HANDLER)
    def _mock_eats_core_retail_mapping(_):
        return {'brands': []}

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)
