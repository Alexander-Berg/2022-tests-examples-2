import pytest


@pytest.fixture(name='v1_regions')
def handle_regions(taxi_eats_catalog):
    path = '/eats-catalog/v1/regions'

    async def get():
        return await taxi_eats_catalog.get(path)

    return get
