from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import diagnostics
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_NOW = '2020-08-03T19:51:00+00:00'
_RECENTLY = '2020-08-03T16:21:00+00:00'
_HISTORY_CHUNK_SIZE = 5
_DRIVER_FIX_SETTINGS = {'rule_id': 'some_id', 'shift_close_time': '00:00'}
_DRIVER_FIX_LONGTERM_SETTINGS = {
    'rule_id': 'longterm_id',
    'shift_close_time': '23:00',
}
_GEOBOOKING_SETTINGS = {
    'rule_id': 'geobooking_id',
    'shift_close_time': '23:00',
}
_SETTINGS_BY_MODE = {
    'driver_fix': _DRIVER_FIX_SETTINGS,
    'driver_fix_longterm': _DRIVER_FIX_LONGTERM_SETTINGS,
    'geobooking': _GEOBOOKING_SETTINGS,
    'geobooking_no_locale': _GEOBOOKING_SETTINGS,
}
_MODE_DRIVER_FIX = {'id': 'driver_fix', 'name': 'За время'}
_MODE_DRIVER_FIX_LONGTERM = {
    'id': 'driver_fix_longterm',
    'name': 'За время с бонусами',
}
_MODE_ORDERS = {'id': 'orders', 'name': 'За заказы'}
_MODE_GEOBOOKING = {'id': 'geobooking', 'name': 'За гарантии'}
_MODE_GEOBOOKING_NO_LOCALE = {
    'id': 'geobooking_no_locale',
    'name': 'geobooking_no_locale',
}


def _get_history_chunk(
        history: List[Tuple[str, str, Optional[Dict[str, str]]]],
        chunk_number: int,
        chunk_size: int,
):
    result = []
    docs_start = chunk_number * chunk_size
    docs_end = docs_start + chunk_size
    for occured, mode, subscription_data in history[docs_start:docs_end]:
        data = {
            'driver': {'park_id': 'dbid0', 'driver_profile_id': 'uuid0'},
            'mode': mode,
        }
        if mode in _SETTINGS_BY_MODE:
            data['settings'] = _SETTINGS_BY_MODE[mode]

        if subscription_data:
            data['subscription_data'] = subscription_data

        result.append(
            {
                'kind': 'driver_mode_subscription',
                'external_event_ref': 'idempotency',
                'event_at': occured,
                'data': data,
            },
        )
    return result


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name='geobooking_no_locale', features={'geobooking': {}},
            ),
            mode_rules.Patch(
                rule_name='geobooking', features={'geobooking': {}},
            ),
            mode_rules.Patch(rule_name='orders', display_mode='orders'),
            mode_rules.Patch(
                rule_name='driver_fix_longterm',
                features={'driver_fix': {'roles': [{'name': 'longterm'}]}},
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_ADMIN_MODE_HISTORY_BULK_SIZE=_HISTORY_CHUNK_SIZE,
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
        'templates': {
            'orders_template': offer_templates.DEFAULT_ORDERS_TEMPLATE,
            'driver_fix_template': offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE,
            'driver_fix_longterm_template': (
                offer_templates.build_driver_fix_template(
                    'offer_card.title_longterm',
                )
            ),
            'geobooking_template': offer_templates.DEFAULT_GEOBOOKING_TEMPLATE,
            'geobooking_bad_key_template': (
                offer_templates.build_geobooking_template('bad_key')
            ),
        },
    },
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders_template',
            'geobooking': 'geobooking_template',
            'geobooking_no_locale': 'geobooking_bad_key_template',
            'driver_fix': 'driver_fix_template',
            'driver_fix_longterm': 'driver_fix_longterm_template',
        },
    },
)
@pytest.mark.parametrize(
    'cursor, expected_cursor, limit, expected_code, expected_history,'
    'mode_history',
    [
        pytest.param(
            '1',  # get second chunk
            '2',  # cursor for next chunk
            2,
            200,
            [
                {
                    'mode': _MODE_ORDERS,
                    'started_at': '2020-08-03T19:49:00+00:00',
                    'subscription': {},
                },
            ],
            [
                ('2020-08-03T19:51:00+00:00', 'driver_fix', None),
                ('2020-08-03T19:50:00+00:00', 'driver_fix', None),
                ('2020-08-03T19:49:00+00:00', 'orders', None),
            ],
            id='known_cursor_custom_limit',
        ),
        pytest.param(
            None,
            '1',  # cursor for second chunk
            None,
            200,
            [
                {
                    'features': [{'name': 'geobooking', 'settings': {}}],
                    'mode': _MODE_GEOBOOKING_NO_LOCALE,
                    'started_at': '2020-07-02T19:51:00+00:00',
                    'subscription': diagnostics.subscription(
                        _SETTINGS_BY_MODE['geobooking_no_locale'],
                        'geobooking',
                    ),
                },
                {
                    'features': [{'name': 'geobooking', 'settings': {}}],
                    'mode': _MODE_GEOBOOKING,
                    'started_at': '2020-08-02T19:51:00+00:00',
                    'subscription': diagnostics.subscription(
                        _SETTINGS_BY_MODE['geobooking'], 'geobooking',
                    ),
                },
                {
                    'features': [{'name': 'driver_fix', 'settings': {}}],
                    'mode': _MODE_DRIVER_FIX,
                    'started_at': '2020-08-03T19:51:00+00:00',
                    'subscription': diagnostics.subscription(
                        _SETTINGS_BY_MODE['driver_fix'], 'driver_fix',
                    ),
                },
                {
                    'features': [
                        {
                            'name': 'driver_fix',
                            'settings': {'roles': [{'name': 'longterm'}]},
                        },
                    ],
                    'mode': _MODE_DRIVER_FIX_LONGTERM,
                    'started_at': '2020-08-03T19:50:00+00:00',
                    'subscription': diagnostics.subscription(
                        _SETTINGS_BY_MODE['driver_fix_longterm'], 'driver_fix',
                    ),
                },
                {
                    'mode': _MODE_ORDERS,
                    'started_at': '2020-08-03T19:49:00+00:00',
                    'subscription': {},
                },
            ],
            [
                ('2020-07-02T19:51:00+00:00', 'geobooking_no_locale', None),
                ('2020-08-02T19:51:00+00:00', 'geobooking', None),
                ('2020-08-03T19:51:00+00:00', 'driver_fix', None),
                ('2020-08-03T19:50:00+00:00', 'driver_fix_longterm', None),
                ('2020-08-03T19:49:00+00:00', 'orders', None),
                ('2020-08-03T19:48:00+00:00', 'orders', None),
            ],
            id='no_cursor_config_limit',
        ),
        pytest.param(
            None,
            '1',  # cursor for second chunk
            None,
            200,
            [
                {
                    'mode': _MODE_ORDERS,
                    'started_at': '2020-08-03T19:51:00+00:00',
                    'subscription': {},
                },
                {
                    'mode': _MODE_ORDERS,
                    'started_at': '2020-08-03T19:49:00+00:00',
                    'subscription': {
                        'source': 'subscription_sync',
                        'reason': 'different_profile_usage',
                    },
                },
            ],
            [
                ('2020-08-03T19:51:00+00:00', 'orders', None),
                (
                    '2020-08-03T19:49:00+00:00',
                    'orders',
                    {
                        'source': 'subscription_sync',
                        'reason': 'different_profile_usage',
                    },
                ),
            ],
            id='subscription_reason',
        ),
    ],
)
async def test_view_history(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        mode_rules_data,
        driver_authorizer,
        cursor: Optional[str],
        expected_cursor: str,
        limit: Optional[int],
        expected_code: int,
        expected_history: List[Dict[str, Any]],
        mode_history: List[Tuple[str, str, Optional[Dict[str, str]]]],
):
    driver_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(
        profiles={
            driver_profile: driver.Mode(
                work_mode='driver_fix', started_at_iso=_RECENTLY,
            ),
        },
    )
    scene.setup(
        mockserver, mocked_time, driver_authorizer, mock_dmi_history=False,
    )

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        expected_limit = limit if limit else _HISTORY_CHUNK_SIZE
        assert request.json['limit'] == expected_limit

        chunk_number = int(request.json.get('cursor', '0'))
        return {
            'docs': _get_history_chunk(
                mode_history, chunk_number, expected_limit,
            ),
            'cursor': f'{chunk_number + 1}',
        }

    response = await common.get_mode_change_history(
        taxi_driver_mode_subscription,
        driver_profile=driver_profile,
        cursor=cursor,
        limit=limit,
    )

    assert expected_code == response.status_code
    response_json = response.json()
    # TODO: this code can be removed for ApplyRules::DbOnly
    for history_item in response_json['history']:
        mode = history_item['mode']
        assert 'rule_id' in mode
        assert mode['rule_id'] != ''
        del mode['rule_id']
    assert response_json == {
        'cursor': expected_cursor,
        'history': expected_history,
    }
