def da_headers(picker_id='1'):
    return {
        'Accept-Language': 'en',
        'X-Remote-IP': '12.34.56.78',
        'X-YaEda-CourierId': picker_id,
        'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
        'X-YaTaxi-Park-Id': 'park_id1',
        'X-Request-Application': 'XYPro',
        'X-Request-Application-Version': '9.99 (9999)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'ios',
    }
