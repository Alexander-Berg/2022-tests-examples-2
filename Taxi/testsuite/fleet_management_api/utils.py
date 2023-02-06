import typing

ACCEPT_LANGUAGE_HEADERS = {'Accept-Language': 'ru_Ru'}
X_REAL_IP_HEADERS = {'X-Real-IP': '1.2.3.4'}


def format_error(message, code=None):
    result = {'message': message}
    if code is not None:
        result['code'] = str(code)
    return result


UNKNOWN_ERROR = format_error('unknown error')
INTERNAL_ERROR = format_error('internal server error', 'internal_error')
ENDPOINT_DISABLED_ERROR = format_error(
    'The endpoint has been disabled. If you have any questions, you may '
    'contact us on: api-taxi@yandex-team.ru.',
)
UNAUTHORIZED_ERROR = format_error('header X-Ya-User-Ticket must not be empty')
TOO_MANY_REQUESTS_ERROR = format_error(
    'Too many requests have been sent.', 'too_many_requests',
)


def check_headers(actual, expected):
    for header, value in expected.items():
        assert actual.get(header) == value, actual


def format_parks_error(text, code=None):
    error = {'text': text}
    if code is not None:
        error['code'] = str(code)

    return {'error': error}


def check_categories_filter(json_object, categories=None):
    json_categories_filter = json_object.pop('categories_filter')
    json_categories_filter.sort()
    if categories is not None:
        categories.sort()
        assert json_categories_filter == categories, json_categories_filter
    else:
        assert json_categories_filter == [
            'business',
            'cargo',
            'comfort',
            'comfort_plus',
            'econom',
            'express',
            'maybach',
            'minivan',
            'personal_driver',
            'pool',
            'premium_suv',
            'premium_van',
            'promo',
            'standart',
            'start',
            'suv',
            'ultimate',
            'vip',
            'wagon',
        ], json_categories_filter


def check_query_park_car_categories_filter(json_object, categories=None):
    json_park = json_object['query']['park']
    check_categories_filter(json_park['car'], categories)
    if not json_park['car']:
        json_park.pop('car')


ACCOUNT_FIELDS = sorted(
    [
        'balance',
        'balance_limit',
        'currency',
        'id',
        'last_transaction_date',
        'type',
    ],
)

CAR_FIELDS = sorted(
    [
        'amenities',
        'badge_for_alternative_transport_expiration_date',
        'body_number',
        'booster_count',
        'brand',
        'callsign',
        'car_authorization_expiration_date',
        'car_insurance_expiration_date',
        'cargo_hold_dimensions',
        'cargo_loaders',
        'carrier_permit_owner_id',
        'carrying_capacity',
        'category',
        'chairs',
        'charge_confirmed',
        'color',
        'confirmed_boosters',
        'confirmed_chairs',
        'created_date',
        'description',
        'euro_car_segment',
        'id',
        'insurance_for_goods_and_passengers_expiration_date',
        'is_readonly',
        'kasko_date',
        'license_type',
        'lightbox_confirmed',
        'mileage',
        'model',
        'modified_date',
        'normalized_number',
        'number',
        'onlycard',
        'osago_date',
        'osago_number',
        'park_id',
        'permit_doc',
        'permit_num',
        'permit_series',
        'registration_cert',
        'registration_cert_verified',
        'rental',
        'rental_status',
        'leasing_company',
        'leasing_start_date',
        'leasing_term',
        'leasing_monthly_payment',
        'leasing_interest_rate',
        'fuel_type',
        'rug_confirmed',
        'service_check_expiration_date',
        'service_date',
        'status',
        'sticker_confirmed',
        'tags',
        'tariffs',
        'transmission',
        'vin',
        'year',
    ],
)

DRIVER_PROFILE_FIELDS = sorted(
    [
        'address',
        'background_criminal_record_issue_date',
        'balance_deny_onlycard',
        'car_id',
        'check_message',
        'created_date',
        'comment',
        'courier_type',
        'deaf',
        'device_model',
        'driver_license',
        'email',
        'fire_date',
        'first_name',
        'sex',
        'platform_uid',
        'gdpr_accept_date',
        'hire_date',
        'hiring_details',
        'license_experience',
        'hiring_source',
        'id',
        'imei',
        'is_readonly',
        'is_removed_by_request',
        'last_name',
        'license',
        'locale',
        'middle_name',
        'modified_date',
        'network_operator',
        'park_id',
        'payment_service_id',
        'permit_number',
        'phones',
        'professional_certificate_expiration_date',
        'providers',
        'road_penalties_record_issue_date',
        'tags',
        'taximeter_version',
        'work_rule_id',
        'affiliation',
        'work_status',
    ],
)

PARK_FIELDS = sorted(['city', 'id', 'name'])
CURRENT_STATUS_FIELDS = sorted(['status', 'status_updated_at'])
DEPTRANS_FIELDS = sorted(['id', 'status', 'updated_at'])
RATING_FIELDS = sorted(['average_rating'])
DRIVER_CATEGORIES_FIELDS = sorted(['disabled_by_driver'])
DRIVER_METRICS_FIELDS = sorted(['activity'])
TAXIMETER_DISABLE_STATUS_FIELDS = sorted(['disable_message', 'disabled'])

EXTERNAL_ACCOUNT_FIELDS = ACCOUNT_FIELDS
EXTERNAL_CAR_FIELDS = sorted(
    [
        'amenities',
        'brand',
        'callsign',
        'category',
        'color',
        'id',
        'license_type',
        'model',
        'normalized_number',
        'number',
        'registration_cert',
        'status',
        'rental',
        'rental_status',
        'leasing_company',
        'leasing_start_date',
        'leasing_term',
        'leasing_monthly_payment',
        'leasing_interest_rate',
        'fuel_type',
        'vin',
        'year',
    ],
)

EXTERNAL_DRIVER_PROFILE_FIELDS = sorted(
    [
        'check_message',
        'comment',
        'created_date',
        'driver_license',
        'fire_date',
        'hire_date',
        'first_name',
        'id',
        'is_readonly',
        'is_removed_by_request',
        'last_name',
        'middle_name',
        'modified_date',
        'park_id',
        'permit_number',
        'phones',
        'work_rule_id',
        'work_status',
    ],
)

EXTERNAL_CURRENT_STATUS_FIELDS = CURRENT_STATUS_FIELDS


EXTERNAL_PARK_FIELDS = PARK_FIELDS
EXTERNAL_RATING_FIELDS: typing.List[str] = []
EXTERNAL_DRIVER_CATEGORIES_FIELDS: typing.List[str] = []
EXTERNAL_DRIVER_METRICS_FIELDS: typing.List[str] = []
EXTERNAL_TAXIMETER_DISABLE_STATUS_FIELDS = TAXIMETER_DISABLE_STATUS_FIELDS
