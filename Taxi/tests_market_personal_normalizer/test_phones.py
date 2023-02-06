import pytest

from tests_market_personal_normalizer.mock_api_impl import personal


@pytest.fixture(autouse=True)
def territories_countries_list(mockserver, load_json):
    @mockserver.json_handler('/territories/v1/countries/list')
    def mock_countries_list(request):
        request.get_data()
        return load_json('countries.json')

    return mock_countries_list


async def test_simple_phone_store(
        taxi_market_personal_normalizer,
        mock_personal_phones_store: personal.PersonalStoreContext,
):
    mock_personal_phones_store.on_call(
        '+71234567890', True,
    ).personal_id = '100500'

    response = await taxi_market_personal_normalizer.post(
        'v1/phones/store', json={'value': '+7-123-45-67-890'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'value': '+7-123-45-67-890',
        'normalized_value': '+71234567890',
        'id': '100500',
    }


async def test_simple_phone_without_validate_store(
        taxi_market_personal_normalizer,
        mock_personal_phones_store: personal.PersonalStoreContext,
):
    mock_personal_phones_store.on_call(
        '+71234567890', False,
    ).personal_id = '100501'

    response = await taxi_market_personal_normalizer.post(
        'v1/phones/store',
        json={'value': '+7-123-45-67-890', 'validate': False},
    )

    assert response.status_code == 200
    assert response.json() == {
        'value': '+7-123-45-67-890',
        'normalized_value': '+71234567890',
        'id': '100501',
    }


async def test_wrong_phone_store(
        taxi_market_personal_normalizer,
        mock_personal_phones_store: personal.PersonalStoreContext,
):
    mock_response = mock_personal_phones_store.on_call('+70987654321', True)
    mock_response.error_code = 400
    mock_response.error_message = 'Some error message'

    response = await taxi_market_personal_normalizer.post(
        'v1/phones/store', json={'value': '+7-098-76-54-321'},
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Some error message'}


@pytest.mark.parametrize(
    'input_phone,normalized_phone,country',
    [
        (
            '8-111-11-11-111',
            '+71111111111',
            None,
        ),  # Default country is Russia. National code 8 will change to +7
        (
            '8-222-22-22-222-22',
            '8222222222222',
            'rus',
        ),  # Wrong phone lenght. So just left digits
        (
            '8-111-11-11-11',
            '8111111111',
            'aze',
        ),  # Azerbaijan has national code 0.
        # Incorrect national code, so just left digits
        (
            '0-111-11-11-11',
            '+994111111111',
            'aze',
        ),  # Azerbaijan has national code 0.
        # Correct national code will change to +994
    ],
)
async def test_territories_phone(
        taxi_market_personal_normalizer,
        mock_personal_phones_store: personal.PersonalStoreContext,
        input_phone,
        normalized_phone,
        country,
):
    mock_personal_phones_store.on_call(
        normalized_phone, True,
    ).personal_id = '100500'

    request_body = {'value': input_phone}
    if country is not None:
        request_body['country'] = country

    response = await taxi_market_personal_normalizer.post(
        'v1/phones/store', json=request_body,
    )

    assert response.status_code == 200
    assert response.json() == {
        'value': input_phone,
        'normalized_value': normalized_phone,
        'id': '100500',
    }
