import pytest


@pytest.mark.experiments3(filename='umlaas_offer_statistics_params.json')
async def test_ml_test_api(taxi_umlaas_pricing, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_pricing.post(
        '/umlaas-pricing/v1/offer-statistics', json=request,
    )
    assert response.status_code == 200

    ml_statistics = response.json()
    assert 'discount_v1' in ml_statistics and ml_statistics['discount_v1'] == 0
    assert (
        'discount_v1_shifted' in ml_statistics
        and ml_statistics['discount_v1_shifted'] == 1
    )
    assert 'discount_v2' in ml_statistics and ml_statistics['discount_v2'] == 1


@pytest.mark.experiments3(filename='umlaas_offer_statistics_params.json')
async def test_user_tags(taxi_umlaas_pricing, load_json):
    request = load_json('request_with_user_tags.json')
    response = await taxi_umlaas_pricing.post(
        '/umlaas-pricing/v1/offer-statistics', json=request,
    )
    assert response.status_code == 200

    ml_statistics = response.json()
    assert (
        'discount_v1' in ml_statistics and ml_statistics['discount_v1'] == -5
    )
