import pytest


URL = '/4.0/mlutp/v1/nearest_zone'


def make_request_json(position, services):
    return {
        'position': position,
        'services': list({'service': each} for each in services),
    }


def sort_by_service(json):
    assert 'services' in json
    json['services'].sort(key=lambda item: item['service'])
    return json


@pytest.mark.parametrize('auth', [True, False])
@pytest.mark.parametrize(
    'header_locale, expected_locale',
    [('ru-RU', 'ru'), ('en-US', 'en'), ('de-DE', 'en')],
    ids=['ru', 'en', 'unsupported'],
)
@pytest.mark.parametrize(
    'request_json, expected_response',
    [
        (
            make_request_json([30.30, 59.95], ('taxi', 'eats')),
            'found_{locale}.json',
        ),
        (
            make_request_json([59.95, 30.30], ('taxi', 'eats')),
            'not_found_{locale}.json',
        ),
    ],
    ids=['found', 'not_found'],
)
async def test_nearest_zone(
        taxi_superapp_misc,
        testpoint,
        load_json,
        header_locale,
        expected_locale,
        request_json,
        expected_response,
        auth,
):
    @testpoint('handle_authorized')
    def handle_authorized(data):
        pass

    @testpoint('handle_unauthorized')
    def handle_unauthorized(data):
        pass

    headers = {'Accept-Language': header_locale}
    if auth:
        headers['X-YaTaxi-Session'] = 'taxi:test_user_id_xxx'
    response = await taxi_superapp_misc.post(
        URL, json=request_json, headers=headers,
    )
    assert response.status == 200
    if auth:
        assert handle_authorized.times_called == 1
        assert handle_unauthorized.times_called == 0
    else:
        assert handle_authorized.times_called == 0
        assert handle_unauthorized.times_called == 1

    actual_json = response.json()
    expected_json = load_json(expected_response.format(locale=expected_locale))
    assert sort_by_service(actual_json) == sort_by_service(expected_json)
