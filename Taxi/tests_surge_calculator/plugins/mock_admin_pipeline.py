import pytest


@pytest.fixture(autouse=True)
def mock_admin_pipeline(admin_pipeline, mockserver, request, load_json):
    admin_pipeline.mock_single_pipeline(
        request,
        load_json,
        admin_pipeline.Config(
            prefix='surge_pipeline',
            consumers=['taxi-surge'],
            service=admin_pipeline.Service(tvm_name='surge-calculator'),
        ),
    )


@pytest.fixture()
def mock_admin_pipelines(admin_pipeline, mockserver, request, load_json):
    admin_pipeline.mock_many_pipelines(
        request,
        load_json,
        admin_pipeline.Config(
            prefix='surge_pipelines',
            consumers=['taxi-surge'],
            service=admin_pipeline.Service(tvm_name='surge-calculator'),
        ),
    )
