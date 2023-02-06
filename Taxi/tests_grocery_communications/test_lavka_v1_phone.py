import pytest


@pytest.mark.parametrize('country', [None, 'RU'])
async def test_basic(taxi_grocery_communications, passport_internal, country):
    client_ip = '1.1.1.1'
    language = 'ru'
    number = '+375336665544'
    track_id = 'track_id'
    code = '123456789'

    passport_internal.configure_headers(client_ip=client_ip)
    passport_internal.configure(status='ok', track_id=track_id)
    passport_internal.check(
        check_country=country,
        check_display_language=language,
        check_number=number,
        check_code=code,
    )

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/phone/submit',
        headers={'X-Remote-IP': client_ip},
        json={
            'display_language': language,
            'number': number,
            'country': country,
        },
    )

    assert response.status_code == 200
    assert response.json()['track_id'] == track_id
    assert passport_internal.times_phone_submit_called() == 1

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/phone/verify',
        headers={'X-Remote-IP': client_ip},
        json={'track_id': track_id, 'code': code},
    )

    assert response.status_code == 200
    assert passport_internal.times_phone_commit_called() == 1


@pytest.mark.parametrize(
    'error, expected_response_code',
    [
        ('display_language.empty', 400),
        ('display_language.invalid', 400),
        ('number.empty', 400),
        ('number.invalid', 400),
        ('country.empty', 400),
        ('country.invalid', 400),
        ('sms_limit.exceeded', 409),
        ('phone.confirmed', 400),
        ('phone.blocked', 405),
        ('backend.yasms_failed', 409),
    ],
)
async def test_submit_error_responses(
        taxi_grocery_communications,
        passport_internal,
        error,
        expected_response_code,
):
    client_ip = '1.1.1.1'
    language = 'ru'
    number = '+375336665544'

    passport_internal.configure_headers(client_ip=client_ip)
    passport_internal.configure(status='error', errors=[error])
    passport_internal.check(
        check_display_language=language, check_number=number,
    )
    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/phone/submit',
        headers={'X-Remote-IP': client_ip},
        json={'display_language': language, 'number': number},
    )

    assert response.status_code == expected_response_code


@pytest.mark.parametrize(
    'error, expected_response_code',
    [
        ('code.empty', 400),
        ('code.invalid', 400),
        ('sms.not_sent', 409),
        ('confirmations_limit.exceeded', 409),
        ('track_id.empty', 400),
        ('track_id.invalid', 400),
        ('track.invalid_state ', 400),
        ('track.not_found', 400),
    ],
)
async def test_commit_error_responses(
        taxi_grocery_communications,
        passport_internal,
        error,
        expected_response_code,
):
    client_ip = '1.1.1.1'
    track_id = 'any_track_id'
    code = '123456'

    passport_internal.configure_headers(client_ip=client_ip)
    passport_internal.configure(
        status='error', errors=[error], track_id=track_id,
    )
    passport_internal.check(check_code=code)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/phone/verify',
        headers={'X-Remote-IP': client_ip},
        json={'track_id': track_id, 'code': code},
    )

    assert response.status_code == expected_response_code
