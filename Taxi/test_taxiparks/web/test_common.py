import pytest


def request_by_method(client, route, method, params):
    if method == 'GET':
        response = client.get(
            route,
            query_string=params,
        )
    elif method == 'POST':
        response = client.post(
            route,
            json=params,
        )
    else:
        raise ValueError('Wrong (not implemented) method: "{}"'.format(method))
    return response


@pytest.mark.parametrize(
    'route, method, params, expected_code',
    [
        ('/get_token', 'GET',  {}, 200),
        ('/users_dyn', 'GET',  {'start': 0, 'count': 30, 'continue': True}, 401),
        ('/v2/taxiparks/history', 'GET',  {'taxipark_id': 'id'}, 401),
        ('/users/history', 'GET',  {'user_id': 'id'}, 401),
        ('/suggests/organization', 'GET',  {}, 401),

        ('/users/export', 'POST',  {'start': 0, 'count': 30, 'continue': True, 'csrf_token': "tiktoken"}, 403),
        ('/users/export', 'POST',  {'start': 0, 'count': 30, 'continue': True}, 403),
    ],
)
def test_no_auth(taxiparks_client, route, method, params, expected_code):
    response = request_by_method(taxiparks_client, route, method, params)
    assert response.status_code == expected_code
