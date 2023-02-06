import pytest


async def test_not_found(taxi_maas):
    response = await taxi_maas.post(
        '/internal/maas/v1/admin/subscription/fetch-info',
        headers={},
        json={'subscription_id': 'some_id'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'not_found',
        'message': 'No such subscription',
    }


@pytest.mark.pgsql('maas', files=['admin.sql'])
@pytest.mark.parametrize(
    [
        'vtb_resp',
        'coupons_status',
        'coupons_resp',
        'coupons_times_called',
        'user_api_resp',
        'maas_resp',
    ],
    [
        (
            'vtb_error_resp.json',
            404,
            'coupons_error_resp.json',
            1,
            'user_api_ok_resp.json',
            'resp_basic_info.json',
        ),
        (
            'vtb_ok_resp.json',
            200,
            'coupons_ok_resp.json',
            1,
            'user_api_ok_resp.json',
            'resp_full_info.json',
        ),
        (
            'vtb_ok_resp.json',
            404,
            'coupons_error_resp.json',
            1,
            'user_api_ok_resp.json',
            'resp_with_vtb_info.json',
        ),
        (
            'vtb_ok_resp.json',
            200,
            'coupons_ok_resp.json',
            0,
            'user_api_empty_resp.json',
            'resp_with_vtb_info.json',
        ),
    ],
)
async def test_simple(
        taxi_maas,
        mockserver,
        load_json,
        vtb_resp,
        coupons_status,
        coupons_resp,
        coupons_times_called,
        user_api_resp,
        maas_resp,
):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_user_api(request):
        assert request.json == {
            'phone_ids': ['user_1_phone_id'],
            'fields': ['yandex_uid'],
            'primary_replica': False,
        }
        return load_json(user_api_resp)

    @mockserver.json_handler('/vtb-maas/api/0.1/user/info')
    def _mock_vtb(request):
        return mockserver.make_response(200, json=load_json(vtb_resp))

    @mockserver.json_handler('/coupons/internal/coupon/state')
    def _mock_coupons(request):
        assert request.json == {
            'coupon_code': 'user_1_coupon_id_1',
            'phone_id': 'user_1_phone_id',
            'yandex_uid': 'user_1_yandex_uid',
        }
        return mockserver.make_response(
            coupons_status, json=load_json(coupons_resp),
        )

    response = await taxi_maas.post(
        '/internal/maas/v1/admin/subscription/fetch-info',
        headers={},
        json={'subscription_id': 'user_1_sub_id_1'},
    )
    assert response.status_code == 200
    assert _mock_user_api.times_called
    assert _mock_vtb.times_called
    assert _mock_coupons.times_called == coupons_times_called
    assert response.json() == load_json(maas_resp)
