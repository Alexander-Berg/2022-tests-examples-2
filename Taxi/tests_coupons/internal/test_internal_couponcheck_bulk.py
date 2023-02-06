import pytest

from tests_coupons import util


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)
@pytest.mark.filldb(promocode_series='eats_flow')
async def test_eats_flow_with_personal_phone_id(
        taxi_coupons, local_services_card,
):
    request = util.mock_request_couponcheck_bulk(
        coupons=['eatspromo'],
        payment_info={'type': 'cash'},
        service='eats',
        phone_id=None,
    )
    response = await taxi_coupons.post(
        'internal/couponcheck/bulk',
        request,
        headers={'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['coupons'][0]['valid'] is True


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)
@pytest.mark.filldb(promocode_series='eats_flow')
async def test_several_coupons(taxi_coupons, local_services_card):
    request = util.mock_request_couponcheck_bulk(
        coupons=['eatspromo', 'serialess000001'],
        payment_info={'type': 'cash'},
        service='eats',
        phone_id=None,
    )
    request['zone_classes'] = []
    response = await taxi_coupons.post(
        'internal/couponcheck/bulk',
        request,
        headers={'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['coupons']) == 2
    assert data['coupons'][0]['valid'] is True
    assert data['coupons'][1]['valid'] is False
