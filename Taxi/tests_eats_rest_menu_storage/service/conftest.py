import pytest

from tests_eats_rest_menu_storage import models
from tests_eats_rest_menu_storage import sql

PLACE_ID = 1
BRAND_ID = 1


@pytest.fixture(name='setup_basic_item')
def _setup_basic_item():
    def do_setup_basic_item(db):
        db.add_category(
            models.PlaceMenuCategory(
                brand_menu_category_id='',
                place_id=PLACE_ID,
                origin_id='category_origin_id_1',
                name='category_name_1',
            ),
        )

        db.add_item(
            category_id=1,
            item=models.PlaceMenuItem(
                place_id=1, brand_menu_item_id='', origin_id='origin_id_1',
            ),
        )

    return do_setup_basic_item


@pytest.fixture(name='setup_brand_and_place')
def _setup_brand_and_place(database):
    sql.insert_brand(database, BRAND_ID)
    sql.insert_place(
        database,
        models.Place(
            place_id=PLACE_ID, brand_id=BRAND_ID, slug=f'place_{PLACE_ID}',
        ),
    )
