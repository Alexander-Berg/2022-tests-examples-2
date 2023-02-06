# pylint: disable=redefined-outer-name
from hackathon2020_client_product_py3.generated.cron import run_cron


async def test_example():
    await run_cron.main(
        ['hackathon2020_client_product_py3.crontasks.example', '-t', '0'],
    )
