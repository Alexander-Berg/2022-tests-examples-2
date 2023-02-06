import datetime

import pytest
import pytz

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules

REQUEST_PARAMS = {'park_id': 'park_id_0', 'driver_profile_id': 'uuid'}

REQUEST_HEADER = {
    'User-Agent': 'Taximeter 8.90 (228)',
    'X-Ya-Service-Ticket': common.MOCK_TICKET,
}

_NOW = '2019-05-01T05:00:00+00:00'


@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'features, excepted_features',
    [
        pytest.param([], None, id='no_features'),
        pytest.param(
            {'driver_fix': {}}, [common.DRIVER_FIX_FEATURE], id='driver_fix',
        ),
        pytest.param(
            {'geobooking': {}}, [common.GEOBOOKING_FEATURE], id='geobooking',
        ),
        pytest.param(
            {
                'driver_fix': {},
                'tags': {'assign': ['driver_fix']},
                'reposition': {'profile': 'home'},
                'active_transport': {'type': 'bicycle'},
                'geobooking': {},
            },
            [
                common.DRIVER_FIX_FEATURE,
                common.TAGS_FEATURE,
                common.REPOSITION_FEATURE,
                common.ACTIVE_TRANSPORT_FEATURE,
                common.GEOBOOKING_FEATURE,
            ],
            id='driver_fix_and_tags',
        ),
    ],
)
async def test_mode_info(
        mockserver,
        mocked_time,
        mode_rules_data,
        taxi_driver_mode_subscription,
        features,
        excepted_features,
):
    mode_name = 'custom_mode'
    mode_type = 'custom_mode_type'
    starts_at_before = mocked_time.now() - datetime.timedelta(hours=2)
    stops_at_after = mocked_time.now() + datetime.timedelta(hours=1)
    starts_at_after = mocked_time.now() + datetime.timedelta(hours=2)

    patches = [
        mode_rules.Patch(
            rule_name=mode_name,
            display_mode=mode_type,
            features=features,
            starts_at=pytz.utc.localize(starts_at_before),
            stops_at=pytz.utc.localize(stops_at_after),
        ),
        mode_rules.Patch(
            rule_name='future_rule',
            display_mode='future_rule_type',
            assign_tags=['future_rule_tag'],
            starts_at=pytz.utc.localize(starts_at_after),
        ),
    ]

    mode_rules_data.set_mode_rules(patches=patches)

    await taxi_driver_mode_subscription.invalidate_caches()

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return common.mode_history_response(
            request,
            mode_name,
            mocked_time,
            mode_settings=common.MODE_SETTINGS,
        )

    await taxi_driver_mode_subscription.invalidate_caches()
    response = await taxi_driver_mode_subscription.get(
        'v1/mode/info', params=REQUEST_PARAMS, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    excepted_response = {
        'mode': {
            'name': mode_name,
            'started_at': mocked_time.now().strftime(
                '%Y-%m-%dT%H:%M:%S+00:00',
            ),
        },
    }
    if excepted_features:
        excepted_response['mode']['features'] = []
        for feature in excepted_features:
            item = {'name': feature}
            if feature in common.FEATURES_WITH_MODE_SETTINGS:
                item['settings'] = common.MODE_SETTINGS
            excepted_response['mode']['features'].append(item)

    assert response.json() == excepted_response


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            [
                mode_rules.Patch(
                    'orders',
                    features={'tags': {'assign': ['tag1']}},
                    stops_at=datetime.datetime.fromisoformat(
                        '2019-05-01T06:00:00+00:00',
                    ),
                    rule_id='11111111111111111111111111111111',
                ),
                mode_rules.Patch(
                    'orders',
                    features={'reposition': {'profile': 'orders'}},
                    is_canceled=True,
                    starts_at=datetime.datetime.fromisoformat(
                        '2019-05-01T04:00:00+00:00',
                    ),
                    stops_at=datetime.datetime.fromisoformat(
                        '2019-05-01T06:00:00+00:00',
                    ),
                    rule_id='22222222222222222222222222222222',
                ),
            ],
        ),
    ],
)
@pytest.mark.now(_NOW)
async def test_no_match_canceled_rules(
        taxi_driver_mode_subscription, mockserver, mocked_time, pgsql,
):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return common.mode_history_response(
            request, 'orders', mocked_time, mode_settings=common.MODE_SETTINGS,
        )

    response = await taxi_driver_mode_subscription.get(
        'v1/mode/info', params=REQUEST_PARAMS, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200
    assert response.json() == {
        'mode': {
            'name': 'orders',
            'started_at': mocked_time.now().strftime(
                '%Y-%m-%dT%H:%M:%S+00:00',
            ),
            'features': [{'name': 'tags'}],
        },
    }

    # swap canceled value for orders rules
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'UPDATE config.mode_rules SET canceled = not canceled WHERE '
        'mode_id = (SELECT id FROM config.modes WHERE name = \'orders\')',
    )

    await taxi_driver_mode_subscription.invalidate_caches()
    response = await taxi_driver_mode_subscription.get(
        'v1/mode/info', params=REQUEST_PARAMS, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200
    assert response.json() == {
        'mode': {
            'name': 'orders',
            'started_at': mocked_time.now().strftime(
                '%Y-%m-%dT%H:%M:%S+00:00',
            ),
            'features': [{'name': 'reposition'}],
        },
    }
