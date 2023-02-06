import pytest


@pytest.fixture(autouse=True)
def mock_admin_pipeline(admin_pipeline, request, load_json):
    admin_pipeline.mock_many_pipelines(
        request,
        load_json,
        admin_pipeline.Config(
            prefix='eats_logistics_performer_payouts_pipeline',
            consumers=[
                'eats-logistics-performer-payouts',
                'eats-logistics-courier-demand',
                'eats-logistics-predict-cpo',
            ],
        ),
    )
