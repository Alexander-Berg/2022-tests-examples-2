from tests_eats_billing_processor.full_run import runner


async def test_launch(full_run_fixtures):
    await runner.run(full_run_fixtures, __file__)
