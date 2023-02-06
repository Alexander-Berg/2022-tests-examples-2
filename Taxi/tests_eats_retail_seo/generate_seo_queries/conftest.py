import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_retail_seo_plugins import *  # noqa: F403 F401

from .. import models


@pytest.fixture
def generate_seo_query():
    def do_generate(
            product_type: models.ProductType = None,
            product_brand: models.ProductBrand = None,
            is_enabled: bool = True,
    ):
        slug = ''
        if product_type:
            slug += product_type.name
        if product_brand:
            if slug:
                slug += '-'
            slug += product_brand.name
        text = slug.replace('-', ' ')
        return models.SeoQuery(
            product_type=product_type,
            product_brand=product_brand,
            is_enabled=is_enabled,
            generated_data=models.SeoQueryData(
                slug=slug, query=text, title=text, description=text,
            ),
        )

    return do_generate
