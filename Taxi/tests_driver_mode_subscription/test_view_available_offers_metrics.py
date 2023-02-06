import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_NOW = datetime.datetime.fromisoformat('2019-05-01T12:00:00+03:00')
_LONG_AGO = datetime.datetime.fromisoformat('2010-05-01T12:00:00+03:00')

_VIEW_OFFERS: List[Dict[str, Any]] = [
    {
        'offer_card': {
            'title': 'За время',
            'subtitle': 'Доступен до 2 декабря',
            'description': 'Заработок зависит от времени работы',
            'is_new': True,
            'enabled': True,
        },
        'settings': {'rule_id': 'id_rule1', 'shift_close_time': '00:01'},
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 1.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 1'}]},
    },
]

_VIEW_GEOBOOKING_OFFERS: List[Dict[str, Any]] = [
    {
        'offer_card': {
            'title': 'За geobooking',
            'description': 'Заработок за бонусы по времени',
            'is_new': True,
            'enabled': True,
        },
        'key_params': {
            'tariff_zone': 'test_tariff_zone',
            'subvention_geoarea': 'test_subvention_geoarea',
            'tag': 'no_free_slots_tag',
        },
        'settings': {'rule_id': 'id_rule1'},
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 1.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 1'}]},
    },
]


def _mock_driver_fix(mockserver):
    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': _VIEW_OFFERS}


def _mock_driver_fix_fail(mockserver):
    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        raise mockserver.NetworkError()


def _mock_geobooking(mockserver):
    @mockserver.json_handler('/driver-fix/v1/view/geobooking_offer')
    async def _mock_view_offer(request):
        return {'offers': _VIEW_GEOBOOKING_OFFERS}


def _mock_geobooking_fail(mockserver):
    @mockserver.json_handler('/driver-fix/v1/view/geobooking_offer')
    async def _mock_view_offer(request):
        raise mockserver.NetworkError()


def _validate_metric(
        metrics: Dict[str, Any], path: str, expected_value: Optional[int],
):
    keys = path.split('.')
    current_item = metrics
    for key in keys:
        if key not in current_item:
            assert expected_value is None
            return
        current_item = current_item[key]
    assert current_item == expected_value


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
        '__default__': {
            'restrictions': [],
            'warnings': {
                'title': 'accept_warning.title',
                'message': 'accept_warning.message',
                'accept': 'accept_warning.accept',
                'reject': 'accept_warning.reject',
            },
        },
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
        'templates': {
            'orders': offer_templates.DEFAULT_ORDERS_TEMPLATE,
            'driver_fix': offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE,
            'geobooking': offer_templates.DEFAULT_GEOBOOKING_TEMPLATE,
            'custom_orders': offer_templates.build_orders_template(
                card_title='bad',
                card_subtitle=None,
                card_description='bad',
                screen_header='bad',
                screen_description='bad',
                memo_header='bad',
                memo_description='bad',
            ),
        },
    },
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders',
            'driver_fix': 'driver_fix',
            'custom_orders': 'custom_orders',
            'geobooking': 'geobooking',
            'eda_orders': 'orders',
            'lavka_orders': 'orders',
            'uberdriver': 'orders',
        },
    },
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch('eda_orders', offers_group='eda'),
            mode_rules.Patch('lavka_orders', offers_group='lavka'),
            mode_rules.Patch('geobooking', features={'geobooking': {}}),
            mode_rules.Patch('custom_orders', stops_at=_LONG_AGO),
        ],
    ),
)
@pytest.mark.parametrize(
    'current_work_mode, fail_driver_fix, fail_geobooking, '
    'fail_driver_trackstory, no_client_position, metrics_to_check',
    [
        pytest.param(
            'eda_orders',
            False,
            False,
            True,
            False,
            {
                'requests.eda': 1,
                'offers_provider_status.success.'
                'driver_mode_subscription.eda': 1,
                # check that unrelated metrics not changed, just in case
                'requests.lavka': None,
                'offers_provider_status.fail.driver_mode_subscription.eda': (
                    None
                ),
                'offers_provider_status.success.driver_fix.eda': None,
                'many_offers_requests.eda': None,
                'no_client_position.eda': None,
            },
            id='eda_request',
        ),
        pytest.param(
            'lavka_orders',
            False,
            False,
            True,
            False,
            {
                'requests.lavka': 1,
                'offers_provider_status.success.'
                'driver_mode_subscription.lavka': 1,
            },
            id='lavka_request',
        ),
        pytest.param(
            'uberdriver',
            False,
            False,
            True,
            False,
            {
                'requests.no_group': 1,
                'offers_provider_status.success.'
                'driver_mode_subscription.eda': None,
            },
            id='no_group_request',
        ),
        pytest.param(
            'orders',
            False,
            False,
            True,
            False,
            {
                'requests.taxi': 1,
                'offers_provider_status.success.'
                'driver_mode_subscription.taxi': 1,
                'offers_provider_status.success.driver_fix.taxi': 1,
                'offers_provider_status.success.geobooking.taxi': 1,
                'many_offers_requests.taxi': 1,
            },
            id='taxi_request',
        ),
        pytest.param(
            'orders',
            True,
            False,
            True,
            False,
            {
                'requests.taxi': 1,
                'offers_provider_status.success.'
                'driver_mode_subscription.taxi': 1,
                'offers_provider_status.success.geobooking.taxi': 1,
                'offers_provider_status.fail.driver_fix.taxi': 1,
                'many_offers_requests.taxi': 1,
            },
            id='fail_driver_fix',
        ),
        pytest.param(
            'orders',
            False,
            True,
            True,
            False,
            {
                'requests.taxi': 1,
                'offers_provider_status.success.'
                'driver_mode_subscription.taxi': 1,
                'offers_provider_status.success.driver_fix.taxi': 1,
                'offers_provider_status.fail.geobooking.taxi': 1,
                'many_offers_requests.taxi': 1,
            },
            id='fail_geobooking',
        ),
        pytest.param(
            'orders',
            True,
            True,
            True,
            False,
            {
                'requests.taxi': 1,
                'offers_provider_status.success.'
                'driver_mode_subscription.taxi': 1,
                'offers_provider_status.fail.driver_fix.taxi': 1,
                'offers_provider_status.fail.geobooking.taxi': 1,
                'many_offers_requests.taxi': None,
            },
            id='fail_driver_fix_and_geobooknig',
        ),
        pytest.param(
            'orders',
            True,
            True,
            True,
            False,
            {
                'requests.taxi': 1,
                'offers_provider_status.success.'
                'driver_mode_subscription.taxi': None,
                'offers_provider_status.fail.driver_mode_subscription.taxi': 1,
                'offers_provider_status.fail.driver_fix.taxi': 1,
                'offers_provider_status.fail.geobooking.taxi': 1,
                'many_offers_requests.taxi': None,
            },
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        patches=[
                            mode_rules.Patch('custom_orders', stops_at=_NOW),
                            mode_rules.Patch(
                                'geobooking', features={'geobooking': {}},
                            ),
                        ],
                    ),
                ),
            ],
            id='fail_own_offer',
        ),
        pytest.param(
            'orders',
            False,
            False,
            True,
            True,
            {'no_client_position.taxi': 1},
            id='no_client_position',
        ),
        pytest.param(
            'orders',
            False,
            False,
            True,
            True,
            {'position_fetch_errors.taxi': 1},
            id='no_position',
        ),
        pytest.param(
            'orders',
            False,
            False,
            True,
            False,
            {'position_fetch_errors.taxi': None},
            id='has_client_position',
        ),
        pytest.param(
            'orders',
            False,
            False,
            False,
            True,
            {'position_fetch_errors.taxi': None},
            id='has_server_position',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_available_offers_metrics(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_driver_mode_subscription_monitor,
        current_work_mode: str,
        fail_driver_fix: bool,
        fail_geobooking: bool,
        fail_driver_trackstory: bool,
        no_client_position: bool,
        # metric paths and expected values, other metrics will be ignored
        metrics_to_check: Dict[str, int],
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return common.mode_history_response(
            request, current_work_mode, mocked_time,
        )

    if fail_driver_trackstory:
        scenario.Scene.mock_driver_trackstory(mockserver)
    else:
        scenario.Scene.mock_driver_trackstory(
            mockserver, common.Position(55, 37),
        )

    if fail_driver_fix:
        _mock_driver_fix_fail(mockserver)
    else:
        _mock_driver_fix(mockserver)

    if fail_geobooking:
        _mock_geobooking_fail(mockserver)
    else:
        _mock_geobooking(mockserver)

    await taxi_driver_mode_subscription.tests_control(reset_metrics=True)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription,
        profile,
        client_position=None
        if no_client_position
        else common.Position(55, 37),
    )
    assert response.status_code == 200

    metrics = await taxi_driver_mode_subscription_monitor.get_metric(
        'available-offers',
    )

    for key, value in metrics_to_check.items():
        _validate_metric(metrics, key, value)
