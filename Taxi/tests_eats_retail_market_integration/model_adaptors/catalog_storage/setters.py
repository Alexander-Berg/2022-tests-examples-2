from typing import List

import pytest

from tests_eats_retail_market_integration.eats_catalog_internals import storage
from tests_eats_retail_market_integration import models


@pytest.fixture(name='save_brand_places_to_storage')
def _save_brand_places_to_storage(eats_catalog_storage):
    def impl(brands: List[models.Brand]):
        for brand in brands:
            for place in brand.get_places().values():
                eats_catalog_storage.add_place(
                    storage.Place(
                        place_id=int(place.place_id),
                        slug=place.slug,
                        brand=storage.Brand(brand_id=int(brand.brand_id)),
                        business=storage.Business.Shop,
                    ),
                )

    return impl
