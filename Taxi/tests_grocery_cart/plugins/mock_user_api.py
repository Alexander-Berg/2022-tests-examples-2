import pytest

PHONE_ID = 'phone_id'
PERSONAL_PHONE_ID = 'personal_phone_id'


@pytest.fixture(name='user_api')
def mock_user_api(mockserver):
    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve')
    def _create(request):
        assert 'personal_phone_id' in request.json
        return {
            'id': PHONE_ID,
            'phone': '+70009999987',
            'type': 'yandex',
            'is_taxi_staff': False,
            'is_yandex_staff': False,
            'is_loyal': False,
            'stat': {
                'total': 0,
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
                'fake': 0,
            },
        }

    return _create
