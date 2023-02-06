import pytest

HEADERS = {'User-Agent': 'Taximeter 9.61 (1234)'}
LINK1 = 'https://play.google.com/store/apps/details?id=com.example.android'
LINK2 = 'some-protocol://some-domain/some/uri?param1=value1&param2=value2'
LINK3 = 'param1=value1&param3=value3'


@pytest.mark.config(
    TAXIMETER_SELFREG_REGISTRATION_PARAMETER_SETTINGS={
        'allowed_parameters': ['id', 'param1', 'param3'],
    },
)
@pytest.mark.parametrize(
    'token, body, expected_response, expected_db_data',
    [
        [
            'token1',
            {'registration_link': LINK1},
            {'parameters': [{'name': 'id', 'value': 'com.example.android'}]},
            {'id': 'com.example.android'},
        ],
        [
            'token2',
            {
                'registration_link': LINK2,
                'additional_parameters': [
                    {'name': 'param1', 'value': 'value1-1'},
                    {'name': 'param3', 'value': 'value3'},
                ],
            },
            {
                'parameters': [
                    {'name': 'param1', 'value': 'value1-1'},
                    {'name': 'param3', 'value': 'value3'},
                ],
            },
            {'param1': 'value1-1', 'param3': 'value3'},
        ],
        [
            'token3',
            {'registration_link': LINK3},
            {
                'parameters': [
                    {'name': 'param1', 'value': 'value1'},
                    {'name': 'param3', 'value': 'value3'},
                ],
            },
            {'param1': 'value1', 'param3': 'value3'},
        ],
    ],
)
async def test_registration_parameters_post(
        taxi_selfreg, mongo, token, body, expected_response, expected_db_data,
):
    response = await taxi_selfreg.post(
        '/selfreg/v1/registration-parameters',
        params={'token': token},
        json=body,
        headers=HEADERS,
    )

    assert response.status == 200
    content = await response.json()
    assert expected_response == content

    profile = await mongo.selfreg_profiles.find_one({'token': token})
    assert profile.pop('registration_parameters') == expected_db_data
