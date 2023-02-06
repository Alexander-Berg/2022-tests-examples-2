import pytest


@pytest.fixture(autouse=True)
def mock_admin_pipeline(admin_pipeline, request, load_json):
    admin_pipeline.mock_single_pipeline(
        request,
        load_json,
        admin_pipeline.Config(
            prefix='eda_surge_pipeline',
            consumers=['eda-surge', 'grocery-surge'],
        ),
    )
