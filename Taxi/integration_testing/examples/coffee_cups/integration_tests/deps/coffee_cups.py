import aiohttp
import pytest

from taxi.integration_testing.framework import environment


@pytest.fixture(scope='session')
def coffee_cups_container(
    testenv: environment.EnvironmentManager
) -> environment.TestContainer:
    cntnr = testenv.add_container(
        name='coffee-cups',
        image='registry.yandex.net/taxi/coffee-cups',
        package_json='taxi/integration_testing/examples/coffee_cups/integration_tests/deps/package.json',
        ports=[80],
        aliases=[
            'coffee-cups.test.yandex.net'
        ]
    )

    testenv.wait_container_healthy(cntnr, f'http://{cntnr.get_endpoint(80)}/ping')
    return cntnr


@pytest.fixture
async def coffee_cups_client(coffee_cups_container: environment.TestContainer) -> aiohttp.ClientSession:
    client = aiohttp.ClientSession(base_url=f'http://{coffee_cups_container.get_endpoint(80)}')
    yield client
    await client.close()
