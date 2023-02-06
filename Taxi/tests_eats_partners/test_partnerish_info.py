import pytest


@pytest.mark.parametrize(
    'status_code, expected_json',
    [
        (400, {'uuid': '000'}),
        (
            200,
            {
                'uuid': 'abcd1',
                'email': 'email1@test.ya',
                'name': 'Test',
                'rest_name': 'Vkusno',
                'city': 'SPb',
                'address': 'Goroh street 491',
                'phone_number': '+79997778500',
                'consent_to_data_processing': True,
                'country_code': 'RU',
                'is_accepted': False,
            },
        ),
        (
            200,
            {
                'uuid': 'abcd2',
                'email': 'email2@test.ya',
                'name': 'Test',
                'rest_name': 'Vkusno',
                'city': 'SPb',
                'address': 'Goroh street 492',
                'phone_number': '+79997778500',
                'consent_to_data_processing': True,
                'country_code': 'RU',
                'is_accepted': True,
                'partner_id': 492492,
            },
        ),
        (
            200,
            {
                'uuid': 'abcd3',
                'email': 'email3@test.ya',
                'name': 'Test',
                'rest_name': 'Vkusno',
                'city': 'SPb',
                'address': 'Goroh street 493',
                'phone_number': '+79997778500',
                'consent_to_data_processing': True,
                'is_accepted': False,
            },
        ),
        (
            200,
            {
                'uuid': 'abcd4',
                'email': 'email4@test.ya',
                'name': 'Test',
                'rest_name': 'Vkusno',
                'city': 'SPb',
                'address': 'Goroh street 494',
                'phone_number': '+79997778500',
                'consent_to_data_processing': True,
                'personal_email_id': 'personal_email4_id',
                'country_code': 'RU',
                'is_accepted': False,
            },
        ),
    ],
)
@pytest.mark.config(
    EATS_PARTNERISH_SETTINGS={
        'registartion_url': 'test.ru',
        'sender_email': 'no-reply@yango.yandex.com',
        'registration_text': (
            'Пожалуйста завершите регистрацию заполнив информацию по ссылке,'
        ),
        'check_email_in_vendor': True,
        'enable_paths': True,
    },
)
async def test_partnerish_info(taxi_eats_partners, status_code, expected_json):
    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/login/partnerish/info',
        json={'uuid': expected_json['uuid']},
    )

    assert response.status_code == status_code
    if status_code == 200:
        assert response.json() == expected_json


@pytest.mark.config(
    EATS_PARTNERISH_SETTINGS={
        'registartion_url': 'test.ru',
        'sender_email': 'no-reply@yango.yandex.com',
        'registration_text': (
            'Пожалуйста завершите регистрацию заполнив информацию по ссылке,'
        ),
        'check_email_in_vendor': True,
        'enable_paths': False,
    },
)
async def test_partnerish_info_off_path(taxi_eats_partners):
    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/login/partnerish/info',
        json={'uuid': 'sdfsdfsdfsdfsdf-sdfsdfsdf-sdfsdfsd'},
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Path not support'}
