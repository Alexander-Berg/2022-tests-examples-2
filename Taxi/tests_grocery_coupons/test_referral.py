import copy

# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_grocery_coupons import consts

REFERRAL_INFORMER_TEXT = 'referral_informer_text'
REFERRAL_INFORMER_IMAGE = 'referral_informer_image'
REFERRAL_PAGE_TITLE = 'referral_page_title'
REFERRAL_PAGE_TEXT = 'referral_page_text'
REFERRAL_PAGE_IMAGE = 'referral_page_image'
REFERRAL_PAGE_MORE_INFO = 'referral_page_more_info'
REFERRAL_PAGE_MORE_INFO_LINK = 'referral_page_more_info_link'
REFERRAL_PAGE_BUTTON_TEXT = 'referral_page_button_text'
REFERRAL_PAGE_SHARE_TEXT = 'referral_page_share_text'
REFERRAL_PAGE_SHARE_TITLE = 'referral_page_share_title'
REFERRAL_PAGE_COPY_TEXT = 'referral_page_copy_text'
REFERRAL_PAGE_ADDITIONAL_TEXT = 'referral_page_additional_text'

USER_LOCATION = [30.1, 53.7]

COUPONS_ERROR = 'coupons-error'
CURRENCY_ERROR = 'currency-error'
CONSUMER_ERROR = 'consumer-error'
CREATOR_ERROR = 'creator-error'
LOCATION_ERROR = 'location-error'
FIELDS_ERROR = 'not-all-fields-error'


def make_referral_response(consumer_properties, creator_properties):
    referral = copy.deepcopy(DEFAULT_REFERRAL)
    referral['consumer_properties'] = consumer_properties
    referral['creator_properties'] = creator_properties

    return referral


GROCERY_REFERRAL_PAYMENT_OPTIONS = pytest.mark.experiments3(
    name='grocery_referral_payment_options',
    consumers=['grocery-coupons/referral'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'is_signal': False,
            'title': 'Always enabled',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {
                'zone_name': 'moscow',
                'payment_options': ['card', 'coupon'],
            },
        },
    ],
    is_config=True,
)

GROCERY_REFERRAL_PROPERTIES = pytest.mark.experiments3(
    name='grocery_referral_localization',
    consumers=['grocery-coupons/referral'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'is_signal': False,
            'title': 'Always enabled',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {
                'referral_informer_text': REFERRAL_INFORMER_TEXT,
                'referral_informer_image': REFERRAL_INFORMER_IMAGE,
                'referral_page': {
                    'title': REFERRAL_PAGE_TITLE,
                    'text': REFERRAL_PAGE_TEXT,
                    'image': REFERRAL_PAGE_IMAGE,
                    'more_info': REFERRAL_PAGE_MORE_INFO,
                    'more_info_link': REFERRAL_PAGE_MORE_INFO_LINK,
                    'share_button_text': REFERRAL_PAGE_BUTTON_TEXT,
                    'promo_share_text': REFERRAL_PAGE_SHARE_TEXT,
                    'promo_share_title': REFERRAL_PAGE_SHARE_TITLE,
                    'copy_text': REFERRAL_PAGE_COPY_TEXT,
                    'additional_text': REFERRAL_PAGE_ADDITIONAL_TEXT,
                },
            },
        },
    ],
    is_config=True,
)

TEMPLATE_VALUE_FIRST = '$VALUE$ $SIGN$'
TEMPLATE_SIGN_FIRST = '$SIGN$ $VALUE$'

BASIC_TRANSLATIONS = pytest.mark.translations(
    grocery_referral={},
    grocery_localizations={
        'decimal_separator': {'ru': ',', 'en': '.', 'fr': ',', 'he': '.'},
        'price_with_sign.default': {
            'ru': TEMPLATE_VALUE_FIRST,
            'en': TEMPLATE_VALUE_FIRST,
            'fr': TEMPLATE_VALUE_FIRST,
            'he': TEMPLATE_VALUE_FIRST,
        },
        'price_with_sign.gbp': {
            'ru': TEMPLATE_SIGN_FIRST,
            'en': TEMPLATE_SIGN_FIRST,
            'fr': TEMPLATE_SIGN_FIRST,
            'he': TEMPLATE_SIGN_FIRST,
        },
    },
    currencies={
        'currency_sign.eur': {'ru': '€', 'en': '€', 'fr': '€', 'he': '€'},
        'currency_sign.gbp': {'ru': '£', 'en': '£', 'fr': '£', 'he': '£'},
        'currency_sign.ils': {'ru': '₪', 'en': '₪', 'fr': '₪', 'he': '₪'},
        'currency_sign.rub': {'ru': '₽', 'en': '₽', 'fr': '₽', 'he': '₽'},
    },
)


DEFAULT_CONSUMER_PROPERTIES = {
    'value': '100',
    'currency': 'RUB',
    'external_meta': {'min_cart_cost': '500'},
}


DEFAULT_CREATOR_PROPERTIES = {
    'value': '200',
    'currency': 'RUB',
    'percent': '20',
    'limit': '200',
    'external_meta': {},
}


DEFAULT_REFERRAL = {
    'promocode': 'grocery_referral',
    'value': 345,
    'currency': 'RUB',
    'rides_count': 5,
    'rides_left': 3,
    'descr': 'Подарите другу скидку 10%',
    'message': 'message',
    'currency_rules': {
        'code': 'RUB',
        'text': 'руб.',
        'template': '$VALUE$ $SIGN$$CURRENCY$',
        'sign': '₽',
    },
    'referral_service': 'grocery',
    'consumer_properties': DEFAULT_CONSUMER_PROPERTIES,
    'creator_properties': DEFAULT_CREATOR_PROPERTIES,
}


@GROCERY_REFERRAL_PROPERTIES
@BASIC_TRANSLATIONS
@consts.GROCERY_COUPONS_ZONE_NAME
@GROCERY_REFERRAL_PAYMENT_OPTIONS
@pytest.mark.parametrize(
    'referral_request',
    [
        ({'location': USER_LOCATION}),
        (
            {
                'country': 'rus',
                'currency': 'RUB',
                'format_currency': True,
                'payment_options': ['card', 'coupon'],
                'zone_name': 'moscow',
            }
        ),
        (
            {
                'location': USER_LOCATION,
                'country': 'isr',
                'currency': 'USD',
                'format_currency': True,
                'payment_options': ['card', 'coupon'],
                'zone_name': 'tel_aviv',
            }
        ),
    ],
)
async def test_basic(
        taxi_grocery_coupons,
        coupons,
        overlord_catalog,
        referral_request,
        grocery_depots,
):
    depot_id = 'depot-id-1'
    legacy_depot_id = '100'

    coupons.set_coupons_referral_response(body=[DEFAULT_REFERRAL])
    coupons.check_referral_request(
        headers={
            'X-Yandex-UID': consts.YANDEX_UID,
            'X-YaTaxi-User': consts.USER_INFO,
        },
    )

    overlord_catalog.add_location(
        location=USER_LOCATION,
        depot_id=depot_id,
        legacy_depot_id=legacy_depot_id,
    )
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        legacy_depot_id=legacy_depot_id,
    )

    response = await taxi_grocery_coupons.post(
        '/lavka/v1/coupons/referral',
        headers=consts.HEADERS,
        json=referral_request,
    )

    assert response.status_code == 200

    body = response.json()
    assert body['referrals'][0]['promocode'] == DEFAULT_REFERRAL['promocode']
    assert coupons.referral_times_called() == 1


@GROCERY_REFERRAL_PROPERTIES
@BASIC_TRANSLATIONS
@consts.GROCERY_COUPONS_ZONE_NAME
@GROCERY_REFERRAL_PAYMENT_OPTIONS
@pytest.mark.parametrize(
    'referral_request, coupons_response, expected_status, error_code',
    [
        ({'location': [50, 30]}, DEFAULT_REFERRAL, 406, LOCATION_ERROR),
        (
            {
                'country': 'rus',
                'currency': 'USD',
                'format_currency': True,
                'payment_options': ['card', 'coupon'],
                'zone_name': 'moscow',
            },
            DEFAULT_REFERRAL,
            406,
            CURRENCY_ERROR,
        ),
        (
            {
                'country': 'rus',
                'format_currency': True,
                'payment_options': ['card', 'coupon'],
                'zone_name': 'moscow',
            },
            DEFAULT_REFERRAL,
            400,
            FIELDS_ERROR,
        ),
        (
            {
                'country': 'rus',
                'currency': 'RUB',
                'format_currency': True,
                'payment_options': ['card', 'coupon'],
                'zone_name': 'moscow',
            },
            make_referral_response(None, DEFAULT_CREATOR_PROPERTIES),
            406,
            CONSUMER_ERROR,
        ),
        (
            {
                'country': 'rus',
                'currency': 'RUB',
                'format_currency': True,
                'payment_options': ['card', 'coupon'],
                'zone_name': 'moscow',
            },
            make_referral_response(DEFAULT_CONSUMER_PROPERTIES, None),
            406,
            CREATOR_ERROR,
        ),
        (
            {
                'country': 'rus',
                'currency': 'RUB',
                'format_currency': True,
                'payment_options': ['card', 'coupon'],
                'zone_name': 'moscow',
            },
            make_referral_response(None, None),
            406,
            CONSUMER_ERROR,
        ),
    ],
)
@pytest.mark.parametrize('coupons_code', [200, 400, 406, 429, 500])
async def test_errors(
        taxi_grocery_coupons,
        taxi_grocery_coupons_monitor,
        overlord_catalog,
        referral_request,
        expected_status,
        error_code,
        coupons,
        coupons_code,
        coupons_response,
        grocery_depots,
):
    if coupons_code == 200:
        depot_id = 'depot-id-1'
        legacy_depot_id = '100'

        coupons.set_coupons_referral_response(body=[coupons_response])

        overlord_catalog.add_location(
            location=USER_LOCATION,
            depot_id=depot_id,
            legacy_depot_id=legacy_depot_id,
        )
        grocery_depots.add_depot(
            depot_test_id=int(legacy_depot_id),
            depot_id=depot_id,
            legacy_depot_id=legacy_depot_id,
        )
    else:
        error_code = (
            str(coupons_code) if coupons_code != 500 else 'coupons-error'
        )
        coupons.set_coupons_referral_response(status_code=str(coupons_code))
        referral_request = {
            'country': 'rus',
            'currency': 'RUB',
            'format_currency': True,
            'payment_options': ['card', 'coupon'],
            'zone_name': 'moscow',
        }

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_coupons_monitor,
            sensor='referral_errors',
            labels={'error': error_code, 'application': consts.APP_NAME},
    ) as collector:
        response = await taxi_grocery_coupons.post(
            '/lavka/v1/coupons/referral',
            headers=consts.HEADERS,
            json=referral_request,
        )

    if coupons_code == 200:
        assert response.status_code == expected_status
    else:
        assert response.status_code == coupons_code

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    if coupons_code != 500:
        assert len(response.json()['errors']) == 1
        assert response.json()['errors'][0]['code'] == error_code


TRANSLATION_ARGS = (
    '%(referral_value)s, %(referral_min_cart_cost)s, '
    '%(reward_value)s %(reward_limit)s, %(reward_min_cart_cost)s'
)


@GROCERY_REFERRAL_PROPERTIES
@BASIC_TRANSLATIONS
@pytest.mark.translations(
    grocery_referral={
        REFERRAL_INFORMER_TEXT: {
            'ru': f'referral-informer-text-ru, {TRANSLATION_ARGS}',
            'en': f'referral-informer-text-en, {TRANSLATION_ARGS}',
        },
        REFERRAL_PAGE_TITLE: {
            'ru': f'referral-page-title-ru, {TRANSLATION_ARGS}',
            'en': f'referral-page-title-en, {TRANSLATION_ARGS}',
        },
        REFERRAL_PAGE_TEXT: {
            'ru': f'referral-page-text-ru, {TRANSLATION_ARGS}',
            'en': f'referral-page-text-en, {TRANSLATION_ARGS}',
        },
        REFERRAL_PAGE_MORE_INFO: {
            'ru': f'referral-page-more-info-ru, {TRANSLATION_ARGS}',
            'en': f'referral-page-more-info-en, {TRANSLATION_ARGS}',
        },
        REFERRAL_PAGE_BUTTON_TEXT: {
            'ru': f'referral-button-text-ru, {TRANSLATION_ARGS}',
            'en': f'referral-button-text-en, {TRANSLATION_ARGS}',
        },
        REFERRAL_PAGE_SHARE_TEXT: {
            'ru': f'referral-page-share-text-ru, {TRANSLATION_ARGS}',
            'en': f'referral-page-share-text-en, {TRANSLATION_ARGS}',
        },
        REFERRAL_PAGE_SHARE_TITLE: {
            'ru': f'referral-page-share-title-ru, {TRANSLATION_ARGS}',
            'en': f'referral-page-share-title-en, {TRANSLATION_ARGS}',
        },
        REFERRAL_PAGE_COPY_TEXT: {
            'ru': f'referral-page-copy-text-ru, {TRANSLATION_ARGS}',
            'en': f'referral-page-copy-text-en, {TRANSLATION_ARGS}',
        },
        REFERRAL_PAGE_ADDITIONAL_TEXT: {
            'ru': f'referral-page-additional-text-ru, {TRANSLATION_ARGS}',
            'en': f'referral-page-additional-text-en, {TRANSLATION_ARGS}',
        },
    },
)
@pytest.mark.parametrize('locale', ['ru', 'en'])
async def test_referral_info(taxi_grocery_coupons, coupons, locale):
    coupons.set_coupons_referral_response(body=[DEFAULT_REFERRAL])

    translated_args = '100 ₽, 500 ₽, 20% 200 ₽, 0 ₽'
    referral_informer_texts = {
        REFERRAL_INFORMER_TEXT: {
            'ru': f'referral-informer-text-ru, {translated_args}',
            'en': f'referral-informer-text-en, {translated_args}',
        },
        REFERRAL_PAGE_TITLE: {
            'ru': f'referral-page-title-ru, {translated_args}',
            'en': f'referral-page-title-en, {translated_args}',
        },
        REFERRAL_PAGE_TEXT: {
            'ru': f'referral-page-text-ru, {translated_args}',
            'en': f'referral-page-text-en, {translated_args}',
        },
        REFERRAL_PAGE_MORE_INFO: {
            'ru': f'referral-page-more-info-ru, {translated_args}',
            'en': f'referral-page-more-info-en, {translated_args}',
        },
        REFERRAL_PAGE_BUTTON_TEXT: {
            'ru': f'referral-button-text-ru, {translated_args}',
            'en': f'referral-button-text-en, {translated_args}',
        },
        REFERRAL_PAGE_SHARE_TEXT: {
            'ru': f'referral-page-share-text-ru, {translated_args}',
            'en': f'referral-page-share-text-en, {translated_args}',
        },
        REFERRAL_PAGE_SHARE_TITLE: {
            'ru': f'referral-page-share-title-ru, {translated_args}',
            'en': f'referral-page-share-title-en, {translated_args}',
        },
        REFERRAL_PAGE_COPY_TEXT: {
            'ru': f'referral-page-copy-text-ru, {translated_args}',
            'en': f'referral-page-copy-text-en, {translated_args}',
        },
        REFERRAL_PAGE_ADDITIONAL_TEXT: {
            'ru': f'referral-page-additional-text-ru, {translated_args}',
            'en': f'referral-page-additional-text-en, {translated_args}',
        },
    }

    response = await taxi_grocery_coupons.post(
        '/lavka/v1/coupons/referral',
        headers={**consts.HEADERS, 'X-Request-Language': locale},
        json={
            'country': 'rus',
            'currency': 'RUB',
            'format_currency': True,
            'payment_options': ['card', 'coupon'],
            'zone_name': 'moscow',
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body['referrals'][0]['referral_info'] == {
        'referral_informer': {
            'text': referral_informer_texts[REFERRAL_INFORMER_TEXT][locale],
            'image': REFERRAL_INFORMER_IMAGE,
        },
        'referral_page': {
            'title': referral_informer_texts[REFERRAL_PAGE_TITLE][locale],
            'text': referral_informer_texts[REFERRAL_PAGE_TEXT][locale],
            'image': REFERRAL_PAGE_IMAGE,
            'more_info': referral_informer_texts[REFERRAL_PAGE_MORE_INFO][
                locale
            ],
            'more_info_link': REFERRAL_PAGE_MORE_INFO_LINK,
            'share_button_text': referral_informer_texts[
                REFERRAL_PAGE_BUTTON_TEXT
            ][locale],
            'promo_share_text': referral_informer_texts[
                REFERRAL_PAGE_SHARE_TEXT
            ][locale],
            'promo_share_title': referral_informer_texts[
                REFERRAL_PAGE_SHARE_TITLE
            ][locale],
            'copy_text': referral_informer_texts[REFERRAL_PAGE_COPY_TEXT][
                locale
            ],
            'additional_text': referral_informer_texts[
                REFERRAL_PAGE_ADDITIONAL_TEXT
            ][locale],
        },
    }


@BASIC_TRANSLATIONS
@GROCERY_REFERRAL_PROPERTIES
async def test_several_referrals(taxi_grocery_coupons, coupons):
    missing_properties_referral = copy.deepcopy(DEFAULT_REFERRAL)
    missing_properties_referral['promocode'] = 'missing_properties'
    missing_properties_referral['consumer_properties'] = None

    wrong_currency_referral = copy.deepcopy(DEFAULT_REFERRAL)
    wrong_currency_referral['promocode'] = 'wrong_currency'
    wrong_currency_referral['currency'] = 'GBP'

    coupons.set_coupons_referral_response(
        body=[
            DEFAULT_REFERRAL,
            missing_properties_referral,
            wrong_currency_referral,
        ],
    )

    response = await taxi_grocery_coupons.post(
        '/lavka/v1/coupons/referral',
        headers={**consts.HEADERS},
        json={
            'country': 'rus',
            'currency': 'RUB',
            'format_currency': True,
            'payment_options': ['card', 'coupon'],
            'zone_name': 'moscow',
        },
    )

    assert response.status_code == 200

    referrals = response.json()['referrals']

    assert len(referrals) == 1
    assert referrals[0]['promocode'] == DEFAULT_REFERRAL['promocode']
