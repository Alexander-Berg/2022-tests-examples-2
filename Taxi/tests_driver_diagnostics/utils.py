# pylint: disable=dangerous-default-value


PARK_ID = 'park_id1'
CONTRACTOR_PROFILE_ID = 'driver_id1'
PARK_CONTRACTOR_PROFILE_ID = 'park_id1_driver_id1'


def get_position(lat=55.744094, lon=37.627920):
    return {'lat': lat, 'lon': lon}


def get_internal_body(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        position=get_position(),
):
    return {
        'contractor_app': {
            'version_type': '',
            'version': '9.40',
            'platform': 'android',
        },
        'contractor_params': {
            'park_id': park_id,
            'contractor_profile_id': contractor_profile_id,
        },
        'position': position,
    }


def get_default_body(position=get_position()):
    body = {'client_reasons': []}
    if position:
        body['position'] = position
    return body


def get_headers():
    return {'Accept-language': 'ru', 'User-Agent': 'Taximeter 9.40 (1234)'}


def get_auth_headers(
        park_id=PARK_ID, contractor_profile_id=CONTRACTOR_PROFILE_ID,
):
    return {
        'X-Remote-IP': '12.34.56.78',
        'X-YaTaxi-Driver-Profile-Id': contractor_profile_id,
        'X-YaTaxi-Park-Id': park_id,
        'X-Request-Application-Version': '9.40',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'Accept-language': 'ru',
        'User-Agent': 'Taximeter 9.40 (1234)',
    }


def get_courier(status: str, external_id=None):
    return {
        'courier': {
            'id': 592591,
            'first_name': 'Самозанят',
            'middle_name': 'Самозанятович',
            'last_name': 'Самозанятов',
            'phone_number': '123456',
            'contact_email': 'test@test.test',
            'billing_type': 'self_employed',
            'courier_type': 'pedestrian',
            'registration_country': {
                'name': 'Российская Федерация',
                'code': 'RU',
            },
            'work_region': {'id': 1, 'name': 'Москва'},
            'project_type': 'eda',
            'courier_service': None,
            'work_status': status,
            'work_status_updated_at': '2018-04-30T13:21:57+03:00',
            'source': None,
            'external_id': external_id,
        },
    }
