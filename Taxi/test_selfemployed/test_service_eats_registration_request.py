# pylint: disable=unused-variable
import pytest


TEST_TOKEN = 'test_token'
TEST_TOKEN_HASH = (
    '387e742062298880381bd43e923cdf030ab0cfe18a0373e61c78f0df4b0c6e6d'
)
TEST_USER_AGENT = 'some user agent'
TEST_REAL_IP = '192.168.100.100'
TEST_HEADERS = {
    'X-Driver-Token': TEST_TOKEN,
    'X-Real-User-Agent': TEST_USER_AGENT,
    'X-Real-IP': TEST_REAL_IP,
}
TEST_DRIVER_PROFILE_ID = 'driver_id1'
TEST_PARK_ID = 'park_id1'


@pytest.fixture(autouse=True)
def mock_secdist(simple_secdist):
    simple_secdist['eats_courier'] = {
        'api_key': 'secret',
        'token_salt': 'salt',
    }
    return simple_secdist


@pytest.fixture(autouse=True)
def mock_parks(patch):
    @patch('taxi.clients.parks.ParksClient.get_driver_info')
    async def get_driver_info(park_id: str, driver_id: str):
        assert park_id == TEST_PARK_ID
        assert driver_id == TEST_DRIVER_PROFILE_ID
        return {
            'first_name': 'Тест',
            'last_name': 'Тестов',
            'middle_name': 'Тестович',
            'park_city': 'Москва',
        }

    @patch('taxi.clients.parks.ParksClient.get_driver_phone')
    async def get_driver_phone(park_id: str, driver_id: str):
        assert park_id == TEST_PARK_ID
        assert driver_id == TEST_DRIVER_PROFILE_ID
        return ['+79260000000']


async def test_empty_token(se_client):
    response = await se_client.post(
        '/service/eats-registration-request', json={}, headers={},
    )

    assert response.status == 400


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO eats_registration_states(
        token_hash,
        park_id, driver_profile_id,
        created_ts, created_tstz, expire_ts, expire_tstz, status)
        VALUES(
        '387e742062298880381bd43e923cdf030ab0cfe18a0373e61c78f0df4b0c6e6d',
        'park_id1', 'driver_id1',
        '2020-01-01', '2020-01-01+00', '2020-01-01', '2020-01-01+00', 'new'
        )
        """,
    ],
)
async def test_expired_token(se_client):
    response = await se_client.post(
        '/service/eats-registration-request', json={}, headers=TEST_HEADERS,
    )

    assert response.status == 400


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO eats_registration_states(
            token_hash,
            park_id, driver_profile_id, created_ts,
            expire_ts, expire_tstz, lock_ts, status)
        VALUES (
            '387e742062298880381bd43e923cdf030ab0cfe18a0373e61c78f0df4b0c6e6d',
            'park_id1', 'driver_id1', '2020-01-01',
            '2099-01-01', '2099-01-01+00', '2010-01-01', 'pending'
        )
        """,
        """
        INSERT INTO profiles
            (id, step, status,
            park_id, driver_id, bik, account_number, created_at,
            modified_at, address, post_code, phone, first_name, last_name,
            middle_name)
        VALUES
            ('profile_id', 'requisites', 'confirmed',
            'park_id1', 'driver_id1', '044525974',
            '12345678901234567890', now()::timestamp, now()::timestamp,
            'Москва, Кремль', '777777', '-', '-', '-', '-')
        """,
    ],
)
async def test_valid_token_and_data(se_client, mockserver):
    @mockserver.json_handler('/eats-courier/api/v2/courier-creation/create')
    def _eats_courier_mock(request):
        assert request.method == 'POST'
        assert request.json == {
            'registration_country': 'Российская Федерация',
            'registration_postcode': '777777',
            'registration_address': 'Москва, Кремль',
            'contact_email': 'some_mail@yandex.ru',
            'telegram_name': 'tg_login',
            'identity_document': 'passport',
            'bank_account_id': '12345678901234567890',
            'bic': '044525974',
            'first_name': 'Тест',
            'last_name': 'Тестов',
            'middle_name': 'Тестович',
            'phone_number': '+79260000000',
            'work_region': 'Москва',
        }
        return mockserver.make_response(json={})

    response = await se_client.post(
        '/service/eats-registration-request',
        json={
            'registration_country': 'Российская Федерация',
            'contact_email': 'some_mail@yandex.ru',
            'telegram_name': 'tg_login',
            'data_processing_accepted': 'True',
            'offer_accepted': 'True',
            'identity_document': 'passport',
        },
        headers=TEST_HEADERS,
    )

    assert response.status == 200
