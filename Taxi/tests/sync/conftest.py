import pytest
from stall.sync.pigeon.product import ProductSync
from stall.sync.pigeon.product_group import ProductGroupSync
from stall.client.pigeon import client as pigeon_client

@pytest.fixture()
async def fake_grocery_pics_client():
    class Client:
        def __init__(self):
            self.call_count = 0

        async def upload(self, url):
            name = str(url).rsplit('/', maxsplit=1)[-1].split('.')[0]
            self.call_count += 1
            return f'https://s3/{name}.png'

    return Client()


@pytest.fixture()
async def prod_sync():
    prod = ProductSync(pim_client=None)
    prod.skip_images = 1

    return prod


@pytest.fixture
async def prod_sync_group():
    prod = ProductGroupSync(pim_client=None)
    prod.skip_images = 1

    return prod


@pytest.fixture()
async def prod_sync_client(uuid):

    prod = ProductSync(
        pim_client=pigeon_client,
        skip_images=True,
        skip_tanker=True,
        not_updated_stash_name='not_updated_products:' + uuid()
    )
    prod.skip_images = 1

    return prod


@pytest.fixture()
async def prod_sync_group_client(uuid):

    prod = ProductGroupSync(
        pim_client=pigeon_client,
        skip_images=True,
        skip_tanker=True,
        not_updated_stash_name='not_updated_product_groups:' + uuid()
    )
    prod.skip_images = 1

    return prod


@pytest.fixture()
async def prod_sync_pictures():
    prod = ProductSync(pim_client=None)

    return prod


@pytest.fixture()
async def prod_sync_group_pictures():
    prod = ProductGroupSync(pim_client=None)

    return prod
