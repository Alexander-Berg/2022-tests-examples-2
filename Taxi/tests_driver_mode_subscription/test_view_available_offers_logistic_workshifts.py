import datetime

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates


_OFFER_CARD_TITLE = 'offer_card_title'
_OFFER_CARD_SUBTITLE = 'offer_card_subtitle'
_OFFER_CARD_DESCRIPTION = 'offer_card_description'
_OFFER_HEADER = 'offer_header'
_OFFER_TEXT = 'offer_text'
_MEMO_HEADER = 'memo_header'
_MEMO_TEXT = 'memo_text'

_DRIVER_MODE_RULES = mode_rules.patched(
    patches=[
        mode_rules.Patch(
            rule_name='logistic', features={'logistic_workshifts': {}},
        ),
        mode_rules.Patch(
            rule_name='logistic2', features={'logistic_workshifts': {}},
        ),
        mode_rules.Patch(
            rule_name='driver_fix',
            stops_at=datetime.datetime.fromisoformat(
                '2000-05-01T05:00:00+00:00',
            ),
        ),
    ],
)

_LOGISTIC_SLOT_ID = '1b488dd5-24d9-48bb-8bfa-65c013755a22'

_MODE_SETTINGS = {'slot_id': _LOGISTIC_SLOT_ID, 'rule_version': 1}


@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders_template',
            'driver_fix': 'driver_fix_template',
            'custom_orders': 'custom_orders_template',
            'geobooking': 'geobooking_template',
            'logistic': 'custom_orders_template',
        },
    },
)
@pytest.mark.now('2020-05-01T12:00:00+0300')
async def test_available_offers_logistic_workshifts_show_selected(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        load_json,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, 'logistic', mocked_time, mode_settings=_MODE_SETTINGS,
        )
        return response

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()

    assert len(doc['ui']['items']) == 3

    assert 'logistic' in doc['driver_modes']
    assert 'orders' in doc['driver_modes']
    assert 'custom_orders' in doc['driver_modes']
    assert 'logistic2' not in doc['driver_modes']

    logistic_card_ctor = doc['ui']['items'][0]

    assert logistic_card_ctor == load_json('expected_offer_card.json')

    driver_modes_item = doc['driver_modes']['logistic']

    assert driver_modes_item == load_json(
        'expected_offer_driver_modes_item.json',
    )
