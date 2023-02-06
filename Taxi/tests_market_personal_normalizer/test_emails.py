from tests_market_personal_normalizer.mock_api_impl import personal


async def test_simple_email_store(
        taxi_market_personal_normalizer,
        mock_personal_emails_store: personal.PersonalStoreContext,
):
    mock_personal_emails_store.on_call(
        'some_mail@yandex.ru', True,
    ).personal_id = '1234'

    response = await taxi_market_personal_normalizer.post(
        'v1/emails/store', json={'value': 'some_mail@yandex.ru'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'value': 'some_mail@yandex.ru',
        'normalized_value': 'some_mail@yandex.ru',
        'id': '1234',
    }


async def test_simple_phone_without_validate(
        taxi_market_personal_normalizer,
        mock_personal_emails_store: personal.PersonalStoreContext,
):
    mock_personal_emails_store.on_call(
        'some_mail@mail.ru', False,
    ).personal_id = '123'

    response = await taxi_market_personal_normalizer.post(
        'v1/emails/store',
        json={'value': 'some_mail@mail.ru', 'validate': False},
    )

    assert response.status_code == 200
    assert response.json() == {
        'value': 'some_mail@mail.ru',
        'normalized_value': 'some_mail@mail.ru',
        'id': '123',
    }


async def test_wrong_phone(
        taxi_market_personal_normalizer,
        mock_personal_emails_store: personal.PersonalStoreContext,
):
    mock_response = mock_personal_emails_store.on_call('bad_mail.ru', True)
    mock_response.error_code = 400
    mock_response.error_message = 'Incorrect email'

    response = await taxi_market_personal_normalizer.post(
        'v1/emails/store', json={'value': 'bad_mail.ru'},
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Incorrect email'}
