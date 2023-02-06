import pytest


DEFAULT_HEADERS = {
    'X-Request-Language': 'ru',
    'X-YaTaxi-UserId': 'user_id_123',
    'X-Yandex-UID': 'yandex_uid_123',
}
DEFAULT_REQUEST = {'driver_id': 'abc123_def456', 'order_id': 'order_id_123'}

SFR_DEFAULT_RESP = {
    'profiles': [
        {
            'park_contractor_profile_id': 'inn_pd_id',
            'data': {
                'is_own_park': False,
                'do_send_receipts': True,
                'inn_pd_id': 'inn_pd_id',
            },
        },
    ],
}
PERSONAL_TIN_DEFAULT_RESP = {'id': 'inn_pd_id', 'value': '123321'}
UDRIVER_PHOTOS_DEFAULT_RESP = {
    'photos': {
        'avatar_image': {
            'url': 'avatar_image_url',
            'url_parts': {
                'key': 'avatar_image_url_parts_key',
                'path': 'avatar_image_url_parts_path',
            },
        },
        'profile_photo': {
            'url': 'profile_photo_url',
            'url_parts': {
                'key': 'profile_photo_url_parts_key',
                'path': 'profile_photo_url_parts_path',
            },
        },
    },
}


@pytest.mark.translations(
    client_messages={'taxiontheway.driver_tin_tmpl': {'ru': 'ИНН: %(tin)s'}},
)
async def test_simple(taxi_driver_map, mockserver, load_json):
    @mockserver.json_handler('/personal/v1/tins/retrieve')
    def _mock_personal(request):
        assert request.json['id'] == 'inn_pd_id'
        return PERSONAL_TIN_DEFAULT_RESP

    @mockserver.json_handler('/selfemployed-fns-replica/v1/profiles/retrieve')
    def _mock_sfr(request):
        return SFR_DEFAULT_RESP

    @mockserver.json_handler('/udriver-photos/4.0/orderperformerinfo')
    def _mock_udriver_photos(request):
        assert request.headers['X-YaTaxi-UserId'] == 'user_id_123'
        assert request.headers['X-Yandex-UID'] == 'yandex_uid_123'
        assert request.query['order_id'] == 'order_id_123'
        return UDRIVER_PHOTOS_DEFAULT_RESP

    response = await taxi_driver_map.post(
        '/totw/v1/driver/profile', DEFAULT_REQUEST, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('simple_response.json')


@pytest.mark.parametrize(
    'personal_resp_code,' 'sfr_resp_code,' 'udriver_photos_resp_code',
    [(500, 200, 200), (200, 500, 200), (200, 200, 500)],
)
@pytest.mark.translations(
    client_messages={'taxiontheway.driver_tin_tmpl': {'ru': 'ИНН: %(tin)s'}},
)
async def test_sources_errors(
        taxi_driver_map,
        mockserver,
        personal_resp_code,
        sfr_resp_code,
        udriver_photos_resp_code,
):
    @mockserver.json_handler('/personal/v1/tins/retrieve')
    def _mock_personal(request):
        if personal_resp_code == 200:
            return PERSONAL_TIN_DEFAULT_RESP
        return mockserver.make_response(
            status=personal_resp_code,
            json={'code': 'error_code', 'message': 'message'},
        )

    @mockserver.json_handler('/selfemployed-fns-replica/v1/profiles/retrieve')
    def _mock_sfr(request):
        if sfr_resp_code == 200:
            return SFR_DEFAULT_RESP
        return mockserver.make_response(
            status=sfr_resp_code,
            json={'code': 'error_code', 'message': 'message'},
        )

    @mockserver.json_handler('/udriver-photos/4.0/orderperformerinfo')
    def _mock_udriver_photos(request):
        if udriver_photos_resp_code == 200:
            return UDRIVER_PHOTOS_DEFAULT_RESP
        return mockserver.make_response(
            status=sfr_resp_code,
            json={'code': 'error_code', 'message': 'message'},
        )

    response = await taxi_driver_map.post(
        '/totw/v1/driver/profile', DEFAULT_REQUEST, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    expected = (
        UDRIVER_PHOTOS_DEFAULT_RESP
        if udriver_photos_resp_code == 200
        else {'extra_items': [{'title': 'ИНН: 123321'}]}
    )
    assert response.json() == expected
