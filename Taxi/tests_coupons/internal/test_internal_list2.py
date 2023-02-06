import pytest

from tests_coupons import util


@pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)
@pytest.mark.parametrize(
    'promocode, yandex_uid', [('eatswithreason1234', '4026')],
)
async def test_description_from_reason(
        local_services, taxi_coupons, promocode, yandex_uid,
):
    local_services.add_card()

    request = util.mock_request_internal_list(
        yandex_uids=[yandex_uid],
        services=['eats'],
        service='eats',
        phone_id='5bbb5faf15870bd76635d5e2',
        brand_names=['eats', 'yataxi'],
    )
    response = await util.make_internal_list_request(
        taxi_coupons,
        request,
        {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
    )
    assert response.status_code == 200
    assert (
        response.json()['coupons'][0]['description']
        == 'Ресторан Большая кувшинка извиняется'
    )
