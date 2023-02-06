import pytest


def _create_headers(phone_id):
    return {
        'X-YaTaxi-User': 'personal_phone_id=personal_phone_id_1',
        'X-Yandex-UID': 'uid_1',
        'X-YaTaxi-PhoneId': phone_id,
        'X-YaTaxi-UserId': 'user_id_1',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app=iphone',
    }


DEFAULT_HEADERS = _create_headers('phone_id_1')

DEFAULT_REQUEST = {
    'user_context': {
        'pin_position': [-37, -55],
        'show_at': '2019-01-10T22:39:50+03:00',
    },
}


@pytest.fixture(autouse=True)
def _eda_shortlist(mockserver):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_shortlist(request):
        return mockserver.make_response(status=500)

    return _mock_eda_shortlist


@pytest.mark.experiments3(filename='exp3_dummy.json')
# @pytest.mark.experiments3(filename='exp3_objects_over_map.json')
async def test_objects_over_map_from_exp(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_objects_over_map.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        json=DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert response.status == 200, response.text
    assert 'objects_over_map' in response.json(), response.json()

    objects_over_map = response.json()['objects_over_map']

    assert len(objects_over_map) == 1
    assert objects_over_map[0] == {
        'id': 'some_promo_object',
        'priority': 999,
        'content': {
            'type': 'animation',
            'animation_count': 100,
            'tap_count': 10,
            'delay': 0.5,
            'source': {
                'url': 'https://aws.com/mds/anitaion.json',
                'type': 'remote',
            },
        },
        'show_policy': {'id': 'counter_id', 'max_show_count': 5},
        'action': {'type': 'deeplink', 'deeplink': 'yandextaxi://shortcuts'},
        'position': 'center_start',
        'accessibility_text': 'some_accessibility_text_key',
    }
