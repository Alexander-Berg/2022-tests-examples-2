import aiohttp
import pytest

from taxi.integration_testing.framework import environment


pytest_plugins = [
    'taxi.integration_testing.examples.coffee_cups.integration_tests.deps.coffee_cups',
]


@pytest.fixture(scope='session')
def coffee_machine_container(
    testenv: environment.EnvironmentManager,
    coffee_cups_container: environment.TestContainer
) -> environment.TestContainer:
    cntnr = testenv.add_container(
        name='coffee-machine',
        image='registry.yandex.net/taxi/coffee-machine',
        package_json='taxi/integration_testing/examples/coffee_machine/integration_tests/deps/package.json',
        ports=[80],
        aliases=[
            'coffee-machine.test.yandex.net'
        ]
    )

    testenv.wait_container_healthy(cntnr, f'http://{cntnr.get_endpoint(80)}/ping')
    return cntnr


@pytest.fixture
async def coffee_machine_client(coffee_machine_container: environment.TestContainer) -> aiohttp.ClientSession:
    client = aiohttp.ClientSession(base_url=f'http://{coffee_machine_container.get_endpoint(80)}')
    yield client
    await client.close()
