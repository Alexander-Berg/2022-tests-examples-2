from typing import Optional

import jwt


def get_auth_token(
        user_id: int,
        device_uuid: str = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
):
    secret = 'jwtSecretToken'
    raw_token = jwt.encode(
        {
            'iss': 'https://api-tada.helix.am',
            'aud': 'https://api-tada.helix.am',
            'iat': 1622740197,
            'nbf': 1622740197,
            'exp': 1854276197,
            'id': user_id,
            'device_uuid': device_uuid,
        },
        secret,
        algorithm='HS256',
    )
    token = raw_token.decode()
    return token


def get_auth_headers(
        user_id: int,
        device_uuid: str = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
):
    token = get_auth_token(user_id, device_uuid)
    headers = {'Authorization': f'Bearer {token}'}
    return headers


async def create_offer(
        web_app_client, headers, expected_response_status=200, **kwargs,
):
    request_body = {
        'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5K',
        'point_a': 'point_a',
        'point_b': 'point_b',
        'point_a_lat': 56.354,
        'point_a_long': 53.532,
        'point_b_lat': 34.432,
        'point_b_long': 56.322,
        'points_data': 'points_data',
        'entrance': '1',
        'comment': 'comment',
        'initial_price': 35.5,
        'payment_method_id': 1,
        'payment_method': 'cash',
        'zone_id': 34,
        'country_id': 87,
        'direction_map_url': 'direction_map_url',
    }

    for name, value in kwargs.items():
        request_body[name] = value

    response = await web_app_client.post(
        '/v3/user/offer/create', headers=headers, json=request_body,
    )
    assert response.status == expected_response_status
    return response


def create_persuggest_element(
        lat: Optional[float],
        lon: Optional[float],
        title: str = 'Estate business center 5',
        log: str = 'super_log',
):
    element: dict = {
        'title': {'text': title, 'hl': []},
        'uri': 'super_uri',
        'log': log,
        'method': 'method',
        'lang': '',
        'text': 'text',
        'subtitle': {'text': 'subtitle', 'hl': []},
    }
    if lat is not None and lon is not None:
        element['position'] = [lon, lat]
    return element
