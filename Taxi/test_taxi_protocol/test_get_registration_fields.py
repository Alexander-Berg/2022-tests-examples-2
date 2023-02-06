import pytest


CONFIG = {
    'host.ru': [
        {'id': 'unique_field_id', 'type': 'text', 'name': 'reg_field.phone'},
        {
            'id': 'another_unique_field_id',
            'type': 'text',
            'name': 'reg_field.email',
        },
        {
            'id': 'other_unique_field_id',
            'type': 'text',
            'name': 'reg_field.invalid',
        },
    ],
}

TRANSLATIONS = {
    'reg_field.phone': {'ru': 'Номер телефона', 'en': 'Phone'},
    'reg_field.email': {'ru': 'Адрес электронной почты', 'en': 'Email'},
}


@pytest.mark.config(SUPPORT_CHAT_REGISTRATION_FIELDS=CONFIG)
@pytest.mark.parametrize(
    'host,expected_result',
    [
        ('host.ru', {'registration_fields': CONFIG['host.ru']}),
        ('HoSt.ru', {'registration_fields': CONFIG['host.ru']}),
        ('unknown_host.net', {'registration_fields': []}),
        ('', {'registration_fields': []}),
    ],
)
async def test_get_registration_fields(protocol_client, host, expected_result):
    query = f'?source_domain={host}' if host else ''
    response = await protocol_client.get(
        f'/eats/v1/website_support_chat/v1/registration_fields{query}',
    )
    assert response.status == 200
    result = await response.json()
    assert result == expected_result

    response = await protocol_client.get(
        f'/eats/v1/website_support_chat/v1/registration_fields{query}/',
    )
    assert response.status == 200
    result = await response.json()
    assert result == expected_result


@pytest.mark.config(SUPPORT_CHAT_REGISTRATION_FIELDS=CONFIG)
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    'headers,expected_result',
    [
        (
            {'Accept-Language': 'ru'},
            [
                {
                    'id': 'unique_field_id',
                    'type': 'text',
                    'name': 'Номер телефона',
                },
                {
                    'id': 'another_unique_field_id',
                    'type': 'text',
                    'name': 'Адрес электронной почты',
                },
                {
                    'id': 'other_unique_field_id',
                    'type': 'text',
                    'name': 'reg_field.invalid',
                },
            ],
        ),
        (
            {'Accept-Language': 'en'},
            [
                {'id': 'unique_field_id', 'type': 'text', 'name': 'Phone'},
                {
                    'id': 'another_unique_field_id',
                    'type': 'text',
                    'name': 'Email',
                },
                {
                    'id': 'other_unique_field_id',
                    'type': 'text',
                    'name': 'reg_field.invalid',
                },
            ],
        ),
        (
            {'Accept-Language': 'uk'},
            [
                {
                    'id': 'unique_field_id',
                    'type': 'text',
                    'name': 'reg_field.phone',
                },
                {
                    'id': 'another_unique_field_id',
                    'type': 'text',
                    'name': 'reg_field.email',
                },
                {
                    'id': 'other_unique_field_id',
                    'type': 'text',
                    'name': 'reg_field.invalid',
                },
            ],
        ),
        (
            {'Accept-Language': 'ru,en;q=0.9'},
            [
                {
                    'id': 'unique_field_id',
                    'type': 'text',
                    'name': 'Номер телефона',
                },
                {
                    'id': 'another_unique_field_id',
                    'type': 'text',
                    'name': 'Адрес электронной почты',
                },
                {
                    'id': 'other_unique_field_id',
                    'type': 'text',
                    'name': 'reg_field.invalid',
                },
            ],
        ),
    ],
)
async def test_registration_fields_translations(
        protocol_client, headers, expected_result,
):
    response = await protocol_client.get(
        f'/eats/v1/website_support_chat/v1/registration_fields'
        f'?source_domain=host.ru',
        headers=headers,
    )
    assert response.status == 200
    result = await response.json()
    assert result['registration_fields'] == expected_result
