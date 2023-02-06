import pytest


@pytest.mark.parametrize(
    'route, method, params, expected_code',
    [
        ('/suggests', 'GET', {'field_name': 'some'}, 401),
        ('/suggests/country_by_city', 'GET', {'city': 'небесный_город'}, 401),
        ('/get_country_code', 'GET', {'city': 'небесный_город'}, 401),
        ('/agent', 'POST', {}, 403),
        ('/questionnaire', 'POST', {}, 403),
    ],
)
def test_no_auth(flask_client, route, method, params, expected_code):
    if method == 'GET':
        response = flask_client.get(
            route,
            query_string=params,
        )
    elif method == 'POST':
        response = flask_client.post(
            route,
            json=params,
        )
    else:
        raise ValueError('Wrong (not implemented) method: "{}"'.format(method))
    assert response.status_code == expected_code
