def make_park(
        park_id='park1',
        clid='clid1',
        is_active=True,
        driver_partner_source='self_assign',
        fleet_type='uberdriver',
):
    return {
        'id': park_id,
        'city_id': 'city1',
        'country_id': 'rus',
        'driver_partner_source': driver_partner_source,
        'fleet_type': fleet_type,
        'is_active': is_active,
        'is_billing_enabled': False,
        'is_franchising_enabled': True,
        'demo_mode': False,
        'locale': 'locale4',
        'login': 'login4',
        'name': 'name4',
        'provider_config': {
            'apikey': 'apikey1',
            'clid': clid,
            'type': 'production',
        },
        'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
    }


NICE_PARK = make_park()
FLEET_API_CLIENT_ID = 'antontodua'
FLEET_API_KEY_ID = '17'
X_REAL_IP = '8.7.6.5'
PARK_ID = '123'

DEFAULT_HEADERS_BASE = {'X-Real-Ip': X_REAL_IP, 'X-Park-ID': PARK_ID}

DEFAULT_HEADERS = {
    **DEFAULT_HEADERS_BASE,
    'X-Fleet-API-Client-ID': FLEET_API_CLIENT_ID,
    'X-Fleet-API-Key-ID': FLEET_API_KEY_ID,
}

DEFAULT_RETRIEVE_PROFILE = {
    'profiles': [
        {
            'data': {
                'full_name': {
                    'first_name': 'Водитель',
                    'last_name': 'Убер',
                    'middle_name': 'Москва',
                },
                'is_removed_by_request': False,
                'license': {'country': 'rus', 'pd_id': 'license_pd_id_'},
                'license_driver_birth_date': '1970-01-15T00:00:00.000',
                'license_experience': {'total': '2014-03-07T00:00:00.000'},
                'license_expire_date': '2029-03-07T00:00:00.000',
                'license_issue_date': '2020-03-07T00:00:00.000',
                'rule_id': 'work_rule_1',
                'created_date': '2019-01-01T00:00:00',
            },
            'park_driver_profile_id': '123_12345678',
        },
    ],
}

DEFAULT_DUPLICATES_PROFILE = {'contractor_profiles': []}  # type: ignore

DEFAULT_SPECIFICATIONS = ['taxi']

SPECIFICATIONS_MAP = {'12345678904': ['signalq']}


REPLACEMENT_MAP = {
    'А': 'A',
    'В': 'B',
    'С': 'C',
    'Е': 'E',
    'Н': 'H',
    'К': 'K',
    'М': 'M',
    'О': 'O',
    'Р': 'P',
    'Т': 'T',
    'Х': 'X',
    'У': 'Y',
}


def make_normalization(driver_license):
    result = ''
    for value in driver_license.upper():
        if value in REPLACEMENT_MAP:
            result += REPLACEMENT_MAP[value]
        elif value.isalnum():
            result += value
    return result
