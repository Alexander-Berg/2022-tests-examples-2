# pylint: disable=dangerous-default-value


def get_auth_headers(park_id='db1', driver_profile_id='uuid1', token=None):
    response = {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_profile_id,
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.07 (1234)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'User-Agent': 'Taximeter 9.07 (1234)',
        'X-Idempotency-Token': 'token',
    }
    if token:
        response['X-Idempotency-Token'] = token
    return response
