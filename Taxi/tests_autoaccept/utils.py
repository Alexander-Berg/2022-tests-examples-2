def get_auth_headers(
        park_id, driver_profile_id, user_agent='Taximeter 9.07 (1234)',
):
    app_version = ' '.join(user_agent.split(' ')[1:])
    return {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_profile_id,
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': app_version,
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'User-Agent': user_agent,
    }
