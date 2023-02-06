import pytest

# pylint: disable=C0103
pytestmark = [
    pytest.mark.download_ml_resource(
        attrs={'type': 'eats_cart_eta_statistics'},
    ),
    pytest.mark.download_ml_resource(attrs={'type': 'eats_cart_eta_models'}),
    pytest.mark.download_ml_resource(
        attrs={
            'type': 'grocery_suggest_models',
            'version_build': '1629945215',
        },
    ),
    pytest.mark.download_ml_resource(
        attrs={
            'type': 'grocery_suggest_statistics',
            'version_build': '1629945486',
        },
    ),
]


@pytest.mark.xfail
def test_download(download_ml_resources):
    pass


@pytest.mark.servicetest
@pytest.mark.xfail
async def test_service(taxi_plotva_ml_eats_web):
    pass
