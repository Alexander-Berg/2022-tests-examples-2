from typing import Dict
from typing import List

import pytest

from protocol import yaplus_brandings

TEST_USER_ID = '536b24fa2816451b855d9a3e640215c3'  # has Plus by default
DEFAULT_LOCALE = 'ru'
SIZE_HINT = 9999


CLIENT_MESSAGES = {
    'yandex_plus_discount_tariff_card_title_default': {'ru': 'Плюс'},
    'yandex_plus_discount_tariff_card_subtitle_default': {
        'ru': 'Постоянная скидка',
    },
    'branding.cashback.tariff_card_title': {'ru': 'Плюс'},
    'branding.cashback.tariff_card_subtitle': {'ru': 'Кэшбек'},
    'yandex_plus_discount_summary_card_promo': {'ru': 'скидка от Плюса'},
    'yandex_plus_cashback_summary_card_promo': {'ru': 'кэшбек от Плюса'},
}


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.config(**yaplus_brandings.DEFAULT_CONFIG)
# NOTE: no YANDEX_PLUS_DISCOUNT config
def test_yaplus_no_modifiers_no_branding(taxi_protocol):
    response = _make_zoneinfo_request(taxi_protocol, user_id=TEST_USER_ID)
    brandings = _parse_brandings(response)
    _assert_no_brandings(brandings)


@pytest.mark.config(YANDEX_PLUS_DISCOUNT={'rus': {'comfortplus': 0.1}})
class TestYaPlus:
    # NOTE: no translations defined for test!
    @pytest.mark.config(**yaplus_brandings.DEFAULT_CONFIG)
    @pytest.mark.parametrize(
        'has_cashback_plus',
        [False, True],
        ids=['discount offer', 'cashback offer'],
    )
    def test_no_translations_empty_strings(
            self, taxi_protocol, db, mockserver, has_cashback_plus: bool,
    ):
        _update_user(db, TEST_USER_ID, True, has_cashback_plus)

        response = _make_zoneinfo_request(taxi_protocol, user_id=TEST_USER_ID)
        brandings = _parse_brandings(response)
        branding = _get_branding(brandings, 'comfortplus', 'ya_plus')

        expected_branding = _make_yaplus_branding(
            mockserver,
            has_cashback_plus,
            empty_strings=True,
            payment_subtitile=False,
        )
        assert branding == expected_branding

    @pytest.mark.config(
        **yaplus_brandings.make_configs(
            tariff_card_badge={'bad_version_name': {}},
        ),
    )
    def test_bad_config_no_branding(self, taxi_protocol):
        response = _make_zoneinfo_request(taxi_protocol, user_id=TEST_USER_ID)
        brandings = _parse_brandings(response)

        _assert_no_brandings(brandings)

    @pytest.mark.translations(client_messages=CLIENT_MESSAGES)
    @pytest.mark.config(**yaplus_brandings.DEFAULT_CONFIG)
    @pytest.mark.parametrize(
        'has_ya_plus, has_cashback_plus',
        [(False, False), (True, False), (True, True), (False, True)],
        ids=[
            'no branding',
            'discount branding',
            'cashback branding',
            'no branding but user accepted cashback offer',
        ],
    )
    def test_offers(
            self,
            taxi_protocol,
            db,
            mockserver,
            has_ya_plus: bool,
            has_cashback_plus: bool,
    ):
        _update_user(db, TEST_USER_ID, has_ya_plus, has_cashback_plus)

        response = _make_zoneinfo_request(taxi_protocol, user_id=TEST_USER_ID)
        brandings = _parse_brandings(response)

        # FIXME: because of field 'could_buy_plus' we always return brandings
        # if not has_ya_plus:
        #     _assert_no_brandings(brandings)
        #     return

        branding = _get_branding(brandings, 'comfortplus', 'ya_plus')
        if not has_ya_plus and has_cashback_plus:
            # special case for default behavior. see FIXME before
            expected_branding = _make_yaplus_branding(mockserver, False)
        else:
            expected_branding = _make_yaplus_branding(
                mockserver, has_cashback_plus,
            )
        assert branding == expected_branding

    @pytest.mark.translations(client_messages=CLIENT_MESSAGES)
    @pytest.mark.config(**yaplus_brandings.DEFAULT_CONFIG)
    @pytest.mark.experiments3(
        filename='exp3_turn_off_plus_discount_brandings_visibility.json',
    )
    @pytest.mark.parametrize(
        'has_ya_plus, has_cashback_plus, is_expected_branding',
        [
            (False, False, False),
            (True, False, False),
            (True, True, True),
            (False, True, False),
        ],
        ids=[
            'no branding',
            'discount branding disabled by exp',
            'cashback branding',
            'no branding but user accepted cashback offer',
        ],
    )
    def test_offers_with_experiment_disabile_discount_brandings(
            self,
            taxi_protocol,
            db,
            mockserver,
            has_ya_plus: bool,
            has_cashback_plus: bool,
            is_expected_branding: bool,
    ):
        _update_user(db, TEST_USER_ID, has_ya_plus, has_cashback_plus)

        response = _make_zoneinfo_request(taxi_protocol, user_id=TEST_USER_ID)
        brandings = _parse_brandings(response)

        if not is_expected_branding:
            _assert_no_brandings(brandings)
            return

        branding = _get_branding(brandings, 'comfortplus', 'ya_plus')

        expected_branding = _make_yaplus_branding(
            mockserver, has_cashback_plus,
        )

        assert branding == expected_branding

    @pytest.mark.translations(client_messages=CLIENT_MESSAGES)
    @pytest.mark.config(**yaplus_brandings.DEFAULT_CONFIG)
    @pytest.mark.config(
        CASHBACK_FOR_PLUS_COUNTRIES={'check_enabled': True, 'countries': []},
    )
    @pytest.mark.parametrize(
        'has_ya_plus, has_cashback_plus',
        [(False, False), (True, False), (True, True), (False, True)],
        ids=[
            'no branding',
            'discount branding',
            'still discount branding',
            'no branding but user accepted cashback offer',
        ],
    )
    def test_offers_cashback_disabled_for_country(
            self,
            taxi_protocol,
            db,
            mockserver,
            taxi_config,
            has_ya_plus: bool,
            has_cashback_plus: bool,
    ):
        _update_user(db, TEST_USER_ID, has_ya_plus, has_cashback_plus)

        response = _make_zoneinfo_request(taxi_protocol, user_id=TEST_USER_ID)
        brandings = _parse_brandings(response)

        # FIXME: because of field 'could_buy_plus' we always return brandings
        # if not has_ya_plus:
        #     _assert_no_brandings(brandings)
        #     return

        branding = _get_branding(brandings, 'comfortplus', 'ya_plus')
        if not has_ya_plus and has_cashback_plus:
            # special case for default behavior. see FIXME before
            expected_branding = _make_yaplus_branding(mockserver, False)
        else:
            expected_branding = _make_yaplus_branding(
                mockserver, has_cashback_plus=False,
            )
        assert branding == expected_branding

    @pytest.mark.config(**yaplus_brandings.DEFAULT_CONFIG)
    @pytest.mark.parametrize(
        'locale, expected_suffix', [('ru', 'ru'), ('en', 'en'), ('fr', 'en')],
    )
    def test_locale_changes_image_suffixes(
            self, taxi_protocol, mockserver, locale: str, expected_suffix: str,
    ):
        response = _make_zoneinfo_request(
            taxi_protocol, user_id=TEST_USER_ID, accept_language=locale,
        )
        brandings = _parse_brandings(response)
        branding = _get_branding(brandings, 'comfortplus', 'ya_plus')

        expected_active_badge = _make_image(
            mockserver,
            'plus_badge',
            f'plus_badge_{expected_suffix}',
            SIZE_HINT,
        )
        assert branding['icon'] == expected_active_badge

        expected_inactive_badge = _make_image(
            mockserver,
            'plus_badge',
            f'plus_badge_inactive_{expected_suffix}',
            SIZE_HINT,
        )
        assert branding['inactive_icon'] == expected_inactive_badge

    @pytest.mark.translations(client_messages=CLIENT_MESSAGES)
    @pytest.mark.config(**yaplus_brandings.DEFAULT_CONFIG)
    @pytest.mark.user_experiments('hide_branding_payment_subtitle')
    @pytest.mark.parametrize(
        'has_cashback_plus',
        [False, True],
        ids=['discount offer', 'cashback offer'],
    )
    def test_experiment_hides_payment_subtitle(
            self, taxi_protocol, db, mockserver, has_cashback_plus: bool,
    ):
        _update_user(db, TEST_USER_ID, True, has_cashback_plus)

        response = _make_zoneinfo_request(taxi_protocol, user_id=TEST_USER_ID)
        brandings = _parse_brandings(response)
        branding = _get_branding(brandings, 'comfortplus', 'ya_plus')

        expected_branding = _make_yaplus_branding(
            mockserver, has_cashback_plus, payment_subtitile=False,
        )
        assert branding == expected_branding


def _update_user(db, user_id: str, has_ya_plus: bool, has_cashback_plus: bool):
    db.users.update(
        {'_id': user_id},
        {
            '$set': {
                'has_ya_plus': has_ya_plus,
                'has_cashback_plus': has_cashback_plus,
            },
        },
    )


def _make_zoneinfo_request(
        taxi_protocol,
        *,
        user_id: str,
        accept_language: str = DEFAULT_LOCALE,
        **http_kwargs,
) -> dict:
    headers = {
        'Accept-Language': accept_language,
        'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        'User-Agent': '(iPhone; iPhone5,2; iOS 10.3.3; Darwin)',
    }

    body = {
        'id': user_id,
        'zone_name': 'moscow',
        'size_hint': 100,
        'options': True,
        'supports_hideable_tariffs': True,
    }

    response = taxi_protocol.post(
        '3.0/zoneinfo', headers=headers, json=body, **http_kwargs,
    )
    assert response.status_code == 200
    return response.json()


def _parse_brandings(response: dict) -> Dict[str, List[dict]]:
    brandings_by_class = {}
    for element in response['max_tariffs']:
        tariff_name = element['class']
        brandings = element.get('brandings')
        brandings_by_class[tariff_name] = brandings
    return brandings_by_class


def _assert_no_brandings(brandings: Dict[str, List[dict]]):
    assert all(branding is None for branding in brandings.values())


def _get_branding(
        brandings: Dict[str, List[dict]], tariff: str, branding_type: str,
) -> dict:
    assert tariff in brandings
    tariff_brandings = brandings[tariff]
    assert tariff_brandings
    return next(
        branding
        for branding in tariff_brandings
        if branding['type'] == branding_type
    )


def _make_yaplus_branding(
        mockserver,
        has_cashback_plus: bool = False,
        empty_strings: bool = False,
        payment_subtitile: bool = True,
        locale: str = DEFAULT_LOCALE,
) -> dict:
    if has_cashback_plus:
        card = {
            'badge_title': 'Плюс',
            'badge_subtitle': 'Кэшбек',
            'badge_icon': _make_image(
                mockserver,
                'plus_card_cashback',
                'plus_card_cashback',
                SIZE_HINT,
            ),
        }
    else:
        card = {
            'badge_title': 'Плюс',
            'badge_subtitle': 'Постоянная скидка',
            'badge_icon': _make_image(
                mockserver, 'plus_card', 'plus_card', SIZE_HINT,
            ),
        }

    if empty_strings:
        card['badge_title'] = ''
        card['badge_subtitle'] = ''

    icon = _make_image(
        mockserver, 'plus_badge', f'plus_badge_{locale}', SIZE_HINT,
    )
    inactive_icon = _make_image(
        mockserver, 'plus_badge', f'plus_badge_inactive_{locale}', SIZE_HINT,
    )

    branding = {
        'type': 'ya_plus',
        'name': '',
        'brand_color': '#357AFF',
        'card': card,
        'icon': icon,
        'inactive_icon': inactive_icon,
    }

    if payment_subtitile:
        if has_cashback_plus:
            branding['summary_payment_subtitle'] = 'кэшбек от Плюса'
        else:
            branding['summary_payment_subtitle'] = 'скидка от Плюса'

    return branding


def _make_image(mockserver, prefix: str, tag: str, size_hint: int):
    return {
        'size_hint': size_hint,
        'url': mockserver.url(f'static/images/{prefix}/{tag}'),
        'image_tag': tag,
        'url_parts': {
            'key': 'TC',
            'path': f'/static/test-images/{prefix}/{tag}',
        },
    }
