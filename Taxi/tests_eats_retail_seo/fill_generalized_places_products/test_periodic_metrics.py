PERIODIC_NAME = 'fill-generalized-places-products-periodic'


async def test_periodic_metrics(
        enable_periodic_in_config, verify_periodic_metrics,
):
    enable_periodic_in_config(PERIODIC_NAME)
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)
