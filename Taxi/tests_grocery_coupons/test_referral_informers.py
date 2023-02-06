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

REFERRAL_REWARD_INFORMER_TEXT = 'referral_reward_informer_text'
REFERRAL_REWARD_INFORMER_IMAGE = 'referral_reward_informer_image'
REFERRAL_REWARD_PAGE_TITLE = 'referral_reward_page_title'
REFERRAL_REWARD_PAGE_TEXT = 'referral_reward_page_text'
REFERRAL_REWARD_PAGE_IMAGE = 'referral_reward_page_image'
REFERRAL_REWARD_PAGE_BUTTON_TEXT = 'referral_reward_page_button_text'

REFERRAL_PROMOCODE = 'grocery_referral'

USER_LOCATION = [30.1, 53.7]

COUPONS_ERROR = 'coupons-error'
CONSUMER_ERROR = 'consumer-error'
CREATOR_ERROR = 'creator-error'

REFERRAL_NAME = 'referral-informer'
REFERRAL_REWARD_NAME = 'referral-reward-informer'


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
                'referral_reward_informer_text': REFERRAL_REWARD_INFORMER_TEXT,
                'referral_reward_informer_image': (
                    REFERRAL_REWARD_INFORMER_IMAGE
                ),
                'referral_reward_page': {
                    'title': REFERRAL_REWARD_PAGE_TITLE,
                    'text': REFERRAL_REWARD_PAGE_TEXT,
                    'image': REFERRAL_REWARD_PAGE_IMAGE,
                    'button_text': REFERRAL_REWARD_PAGE_BUTTON_TEXT,
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
    'promocode': REFERRAL_PROMOCODE,
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


TRANSLATION_ARGS = (
    '%(referral_value)s, %(referral_min_cart_cost)s, '
    '%(reward_value)s %(reward_limit)s, %(reward_min_cart_cost)s'
)

TRANSLATION_REWARD_ARGS = (
    '%(reward_value)s, %(reward_limit)s, %(reward_min_cart_cost)s'
)


@GROCERY_REFERRAL_PROPERTIES
@BASIC_TRANSLATIONS
@consts.GROCERY_COUPONS_ZONE_NAME
@GROCERY_REFERRAL_PAYMENT_OPTIONS
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
        REFERRAL_REWARD_INFORMER_TEXT: {
            'ru': (
                f'referral-reward-informer-text-ru, {TRANSLATION_REWARD_ARGS}'
            ),
            'en': (
                f'referral-reward-informer-text-en, {TRANSLATION_REWARD_ARGS}'
            ),
        },
        REFERRAL_REWARD_PAGE_TEXT: {
            'ru': f'referral-reward-page-text-ru, {TRANSLATION_REWARD_ARGS}',
            'en': f'referral-reward-page-text-en, {TRANSLATION_REWARD_ARGS}',
        },
        REFERRAL_REWARD_PAGE_TITLE: {
            'ru': f'referral-reward-page-title-ru, {TRANSLATION_REWARD_ARGS}',
            'en': f'referral-reward-page-title-en, {TRANSLATION_REWARD_ARGS}',
        },
        REFERRAL_REWARD_PAGE_BUTTON_TEXT: {
            'ru': f'referral-page-button-text-ru, {TRANSLATION_REWARD_ARGS}',
            'en': f'referral-page-button-text-en, {TRANSLATION_REWARD_ARGS}',
        },
    },
)
@pytest.mark.parametrize('locale', ['ru', 'en'])
async def test_basic(
        taxi_grocery_coupons,
        coupons,
        overlord_catalog,
        grocery_depots,
        locale,
):
    depot_id = 'depot-id-1'
    legacy_depot_id = '100'

    translated_args = '100 ₽, 500 ₽, 20% 200 ₽, 0 ₽'
    translated_reward_args = '100 ₽, 500 ₽, 50 ₽'
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
        REFERRAL_REWARD_INFORMER_TEXT: {
            'ru': (
                f'referral-reward-informer-text-ru, {translated_reward_args}'
            ),
            'en': (
                f'referral-reward-informer-text-en, {translated_reward_args}'
            ),
        },
        REFERRAL_REWARD_PAGE_TEXT: {
            'ru': f'referral-reward-page-text-ru, {translated_reward_args}',
            'en': f'referral-reward-page-text-en, {translated_reward_args}',
        },
        REFERRAL_REWARD_PAGE_TITLE: {
            'ru': f'referral-reward-page-title-ru, {translated_reward_args}',
            'en': f'referral-reward-page-title-en, {translated_reward_args}',
        },
        REFERRAL_REWARD_PAGE_BUTTON_TEXT: {
            'ru': f'referral-page-button-text-ru, {translated_reward_args}',
            'en': f'referral-page-button-text-en, {translated_reward_args}',
        },
    }

    coupons.set_coupons_referral_response(body=[DEFAULT_REFERRAL])
    coupons.check_referral_request(
        headers={
            'X-Yandex-UID': consts.YANDEX_UID,
            'X-YaTaxi-User': consts.USER_INFO,
        },
    )

    coupons.set_coupons_list_response(
        body={
            'coupons': [
                {
                    'code': 'promocode_with_tag',
                    'status': 'valid',
                    'series_meta': {
                        'title': 'title_tanker_key_tag',
                        'subtitle': 'subtitle_tanker_key_tag',
                        'tag': 'some_tag',
                        'min_cart_cost': '50',
                    },
                    'value': 100.0,
                    'limit': 500.0,
                    'series_id': 'promocode',
                    'expire_at': '2020-05-25T17:43:45+00:00',
                    'currency_code': 'RUB',
                    'reason_type': 'referral_reward',
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                },
            ],
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
        '/internal/v1/coupons/referral/informers',
        headers={**consts.HEADERS, 'X-Request-Language': locale},
        json={'location': USER_LOCATION},
    )

    assert response.status_code == 200

    body = response.json()
    assert coupons.referral_times_called() == 1
    assert body['informers'][0] == {
        'text': referral_informer_texts[REFERRAL_INFORMER_TEXT][locale],
        'picture': REFERRAL_INFORMER_IMAGE,
        'name': REFERRAL_NAME,
        'show_in_root': True,
        'modal': {
            'title': referral_informer_texts[REFERRAL_PAGE_TITLE][locale],
            'text': referral_informer_texts[REFERRAL_PAGE_TEXT][locale],
            'full_screen': True,
            'picture': REFERRAL_PAGE_IMAGE,
            'buttons': [
                {
                    'variant': 'action',
                    'text': REFERRAL_PROMOCODE,
                    'action': 'copy',
                },
                {
                    'variant': 'action',
                    'text': referral_informer_texts[REFERRAL_PAGE_BUTTON_TEXT][
                        locale
                    ],
                    'action': 'share',
                },
            ],
            'extra_data': {
                'text': referral_informer_texts[REFERRAL_PAGE_MORE_INFO][
                    locale
                ],
                'link': REFERRAL_PAGE_MORE_INFO_LINK,
                'additional_text': referral_informer_texts[
                    REFERRAL_PAGE_ADDITIONAL_TEXT
                ][locale],
            },
        },
    }

    # reward informer
    assert body['informers'][1] == {
        'text': referral_informer_texts[REFERRAL_REWARD_INFORMER_TEXT][locale],
        'show_in_root': True,
        'picture': REFERRAL_REWARD_INFORMER_IMAGE,
        'name': REFERRAL_REWARD_NAME,
        'modal': {
            'text': referral_informer_texts[REFERRAL_REWARD_PAGE_TEXT][locale],
            'title': referral_informer_texts[REFERRAL_REWARD_PAGE_TITLE][
                locale
            ],
            'picture': REFERRAL_REWARD_PAGE_IMAGE,
            'buttons': [
                {
                    'text': referral_informer_texts[
                        REFERRAL_REWARD_PAGE_BUTTON_TEXT
                    ][locale],
                    'variant': 'default',
                },
            ],
        },
    }


@GROCERY_REFERRAL_PROPERTIES
@BASIC_TRANSLATIONS
@consts.GROCERY_COUPONS_ZONE_NAME
@GROCERY_REFERRAL_PAYMENT_OPTIONS
@pytest.mark.parametrize(
    'coupons_response, expected_status, error_code',
    [
        (
            make_referral_response(None, DEFAULT_CREATOR_PROPERTIES),
            200,
            CONSUMER_ERROR,
        ),
        (
            make_referral_response(DEFAULT_CONSUMER_PROPERTIES, None),
            200,
            CREATOR_ERROR,
        ),
        (make_referral_response(None, None), 200, CONSUMER_ERROR),
    ],
)
@pytest.mark.parametrize('coupons_code', [200, 400, 406, 429, 500])
async def test_errors(
        taxi_grocery_coupons,
        taxi_grocery_coupons_monitor,
        overlord_catalog,
        expected_status,
        error_code,
        coupons,
        coupons_code,
        coupons_response,
        grocery_depots,
):
    depot_id = 'depot-id-1'
    legacy_depot_id = '100'

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

    coupons.set_coupons_list_response(body={'coupons': []})

    if coupons_code == 200:
        coupons.set_coupons_referral_response(body=[coupons_response])
    else:
        error_code = (
            str(coupons_code) if coupons_code != 500 else COUPONS_ERROR
        )
        coupons.set_coupons_referral_response(status_code=str(coupons_code))

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_coupons_monitor,
            sensor='referral_errors',
            labels={'error': error_code, 'application': consts.APP_NAME},
    ) as collector:
        response = await taxi_grocery_coupons.post(
            '/internal/v1/coupons/referral/informers',
            headers=consts.HEADERS,
            json={'location': USER_LOCATION},
        )

    assert response.status_code == expected_status

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
