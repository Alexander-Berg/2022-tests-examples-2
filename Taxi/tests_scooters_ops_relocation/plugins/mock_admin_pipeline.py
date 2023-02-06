import pytest


@pytest.fixture(autouse=True)
def mock_admin_pipeline(admin_pipeline, request, load_json):
    admin_pipeline.mock_single_pipeline(
        request,
        load_json,
        admin_pipeline.Config(
            prefix='algorithm_pipeline',
            consumers=['scooters-ops-relocation-algorithm'],
        ),
    )
