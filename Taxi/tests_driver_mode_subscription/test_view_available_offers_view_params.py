import datetime
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

AUTH_PARAMS = {'park_id': 'dbid'}

HEADERS = {
    'User-Agent': 'Taximeter 8.80 (562)',
    'X-Driver-Session': 'session1',
    'Accept-Language': 'ru',
}


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch(
                rule_name='custom_orders',
                starts_at=datetime.datetime.fromisoformat(
                    '2020-05-01T05:00:00+00:00',
                ),
            ),
            mode_rules.Patch(
                rule_name='custom_orders',
                starts_at=datetime.datetime.fromisoformat(
                    '2020-05-06T05:00:00+00:00',
                ),
                stops_at=datetime.datetime.fromisoformat(
                    '2020-05-08T05:00:00+00:00',
                ),
            ),
            mode_rules.Patch(
                rule_name='driver-fix',
                starts_at=datetime.datetime.fromisoformat(
                    '2020-05-01T05:00:00+00:00',
                ),
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'expect_new',
    [
        pytest.param(
            False,
            id='new_days default disabled',
            marks=[pytest.mark.now('2020-05-05T05:00:00+00:00')],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.now('2020-05-05T05:00:00+00:00'),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_SETTINGS={},
                ),
            ],
            id='new_days disabled',
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.now('2020-05-05T05:00:00+00:00'),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_SETTINGS={
                        'new_days': 5,
                    },
                ),
            ],
            id='new_days enabled',
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.now('2020-05-07T05:00:00+00:00'),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_SETTINGS={
                        'new_days': 5,
                    },
                ),
            ],
            id='new_days enabled version with stops_at',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.now('2020-05-05T05:00:00+00:00'),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_SETTINGS={
                        'new_days': 4,
                    },
                ),
            ],
            id='new_days enabled, but already pass',
        ),
    ],
)
async def test_view_params_new_days(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        expect_new: bool,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {
            'offers': [
                {
                    'offer_card': {
                        'title': 'За время',
                        'subtitle': 'Доступен до 2 декабря',
                        'description': 'Заработок зависит от времени работы',
                        'is_new': False,
                        'enabled': True,
                    },
                    'settings': {
                        'rule_id': 'id_rule1',
                        'shift_close_time': '00:01',
                    },
                    'offer_screen': {
                        'items': [
                            {'type': 'text', 'text': 'Подробности правила 1.'},
                        ],
                    },
                    'memo_screen': {
                        'items': [{'type': 'text', 'text': 'Memo правила 1'}],
                    },
                },
            ],
        }

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()

    assert doc['driver_modes']['custom_orders']['is_new'] == expect_new
    assert doc['driver_modes']['driver_fix_id_rule1']['is_new'] is False


def _assert_ui_item(
        doc,
        offer_id: str,
        expect_subtitle: str,
        expect_enabled: bool,
        expect_new: bool,
):
    for item in doc['ui']['items']:
        if item['id'] == offer_id:
            assert item['items'][0]['subtitle'] == expect_subtitle
            break

    assert (
        doc['driver_modes'][offer_id]['ui']['accept_button']['enabled']
        == expect_enabled
    )

    assert doc['driver_modes'][offer_id]['is_new'] == expect_new

    assert (
        doc['driver_modes'][offer_id]['ui']['accept_button']['title']
        == 'Выбрать'
        if expect_enabled
        else expect_subtitle
    )


_DEFAULT_DRIVER_MODE_RULES_OLD_DAYS = mode_rules.patched(
    patches=[
        mode_rules.Patch(
            rule_name='custom_orders',
            starts_at=datetime.datetime.fromisoformat(
                '2020-03-01T12:34:56+00:00',
            ),
        ),
        mode_rules.Patch(
            rule_name='custom_orders',
            starts_at=datetime.datetime.fromisoformat(
                '2020-04-01T12:34:56+00:00',
            ),
            stops_at=datetime.datetime.fromisoformat(
                '2020-05-01T12:34:56+00:00',
            ),
        ),
        mode_rules.Patch(
            rule_name='driver_fix',
            stops_at=datetime.datetime.fromisoformat(
                '2020-05-01T12:34:56+00:00',
            ),
        ),
    ],
)


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DEFAULT_DRIVER_MODE_RULES_OLD_DAYS)
@pytest.mark.parametrize(
    'expected_in_offers, expected_subtitle, expect_enabled, expect_new',
    [
        pytest.param(
            False,
            None,
            False,
            False,
            id='old_days default disabled',
            marks=[pytest.mark.now('2020-05-05T13:00:00+00:00')],
        ),
        pytest.param(
            False,
            None,
            False,
            False,
            marks=[
                pytest.mark.now('2020-05-05T13:00:00+00:00'),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_SETTINGS={},
                ),
            ],
            id='old_days disabled',
        ),
        pytest.param(
            False,
            None,
            False,
            False,
            marks=[
                pytest.mark.now('2020-05-05T13:00:00+00:00'),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_SETTINGS={
                        'old_days': 4,
                    },
                ),
            ],
            id='old_days enabled, but already pass',
        ),
        pytest.param(
            True,
            'Был доступен до 15:34',
            False,
            False,
            marks=[
                pytest.mark.now('2020-05-01T13:00:00+00:00'),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_SETTINGS={
                        'old_days': 4,
                    },
                ),
            ],
            id='old_days enabled today',
        ),
        pytest.param(
            True,
            'Был доступен до 15:34 1 мая',
            False,
            False,
            marks=[
                pytest.mark.now('2020-05-05T13:00:00+00:00'),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_SETTINGS={
                        'old_days': 5,
                        'new_days': 1,
                    },
                ),
            ],
            id='old_days enabled not today, not new',
        ),
        pytest.param(
            True,
            'Был доступен до 15:34 1 мая',
            False,
            True,
            marks=[
                pytest.mark.now('2020-05-05T13:00:00+00:00'),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_SETTINGS={
                        'old_days': 5,
                        'new_days': 5,
                    },
                ),
            ],
            id='old_days enabled not today, is new',
        ),
        pytest.param(
            True,
            'Доступен до 15:34',
            True,
            False,
            marks=[
                pytest.mark.now('2020-05-01T11:00:00+00:00'),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_SETTINGS={
                        'new_days': 1,
                    },
                ),
            ],
            id='expire today',
        ),
        pytest.param(
            True,
            'Доступен до 15:34 1 мая',
            True,
            False,
            marks=[pytest.mark.now('2020-04-30T11:00:00+00:00')],
            id='expire in future',
        ),
        pytest.param(
            True,
            'Доступен до 15:34 1 мая',
            True,
            False,
            marks=[pytest.mark.now('2020-04-30T11:00:00+00:00')],
            id='expire in future',
        ),
    ],
)
async def test_view_params_old_days(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        expected_in_offers: bool,
        expect_enabled: bool,
        expect_new: bool,
        expected_subtitle: Optional[str],
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {
            'offers': [
                {
                    'offer_card': {
                        'title': 'За время',
                        'subtitle': 'some-subtitle',
                        'description': 'Заработок зависит от времени работы',
                        'is_new': False,
                        'enabled': True,
                    },
                    'settings': {
                        'rule_id': 'id_rule1',
                        'shift_close_time': '00:01',
                    },
                    'offer_screen': {
                        'items': [
                            {'type': 'text', 'text': 'Подробности правила 1.'},
                        ],
                    },
                    'memo_screen': {
                        'items': [{'type': 'text', 'text': 'Memo правила 1'}],
                    },
                },
                {
                    'offer_card': {
                        'title': 'За время',
                        'subtitle': 'driver-fix-disabled',
                        'disable_reason': 'driver-fix-disabled',
                        'description': 'Заработок зависит от времени работы',
                        'is_new': False,
                        'enabled': False,
                    },
                    'settings': {
                        'rule_id': 'id_rule2',
                        'shift_close_time': '00:01',
                    },
                    'offer_screen': {
                        'items': [
                            {'type': 'text', 'text': 'Подробности правила 1.'},
                        ],
                    },
                    'memo_screen': {
                        'items': [{'type': 'text', 'text': 'Memo правила 1'}],
                    },
                },
            ],
        }

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()
    if expected_in_offers:
        assert len(doc['ui']['items']) == 4

        _assert_ui_item(
            doc,
            'custom_orders',
            str(expected_subtitle),
            expect_enabled,
            expect_new,
        )

        _assert_ui_item(
            doc, 'driver_fix_id_rule1', 'some-subtitle', True, False,
        )

        _assert_ui_item(
            doc, 'driver_fix_id_rule2', 'driver-fix-disabled', False, False,
        )
    else:
        assert len(doc['ui']['items']) == 1
        assert not doc['driver_modes'].get('custom_orders')
        assert not doc['driver_modes'].get('driver_fix_id_rule1')
        assert not doc['driver_modes'].get('driver_fix_id_rule2')


@pytest.mark.now('2020-05-05T13:00:00+00:00')
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DEFAULT_DRIVER_MODE_RULES_OLD_DAYS)
async def test_view_params_old_days_show_current(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, 'custom_orders', mocked_time,
        )
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': []}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()
    assert len(doc['ui']['items']) == 2

    assert doc['ui']['items'][0]['id'] == 'custom_orders'
    assert doc['ui']['items'][0]['items'][0]['subtitle'] == 'Выбранный'
    assert (
        doc['driver_modes']['custom_orders']['ui']['accept_button']['title']
        == 'Режим уже выбран'
    )


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch(
                rule_name='custom_orders',
                stops_at=datetime.datetime.fromisoformat(
                    '2020-05-01T20:34:56+00:00',
                ),
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_SETTINGS={'old_days': 5},
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.parametrize(
    'timezone, expected_code, expected_subtitle',
    [
        pytest.param(
            'Asia/Vladivostok',
            200,
            'Был доступен до 6:34',
            marks=[pytest.mark.now('2020-05-01T21:00:00+00:00')],
            id='vladivostok timezone',
        ),
        pytest.param(
            'Asia/Vladivostok',
            200,
            'Был доступен до 6:34 2 мая',
            marks=[pytest.mark.now('2020-05-03T13:00:00+00:00')],
            id='vladivostok timezone',
        ),
        pytest.param(
            'Europe/Moscow',
            200,
            'Был доступен до 23:34 1 мая',
            marks=[pytest.mark.now('2020-05-05T11:00:00+00:00')],
            id='explicit moscow timezone',
        ),
        pytest.param(
            'GMT+3',
            200,
            'Был доступен до 23:34 1 мая',
            marks=[pytest.mark.now('2020-05-05T11:00:00+00:00')],
            id='short GMT custom timezone',
        ),
        pytest.param(
            'GMT+300',
            200,
            'Был доступен до 23:34 1 мая',
            marks=[pytest.mark.now('2020-05-05T11:00:00+00:00')],
            id='GMT custom timezone',
        ),
        pytest.param(
            'GMT+03:00',
            200,
            'Был доступен до 23:34 1 мая',
            marks=[pytest.mark.now('2020-05-05T11:00:00+00:00')],
            id='normalized GMT custom timezone',
        ),
        pytest.param(
            'GMT+03:13',
            200,
            'Был доступен до 23:47 1 мая',
            marks=[pytest.mark.now('2020-05-05T11:00:00+00:00')],
            id='non-zero minutes GMT custom timezone',
        ),
        pytest.param(
            'Europe/New-York',
            400,
            '',
            marks=[pytest.mark.now('2020-05-05T11:00:00+00:00')],
            id='explicit wrong timezone passed',
        ),
    ],
)
async def test_view_params_old_days_timezone(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        timezone: str,
        expected_code: int,
        expected_subtitle: Optional[str],
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': []}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile, timezone=timezone,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        doc = response.json()

        assert len(doc['ui']['items']) == 2

        _assert_ui_item(
            doc, 'custom_orders', str(expected_subtitle), False, False,
        )
