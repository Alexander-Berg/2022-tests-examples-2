import pytest

# pylint: disable=C0103
pytestmark = [
    # pytest.mark.download_ml_resource(attrs={'type': 'autoreply'}),
    # pytest.mark.download_ml_resource(attrs={'type': 'autoreply_general'}),
    pytest.mark.download_ml_resource(attrs={'type': 'client_tickets_routing'}),
    # pytest.mark.download_ml_resource(attrs={'type': 'dkvu'}),
    # pytest.mark.download_ml_resource(
    #     attrs={'type': 'drivers_tickets_tagging'},
    # ),
    pytest.mark.download_ml_resource(attrs={'type': 'eats_support'}),
    pytest.mark.download_ml_resource(attrs={'type': 'smm_support_taxi'}),
    pytest.mark.download_ml_resource(attrs={'type': 'smm_support_eats'}),
    pytest.mark.download_ml_resource(attrs={'type': 'drivers_support'}),
    pytest.mark.download_ml_resource(attrs={'type': 'parks_support'}),
    pytest.mark.download_ml_resource(attrs={'type': 'remote_quality_control'}),
    pytest.mark.download_ml_resource(attrs={'type': 'music_support'}),
    # pytest.mark.download_ml_resource(
    #     attrs={'type': 'taxi_client_chat_support'},
    # ),
    pytest.mark.download_ml_resource(
        attrs={'type': 'eats_courier_hiring_by_phone'},
    ),
    pytest.mark.download_ml_resource(attrs={'type': 'yadrive_support'}),
    pytest.mark.download_ml_resource(attrs={'type': 'biometrics_verify'}),
    pytest.mark.download_ml_resource(attrs={'type': 'photo_rights'}),
    pytest.mark.download_ml_resource(attrs={'type': 'thermobags_check'}),
    pytest.mark.download_ml_resource(attrs={'type': 'drive_classifier'}),
    pytest.mark.download_ml_resource(attrs={'type': 'biometrics_features'}),
    pytest.mark.download_ml_resource(attrs={'type': 'duplicates_drive'}),
    pytest.mark.download_ml_resource(
        attrs={'type': 'zerosuggest_address_matcher'},
    ),
    pytest.mark.download_ml_resource(
        attrs={'type': 'taxi_drivers_chat_support'},
    ),
    pytest.mark.download_ml_resource(attrs={'type': 'medmasks_check'}),
    pytest.mark.download_ml_resource(attrs={'type': 'smm_taxi'}),
    pytest.mark.download_ml_resource(attrs={'type': 'smm_eats'}),
    pytest.mark.download_ml_resource(attrs={'type': 'smm_dzen'}),
    pytest.mark.download_ml_resource(
        attrs={'type': 'z_detector', 'version_maj': '2'},
    ),
]


@pytest.mark.xfail
def test_download(download_ml_resources):
    pass


@pytest.mark.servicetest
@pytest.mark.xfail
async def test_service(taxi_plotva_ml_web):
    pass
