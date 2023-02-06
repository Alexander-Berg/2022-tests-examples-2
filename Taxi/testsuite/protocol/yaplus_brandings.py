from typing import Dict

# config names
MENU_ICON = 'YAPLUS_MENU_ICON_BASE_TAG_BY_PLUS_VERSION'
PROFILE_BADGE = 'YAPLUS_PROFILE_BADGE_BY_PLUS_VERSION'
PAYMENT_DECORATION = 'YAPLUS_PAYMENT_DECORATION_BY_PLUS_VERSION'
TARIFF_CARD_BADGE = 'YAPLUS_TARIFF_CARD_BADGE_BY_PLUS_VERSION'


MENU_ICON_BASE_TAG_CONFIG = {
    '__default__': 'plus_profile_icon',
    'discount': 'plus_discount_profile_icon',
    'cashback': 'plus_cashback_profile_icon',
}

PROFILE_BADGE_CONFIG = {
    'discount': {
        'title_key': 'branding.profile_badge_title',
        'subtitle_key': 'branding.profile_badge_subtitle',
        'image_tag': 'plus_card',
    },
    'cashback': {
        'title_key': 'branding.profile_badge_title',
        'subtitle_key': 'branding.cashback.profile_badge_subtitle',
        'image_tag': 'plus_card_cashback',
    },
}

PAYMENT_DECORATION_CONFIG = {
    'discount': {
        'summary_payment_subtitle_key': (
            'yandex_plus_discount_summary_card_promo'
        ),
    },
    'cashback': {
        'summary_payment_subtitle_key': (
            'yandex_plus_cashback_summary_card_promo'
        ),
    },
}

TARIFF_CARD_BADGE_CONFIG = {
    'discount': {
        'title_key': 'yandex_plus_discount_tariff_card_title_default',
        'subtitle_key': 'yandex_plus_discount_tariff_card_subtitle_default',
        'image_tag': 'plus_card',
    },
    'cashback': {
        'title_key': 'branding.cashback.tariff_card_title',
        'subtitle_key': 'branding.cashback.tariff_card_subtitle',
        'image_tag': 'plus_card_cashback',
    },
}


def make_configs(
        menu_icon: dict = None,
        profile_badge: dict = None,
        payment_decoration: dict = None,
        tariff_card_badge: dict = None,
) -> Dict[str, dict]:
    """Returns configs for Yandex.Plus brandings with overridable defaults."""
    config: Dict[str, dict] = {
        MENU_ICON: MENU_ICON_BASE_TAG_CONFIG,
        PROFILE_BADGE: PROFILE_BADGE_CONFIG,
        PAYMENT_DECORATION: PAYMENT_DECORATION_CONFIG,
        TARIFF_CARD_BADGE: TARIFF_CARD_BADGE_CONFIG,
    }
    if menu_icon is not None:
        config[MENU_ICON] = menu_icon
    if profile_badge is not None:
        config[PROFILE_BADGE] = profile_badge
    if payment_decoration is not None:
        config[PAYMENT_DECORATION] = payment_decoration
    if tariff_card_badge is not None:
        config[TARIFF_CARD_BADGE] = tariff_card_badge
    return config


DEFAULT_CONFIG = make_configs()
