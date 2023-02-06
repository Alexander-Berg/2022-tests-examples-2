def prepare_rq(path, park_id, driver_id):
    headers = {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_id,
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '8.80 (562)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
    }
    return dict(path=path, headers=headers)
