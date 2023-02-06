import itertools
import random
import string
import uuid

import pytest

from tests_grocery_coupons import consts

CART_ID = '00000000-0000-0000-0000-d98013100500'

INSERT_ERROR_LOG_SQL = """
INSERT INTO coupons.errors_log
(
    created,
    coupon,
    error_code,
    cart_id,
    yandex_uid,
    personal_phone_id,
    coupon_type
)
VALUES
(
    CURRENT_TIMESTAMP,
    %s,
    %s,
    %s,
    'yandex_uid',
    'personal_phone_id',
    'support'
)
ON CONFLICT (coupon, error_code, cart_id) DO NOTHING;
"""


def _insert_error_log(pgsql, coupon, error_code, cart_id):
    cursor = pgsql['grocery_coupons'].cursor()
    cursor.execute(INSERT_ERROR_LOG_SQL, [coupon, error_code, cart_id])


def _get_random_string(length=5, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(length))


def _generate_errors(error_count, cart_id=None):
    coupon = 'lavkatest' + _get_random_string(length=5)
    error_codes = random.sample(consts.ERROR_CODES, error_count)
    if cart_id is None:
        cart_id = str(uuid.uuid4())
    return [(coupon, error_code, cart_id) for error_code in error_codes]


def _translate(translations, key, locale):
    key = 'coupons.{}'.format(key.lower())
    for translation in translations:
        if translation['_id'] == key:
            for value in translation['values']:
                if (
                        'locale' in value['conditions']
                        and value['conditions']['locale']['language'] == locale
                ):
                    return value['value']
            return translation['values'][-1]['value']
    return key


# def _sorted(response):
#    return {'errors': sorted(response['errors'], key=lambda d: d['coupon'])}


@pytest.mark.parametrize('main_cart_coupons', [0, 1, 3])
@pytest.mark.parametrize(
    'main_cart_errors_per_coupon, locale', [(1, 'ru'), (5, 'en')],
)
@pytest.mark.parametrize('errors_per_coupon', [[], [3], [5, 3, 6, 1, 1, 5]])
async def test_basic(
        pgsql,
        taxi_grocery_coupons,
        load_json,
        main_cart_coupons,
        main_cart_errors_per_coupon,
        locale,
        errors_per_coupon,
):
    main_cart_errors = []
    for _ in range(main_cart_coupons):
        main_cart_errors.extend(
            _generate_errors(main_cart_errors_per_coupon, cart_id=CART_ID),
        )

    other_errors = []
    for error_count in errors_per_coupon:
        other_errors.extend(_generate_errors(error_count))

    for error_log in itertools.chain(main_cart_errors, other_errors):
        _insert_error_log(pgsql, *error_log)

    response = await taxi_grocery_coupons.post(
        '/admin/v1/coupons/list-errors',
        headers={'Accept-Language': locale},
        json={'cart_id': CART_ID},
    )

    assert response.status_code == 200

    translations = load_json('localizations/grocery_cart.json')
    expected_response = {
        'errors': [
            {
                'coupon': coupon,
                'error': _translate(translations, error, locale),
            }
            for coupon, error, cart_id in main_cart_errors
        ],
    }

    assert response.json() == expected_response
