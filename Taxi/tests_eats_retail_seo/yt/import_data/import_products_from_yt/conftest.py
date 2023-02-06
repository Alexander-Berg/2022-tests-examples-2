import pytest

from . import constants
from .... import models


@pytest.fixture(name='add_brand')
def _add_brand(save_brands_to_db):
    def do_work():
        brand = models.Brand(
            brand_id=constants.BRAND_1_ID, slug='magnit', name='Магнит',
        )
        save_brands_to_db([brand])
        return brand

    return do_work


@pytest.fixture(name='add_snapshot_table')
def _add_snapshot_table(save_snapshot_tables_to_db):
    def do_work():
        snapshot_table = models.SnapshotTable(
            constants.SNAPSHOT_PRODUCTS_TABLE_ID,
            constants.SNAPSHOT_PRODUCTS_TABLE_PATH,
        )
        save_snapshot_tables_to_db([snapshot_table])

    return do_work


@pytest.fixture
def add_common_data(add_brand, add_snapshot_table):
    def do_work():
        brand = add_brand()
        add_snapshot_table()
        return brand

    return do_work
