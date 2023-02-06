import json

import pytest

from individual_tariffs_switch_parametrize import (
    PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS,
)
from protocol import yaplus_brandings

TEST_USER_ID = '536b24fa2816451b855d9a3e640215c3'  # has Plus by default
TEST_DEVICE_ID = 'test_device_id'

FRANCE_IP = '89.185.38.136'
RUSSIA_IP = '2.60.1.1'
DUMMY_IP = '0.0.0.0'

CLIENT_MESSAGES = {
    'branding.name': {'ru': 'Яндекс.Плюс'},
    'branding.profile_badge_title': {'ru': 'Яндекс.Плюс'},
    'branding.profile_badge_subtitle': {'ru': 'Скидка 10%'},
    'branding.cashback.profile_badge_subtitle': {'ru': 'Кэшбек 10%'},
}


@pytest.fixture(scope='function', autouse=True)
def mock_services(mockserver):
    @mockserver.json_handler('/feedback/1.0/wanted/retrieve')
    def mock_feedback(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert sorted(data.keys()) == ['id', 'newer_than', 'phone_id']
        return {'orders': []}


# NOTE: no translations defined for test!
@pytest.mark.config(**yaplus_brandings.DEFAULT_CONFIG)
def test_yaplus_no_translations_no_error(taxi_protocol):
    response = _make_launch_request(
        taxi_protocol, user_id=TEST_USER_ID, accept_language='ru',
    )
    assert 'brandings' not in response


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.config(
    **yaplus_brandings.make_configs(profile_badge={'bad_version_name': {}}),
)
def test_yaplus_bad_config_no_error(taxi_protocol):
    response = _make_launch_request(
        taxi_protocol, user_id=TEST_USER_ID, accept_language='ru',
    )
    assert 'brandings' not in response


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
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_yaplus_base(
        taxi_protocol,
        db,
        has_ya_plus: bool,
        has_cashback_plus: bool,
        individual_tariffs_switch_on,
):
    db.users.update(
        {'_id': TEST_USER_ID},
        {
            '$set': {
                'has_ya_plus': has_ya_plus,
                'has_cashback_plus': has_cashback_plus,
            },
        },
    )

    response = _make_launch_request(
        taxi_protocol,
        user_id=TEST_USER_ID,
        accept_language='ru',
        x_real_ip=RUSSIA_IP,
    )

    if not has_ya_plus:
        assert 'brandings' not in response
        return

    yaplus_branding = _get_yaplus_branding(response)
    expected_branding = _make_yaplus_branding(has_cashback_plus)
    assert expected_branding == yaplus_branding


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
        'discount branding disabled',
        'cashback branding',
        'no branding but user accepted cashback offer',
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_yaplus_base_with_experiment_disabile_discount_brandings(
        taxi_protocol,
        db,
        has_ya_plus: bool,
        has_cashback_plus: bool,
        is_expected_branding: bool,
        individual_tariffs_switch_on,
):
    db.users.update(
        {'_id': TEST_USER_ID},
        {
            '$set': {
                'has_ya_plus': has_ya_plus,
                'has_cashback_plus': has_cashback_plus,
            },
        },
    )

    response = _make_launch_request(
        taxi_protocol,
        user_id=TEST_USER_ID,
        accept_language='ru',
        x_real_ip=RUSSIA_IP,
    )

    if not is_expected_branding:
        assert 'brandings' not in response
        return

    yaplus_branding = _get_yaplus_branding(response)
    expected_branding = _make_yaplus_branding(has_cashback_plus)
    assert expected_branding == yaplus_branding


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.config(**yaplus_brandings.DEFAULT_CONFIG)
@pytest.mark.parametrize(
    'db_users_has_cashback_plus, remote_ip, expected_has_cashback_plus',
    [
        (False, RUSSIA_IP, False),
        (True, RUSSIA_IP, True),
        (True, FRANCE_IP, False),
        (True, DUMMY_IP, False),
    ],
    ids=[
        'no cashback in db.users',
        'ok cashback in Russia',
        'no cashback in France',
        'no cashback for dummy ip',
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_yaplus_cashback_by_country(
        taxi_protocol,
        db,
        db_users_has_cashback_plus,
        remote_ip,
        expected_has_cashback_plus,
        individual_tariffs_switch_on,
):
    db.users.update(
        {'_id': TEST_USER_ID},
        {
            '$set': {
                'has_ya_plus': True,
                'has_cashback_plus': db_users_has_cashback_plus,
            },
        },
    )

    response = _make_launch_request(
        taxi_protocol,
        user_id=TEST_USER_ID,
        accept_language='ru',
        x_real_ip=remote_ip,
    )

    yaplus_branding = _get_yaplus_branding(response)
    expected_branding = _make_yaplus_branding(expected_has_cashback_plus)
    assert expected_branding == yaplus_branding


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.config(**yaplus_brandings.DEFAULT_CONFIG)
@pytest.mark.config(
    CASHBACK_FOR_PLUS_COUNTRIES={'check_enabled': False, 'countries': []},
)
@pytest.mark.parametrize(
    'db_users_has_cashback_plus, remote_ip, expected_has_cashback_plus',
    [
        (False, RUSSIA_IP, False),
        (True, RUSSIA_IP, True),
        (True, FRANCE_IP, True),
        (True, DUMMY_IP, True),
    ],
    ids=[
        'no cashback in db.users',
        'ok cashback in Russia',
        'ok cashback in France',
        'ok cashback for dummy ip',
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_yaplus_cashback_by_country_check_disabled(
        taxi_protocol,
        db,
        db_users_has_cashback_plus,
        remote_ip,
        expected_has_cashback_plus,
        individual_tariffs_switch_on,
):
    db.users.update(
        {'_id': TEST_USER_ID},
        {
            '$set': {
                'has_ya_plus': True,
                'has_cashback_plus': db_users_has_cashback_plus,
            },
        },
    )

    response = _make_launch_request(
        taxi_protocol,
        user_id=TEST_USER_ID,
        accept_language='ru',
        x_real_ip=remote_ip,
    )

    yaplus_branding = _get_yaplus_branding(response)
    expected_branding = _make_yaplus_branding(expected_has_cashback_plus)
    assert expected_branding == yaplus_branding


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.config(
    **yaplus_brandings.make_configs(
        menu_icon={'__default__': 'plus_profile_icon'},
    ),
)
@pytest.mark.parametrize(
    'has_cashback_plus',
    [False, True],
    ids=['discount branding', 'cashback branding'],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_yaplus_only_default_defined_for_menu_icon(
        taxi_protocol,
        db,
        has_cashback_plus: bool,
        individual_tariffs_switch_on,
):
    db.users.update(
        {'_id': TEST_USER_ID},
        {'$set': {'has_cashback_plus': has_cashback_plus}},
    )

    response = _make_launch_request(
        taxi_protocol, user_id=TEST_USER_ID, accept_language='ru',
    )

    yaplus_branding = _get_yaplus_branding(response)
    expected_tag = 'plus_profile_icon_ru'
    assert yaplus_branding['profile']['title_badge_tag'] == expected_tag


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.config(**yaplus_brandings.DEFAULT_CONFIG)
@pytest.mark.parametrize(
    'locale, expected_suffix', [('ru', 'ru'), ('en', 'en'), ('fr', 'en')],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_yaplus_locale_changes_menu_icon_suffix(
        taxi_protocol,
        db,
        locale: str,
        expected_suffix: str,
        individual_tariffs_switch_on,
):
    response = _make_launch_request(
        taxi_protocol, user_id=TEST_USER_ID, accept_language=locale,
    )

    yaplus_branding = _get_yaplus_branding(response)
    expected_tag = 'plus_discount_profile_icon_' + expected_suffix
    assert yaplus_branding['profile']['title_badge_tag'] == expected_tag


def _get_yaplus_branding(response: dict) -> dict:
    assert 'brandings' in response and len(response['brandings']) == 1
    return response['brandings'][0]


def _make_yaplus_branding(has_cashback_plus: bool) -> dict:
    if has_cashback_plus:
        profile = {
            'badge_image_tag': 'plus_card_cashback',
            'badge_subtitle': 'Кэшбек 10%',
            'badge_title': 'Яндекс.Плюс',
            'title_badge_tag': 'plus_cashback_profile_icon_ru',
        }
    else:
        profile = {
            'badge_image_tag': 'plus_card',
            'badge_subtitle': 'Скидка 10%',
            'badge_title': 'Яндекс.Плюс',
            'title_badge_tag': 'plus_discount_profile_icon_ru',
        }

    return {
        'brand_color': '#357AFF',
        'link': 'https://plus.yandex.ru',
        'name': 'Яндекс.Плюс',
        'profile': profile,
        'type': 'ya_plus',
    }


def _make_launch_request(
        taxi_protocol,
        *,
        user_id: str,
        supported_features: list = None,
        auth_confirmed: bool = True,
        accept_language: str = 'ru',
        **http_kwargs,
) -> dict:
    headers = {'Accept-Language': accept_language}
    if auth_confirmed:
        headers['X-Yandex-Auth-Confirmed'] = 'true'

    body = {
        'id': user_id,
        # 'device_id': TEST_DEVICE_ID,
        'supported_features': supported_features or [],
    }

    response = taxi_protocol.post(
        '3.0/launch', headers=headers, json=body, **http_kwargs,
    )
    assert response.status_code == 200
    return response.json()
