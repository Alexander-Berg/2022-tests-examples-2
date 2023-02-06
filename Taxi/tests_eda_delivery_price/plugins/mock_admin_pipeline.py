import pytest


@pytest.fixture(autouse=True)
def mock_admin_pipeline(admin_pipeline, request, load_json):
    admin_pipeline.mock_single_pipeline(
        request,
        load_json,
        admin_pipeline.Config(
            prefix='delivery_price_pipeline',
            consumers=['eda-delivery-price', 'eda-delivery-price-surge'],
        ),
    )
