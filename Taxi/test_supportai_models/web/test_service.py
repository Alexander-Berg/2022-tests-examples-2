import pytest


@pytest.fixture
def taxi_supportai_models_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_supportai_models_mocks')
@pytest.mark.download_ml_resource(attrs={'type': 'detmir_dialog'})
@pytest.mark.config(
    SUPPORTAI_MODELS_SETTINGS={
        'models': [
            {
                'name': 'detmir_dialog',
                'shard_id': 'shard1',
                'worker_id': 0,
                'type': 'one_message_text_classification',
            },
        ],
    },
)
async def test_ping(taxi_supportai_models_web):
    response = await taxi_supportai_models_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''


@pytest.mark.xfail
@pytest.mark.download_ml_resource(attrs={'type': 'ya_drive_dialog'})
@pytest.mark.download_ml_resource(attrs={'type': 'detmir_dialog'})
@pytest.mark.download_ml_resource(attrs={'type': 'justschool_dialog'})
@pytest.mark.download_ml_resource(
    attrs={'type': 'russian_post_b2b_orders_dialog'},
)
@pytest.mark.download_ml_resource(attrs={'type': 'taxi_client_dialog'})
def test_download(download_ml_resources):
    pass
