import pytest


HEADERS = {'Accept-Language': 'ru_RU', 'User-Agent': 'Taximeter 9.61 (1234)'}
TRANSLATIONS = {
    'validate_country_invalidcountry_title': {'ru': 'Foreign DL'},
    'validate_country_invalidcountry_text': {'ru': 'cannot be accepted'},
    'validate_country_invalidlicense_title': {'ru': 'Invalid DL format'},
    'validate_country_invalidlicense_text': {'ru': 'Enter a valid DL'},
}


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={'enabled_countries': ['rus', 'fin']},
)
@pytest.mark.parametrize(
    'license_country, is_valid',
    [
        pytest.param(
            'RU', True, id='license_country the same as current_country',
        ),
        pytest.param(
            'KZ', True, id='license_country is supported in current_country',
        ),
        pytest.param(
            'FI',
            False,
            id='license_country is not supported in current_country',
        ),
    ],
)
async def test_validate_country(
        taxi_selfreg, mockserver, license_country, is_valid,
):
    response = await taxi_selfreg.get(
        '/selfreg/v1/validate-license',
        params={
            'token': 'token1',
            'current_country_code': 'RU',
            'license_country_code': license_country,
        },
        headers=HEADERS,
    )

    assert response.status == 200
    content = await response.json()
    assert content['is_valid'] == is_valid
    assert ('reason' in content) == (not is_valid)
    if 'reason' in content:
        expected_reason = {
            'code': 'invalid_license_country',
            'text': 'cannot be accepted',
            'title': 'Foreign DL',
            'url': 'https://example.com',
        }
        assert content['reason'] == expected_reason


@pytest.mark.translations(taximeter_backend_api_controllers=TRANSLATIONS)
@pytest.mark.config(
    TAXIMETER_SELFREG_SETTINGS={'enabled_countries': ['rus', 'fin']},
)
@pytest.mark.parametrize(
    'license_country, license_number, is_valid',
    [
        pytest.param('RU', '0123456789', True, id='matches template'),
        pytest.param('RU', 'ABCDEFGHIJ', False, id='does not match template'),
        pytest.param('KZ', 'ABCDEFGHIJ', True, id='no templates to match'),
    ],
)
async def test_validate_license(
        taxi_selfreg,
        mockserver,
        mock_personal,
        license_country,
        license_number,
        is_valid,
):
    response = await taxi_selfreg.get(
        '/selfreg/v1/validate-license',
        params={
            'token': 'token1',
            'current_country_code': 'RU',
            'license_country_code': license_country,
            'license_number': license_number,
        },
        headers=HEADERS,
    )

    assert response.status == 200
    content = await response.json()
    assert content['is_valid'] == is_valid
    assert ('reason' in content) == (not is_valid)
    assert ('reason' in content) == (not is_valid)
    if 'reason' in content:
        expected_reason = {
            'code': 'invalid_license_number',
            'text': 'Enter a valid DL',
            'title': 'Invalid DL format',
        }
        assert content['reason'] == expected_reason
