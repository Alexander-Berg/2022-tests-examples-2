import pytest


@pytest.fixture(autouse=True)
def mock_admin_pipeline(admin_pipeline, request, load_json):
    admin_pipeline.mock_many_pipelines(
        request,
        load_json,
        admin_pipeline.Config(
            prefix='eda_surge_pipelines', consumers=['eda-surge'],
        ),
    )
