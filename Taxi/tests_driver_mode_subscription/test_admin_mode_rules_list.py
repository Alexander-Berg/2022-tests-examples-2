# pylint: disable=C0302
import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules

REQUEST_HEADER = {'X-Ya-Service-Ticket': common.MOCK_TICKET}


def make_time_range(start: str, end: str):
    return {'start': start, 'end': end}


def make_filters(
        time_range: Optional[Dict[str, str]] = None,
        rule_id: Optional[str] = None,
        work_modes: Optional[List[str]] = None,
        billing_modes: Optional[List[str]] = None,
        billing_mode_rules: Optional[List[str]] = None,
        display_modes: Optional[List[str]] = None,
        display_profiles: Optional[List[str]] = None,
        offers_groups: Optional[List[str]] = None,
        offers_groups_constraint: Optional[Dict[str, Any]] = None,
        work_mode_classes_constraint: Optional[Dict[str, Any]] = None,
        features: Optional[List[str]] = None,
        is_canceled: Optional[bool] = None,
):
    result: Dict[str, Any] = {}
    if time_range:
        result['time_range'] = time_range
    if rule_id:
        result['rule_id'] = rule_id
    if work_modes:
        result['work_modes'] = work_modes
    if billing_modes:
        result['billing_modes'] = billing_modes
    if billing_mode_rules:
        result['billing_mode_rules'] = billing_mode_rules
    if display_modes:
        result['display_modes'] = display_modes
    if display_profiles:
        result['display_profiles'] = display_profiles
    if offers_groups:
        result['offers_groups'] = offers_groups
    if offers_groups_constraint:
        result['offers_groups_constraint'] = offers_groups_constraint
    if work_mode_classes_constraint:
        result['work_mode_classes_constraint'] = work_mode_classes_constraint
    if features:
        result['features'] = features
    if is_canceled is not None:
        result['is_canceled'] = is_canceled

    return result


def compact_rules_data(response_json: Dict[str, Any]):
    return list(
        map(
            lambda x: {
                'work_mode': x['rule_data']['work_mode'],
                'starts_at': x['rule_data']['starts_at'],
            },
            response_json['rules'],
        ),
    )


def make_compact_data(work_mode: str, starts_at: Optional[str] = None):
    result: Dict[str, Any] = {'work_mode': work_mode}
    if starts_at:
        result['starts_at'] = starts_at
    return result


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_name='custom_orders',
                    condition={'any_of': ['tag3']},
                    drafts=[
                        mode_rules.Draft('1', 'create'),
                        mode_rules.Draft('2', 'close'),
                    ],
                ),
                mode_rules.Patch(
                    rule_name='all_features',
                    features={
                        'driver_fix': {'roles': [{'name': 'role1'}]},
                        'tags': {'assign': ['driver_fix']},
                        'reposition': {'profile': 'reposition_profile'},
                        'active_transport': {'type': 'bicycle'},
                        'geobooking': {},
                    },
                    is_canceled=True,
                ),
            ],
            mode_classes=[
                mode_rules.ModeClass('driver_fix_class', ['all_features']),
            ],
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_mode_rules_fulldata(taxi_driver_mode_subscription):
    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/list', json={}, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {
        'rules': [
            {
                'is_canceled': True,
                'rule_data': {
                    'billing_settings': {
                        'mode': 'some_billing_mode',
                        'mode_rule': 'some_billing_mode_rule',
                    },
                    'display_settings': {
                        'mode': 'orders_type',
                        'profile': 'all_features',
                    },
                    # order from db is preserved
                    'features': [
                        {
                            'name': 'driver_fix',
                            'settings': {'roles': [{'name': 'role1'}]},
                        },
                        {
                            'name': 'tags',
                            'settings': {'assign': ['driver_fix']},
                        },
                        {
                            'name': 'reposition',
                            'settings': {'profile': 'reposition_profile'},
                        },
                        {
                            'name': 'active_transport',
                            'settings': {'type': 'bicycle'},
                        },
                        {'name': 'geobooking', 'settings': {}},
                    ],
                    'offers_group': 'taxi',
                    'starts_at': '1970-01-01T00:00:00+00:00',
                    'work_mode': 'all_features',
                    'work_mode_class': 'driver_fix_class',
                },
                'rule_id': '89e290c1a0e5d75d14bbf7cc54270e48',
                'schema_version': 1,
            },
            {
                'drafts': [
                    {'id': '1', 'action': 'create'},
                    {'id': '2', 'action': 'close'},
                ],
                'is_canceled': False,
                'rule_data': {
                    'billing_settings': {
                        'mode': 'some_billing_mode',
                        'mode_rule': 'some_billing_mode_rule',
                    },
                    'conditions': {'condition': {'any_of': ['tag3']}},
                    'display_settings': {
                        'mode': 'orders_type',
                        'profile': 'custom_orders',
                    },
                    'offers_group': 'taxi',
                    'starts_at': '1970-01-01T00:00:00+00:00',
                    'work_mode': 'custom_orders',
                },
                'rule_id': 'ba3da1a93fdb58d8d1d93194e2687e85',
                'schema_version': 1,
            },
            {
                'is_canceled': False,
                'rule_data': {
                    'billing_settings': {
                        'mode': 'driver_fix',
                        'mode_rule': 'driver_fix_billing_mode_rule',
                    },
                    'display_settings': {
                        'mode': 'driver_fix_type',
                        'profile': 'driver_fix',
                    },
                    'features': [{'name': 'driver_fix', 'settings': {}}],
                    'offers_group': 'taxi',
                    'starts_at': '1970-01-01T00:00:00+00:00',
                    'work_mode': 'driver_fix',
                },
                'rule_id': 'adb1a47b6534d0624a4493088150eb5b',
                'schema_version': 1,
            },
            {
                'is_canceled': False,
                'rule_data': {
                    'billing_settings': {
                        'mode': 'some_billing_mode',
                        'mode_rule': 'some_billing_mode_rule',
                    },
                    'display_settings': {
                        'mode': 'orders_type',
                        'profile': 'orders',
                    },
                    'offers_group': 'taxi',
                    'starts_at': '1970-01-01T00:00:00+00:00',
                    'work_mode': 'orders',
                },
                'rule_id': '065a0bc31b38cb5e449c2e31cd0a3deb',
                'schema_version': 1,
            },
            {
                'is_canceled': False,
                'rule_data': {
                    'billing_settings': {
                        'mode': 'uberdriver_billing_mode',
                        'mode_rule': 'uberdriver_billing_mode_rule',
                    },
                    'display_settings': {
                        'mode': 'uberdriver_type',
                        'profile': 'uberdriver',
                    },
                    'starts_at': '1970-01-01T00:00:00+00:00',
                    'work_mode': 'uberdriver',
                },
                'rule_id': '70666be9fe063315d456e55c1bf629ca',
                'schema_version': 1,
            },
        ],
    }


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_name='aorders',
                    starts_at=datetime.datetime.fromisoformat(
                        '1970-01-01T00:00:00+00:00',
                    ),
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-05-01T05:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(rule_name='borders'),
                mode_rules.Patch(rule_name='corders'),
                mode_rules.Patch(
                    rule_name='aorders',
                    starts_at=datetime.datetime.fromisoformat(
                        '2020-05-01T05:00:00+00:00',
                    ),
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-05-01T06:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='aorders',
                    starts_at=datetime.datetime.fromisoformat(
                        '2020-05-01T06:00:00+00:00',
                    ),
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2019-05-01T1:00:00+0300')
async def test_admin_mode_rules_default_sort(taxi_driver_mode_subscription):
    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/list',
        json={
            'filters': make_filters(
                make_time_range(
                    '1970-01-01T00:00:00+00:00', '2020-05-03T00:00:00+00:00',
                ),
            ),
        },
        headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    compact_data = compact_rules_data(response.json())

    assert compact_data == [
        make_compact_data('aorders', '2020-05-01T06:00:00+00:00'),
        make_compact_data('aorders', '2020-05-01T05:00:00+00:00'),
        make_compact_data('aorders', '1970-01-01T00:00:00+00:00'),
        make_compact_data('borders', '1970-01-01T00:00:00+00:00'),
        make_compact_data('corders', '1970-01-01T00:00:00+00:00'),
        make_compact_data('custom_orders', '1970-01-01T00:00:00+00:00'),
        make_compact_data('driver_fix', '1970-01-01T00:00:00+00:00'),
        make_compact_data('orders', '1970-01-01T00:00:00+00:00'),
        make_compact_data('uberdriver', '1970-01-01T00:00:00+00:00'),
    ]


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_name='orders',
                    stops_at=datetime.datetime.fromisoformat(
                        '2019-05-01T05:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='driver_fix',
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-05-01T05:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='driver_fix',
                    starts_at=datetime.datetime.fromisoformat(
                        '2020-06-01T00:00:00+00:00',
                    ),
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-07-01T05:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='custom_orders',
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-01-01T05:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='custom_orders',
                    starts_at=datetime.datetime.fromisoformat(
                        '2020-01-01T05:00:00+00:00',
                    ),
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-02-01T05:00:00+00:00',
                    ),
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'time_range, expected_rules',
    [
        pytest.param(
            make_time_range(
                '2020-01-01T07:00:00+03:00', '2020-01-01T06:00:00+00:00',
            ),
            [
                make_compact_data(
                    'custom_orders', '2020-01-01T05:00:00+00:00',
                ),
                make_compact_data(
                    'custom_orders', '1970-01-01T00:00:00+00:00',
                ),
                make_compact_data('driver_fix', '1970-01-01T00:00:00+00:00'),
                make_compact_data('uberdriver', '1970-01-01T00:00:00+00:00'),
            ],
            id='check timezone handling',
        ),
        pytest.param(
            make_time_range(
                '2020-04-01T05:00:00+00:00', '2020-05-01T00:00:00+00:00',
            ),
            [
                make_compact_data('driver_fix', '1970-01-01T00:00:00+00:00'),
                make_compact_data('uberdriver', '1970-01-01T00:00:00+00:00'),
            ],
            id='exclude orders in left of interval',
        ),
        pytest.param(
            make_time_range(
                '2020-05-21T05:00:00+00:00', '2020-06-01T00:00:00+00:00',
            ),
            [make_compact_data('uberdriver', '1970-01-01T00:00:00+00:00')],
            id='exclude driver_fix at interval end',
        ),
        pytest.param(
            make_time_range(
                '2020-01-01T01:00:00+00:00', '2020-03-01T05:00:00+00:00',
            ),
            [
                make_compact_data(
                    'custom_orders', '2020-01-01T05:00:00+00:00',
                ),
                make_compact_data(
                    'custom_orders', '1970-01-01T00:00:00+00:00',
                ),
                make_compact_data('driver_fix', '1970-01-01T00:00:00+00:00'),
                make_compact_data('uberdriver', '1970-01-01T00:00:00+00:00'),
            ],
            id=(
                'exclude driver_fix in right of interval '
                'and include custom_orders inside'
            ),
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_mode_rules_filter_by_period(
        taxi_driver_mode_subscription,
        time_range: Dict[str, Any],
        expected_rules: List[Dict[str, Any]],
):
    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/list',
        json={'filters': make_filters(time_range)},
        headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    compact_data = compact_rules_data(response.json())

    assert compact_data == expected_rules


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_name='driver_fix',
                    rule_id='11111111111111111111111111111111',
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_mode_rules_filter_by_rule_id(
        taxi_driver_mode_subscription,
):
    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/list',
        json={
            'filters': make_filters(
                rule_id='11111111111111111111111111111111',
            ),
        },
        headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    compact_data = compact_rules_data(response.json())

    assert compact_data == [
        make_compact_data('driver_fix', '1970-01-01T00:00:00+00:00'),
    ]


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_name='orders',
                    stops_at=datetime.datetime.fromisoformat(
                        '2019-05-01T05:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='driver_fix',
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-01-01T05:00:00+00:00',
                    ),
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2020-05-01T12:00:00+0300')
async def test_admin_mode_rules_default_filter(taxi_driver_mode_subscription):
    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/list', json={}, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    compact_data = compact_rules_data(response.json())

    assert compact_data == [
        make_compact_data('custom_orders', '1970-01-01T00:00:00+00:00'),
        make_compact_data('uberdriver', '1970-01-01T00:00:00+00:00'),
    ]


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(rule_name='aorders'),
                mode_rules.Patch(rule_name='borders'),
                mode_rules.Patch(rule_name='corders'),
                mode_rules.Patch(rule_name='dorders'),
            ],
        ),
    ],
)
@pytest.mark.now('2020-05-01T12:00:00+0300')
async def test_admin_mode_rules_limit_cursor(taxi_driver_mode_subscription):
    expected_data: List[List[Dict[str, str]]] = [
        [
            make_compact_data('aorders', '1970-01-01T00:00:00+00:00'),
            make_compact_data('borders', '1970-01-01T00:00:00+00:00'),
            make_compact_data('corders', '1970-01-01T00:00:00+00:00'),
        ],
        [
            make_compact_data('custom_orders', '1970-01-01T00:00:00+00:00'),
            make_compact_data('dorders', '1970-01-01T00:00:00+00:00'),
            make_compact_data('driver_fix', '1970-01-01T00:00:00+00:00'),
        ],
        [
            make_compact_data('orders', '1970-01-01T00:00:00+00:00'),
            make_compact_data('uberdriver', '1970-01-01T00:00:00+00:00'),
        ],
    ]

    expected_cursor: List[Optional[str]] = [
        '{"offset":3}',
        '{"offset":6}',
        None,
    ]

    cursor: Optional[str] = None

    for i in range(0, 3):
        request_params = {'limit': 3}
        if cursor:
            request_params['cursor'] = cursor

        response = await taxi_driver_mode_subscription.post(
            'v1/admin/mode_rules/list',
            json=request_params,
            headers=REQUEST_HEADER,
        )

        assert response.status_code == 200

        response_data = response.json()

        compact_data = compact_rules_data(response_data)

        assert compact_data == expected_data[i]

        next_cursor = response_data.get('next_cursor')

        assert next_cursor == expected_cursor[i]

        cursor = next_cursor


@pytest.mark.parametrize(
    'rule_id',
    [
        'helloworldhelloworldhelloworldhe',
        '444444',
        'feffffff-fdfe-ffff-fffd-fefffffffdfe',
        '000000000000400000000000000000001',
        '000000000000000h0000000000000000',
        '0123456789abcdefgABCDEF000000000',
        '0123456789abcdefABCDEFG000000000',
        '0123456789abcdefABCDEF0000000000',
        '00000000000000000000000000000000',
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_mode_rules_validate_rule_id(
        taxi_driver_mode_subscription, rule_id: str,
):
    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/list',
        json={'filters': make_filters(rule_id=rule_id)},
        headers=REQUEST_HEADER,
    )
    assert response.status_code == 200
    assert response.json() == {'rules': []}


_RULE_ID1 = '11111111111111111111111111111111'
_RULE_ID2 = '22222222222222222222222222222222'
_RULE_ID3 = '33333333333333333333333333333333'


@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_id=_RULE_ID1,
                    rule_name='orders',
                    billing_mode='billing_mode1',
                    billing_mode_rule='billing_mode_rule1',
                    display_mode='display_mode1',
                    display_profile='display_profile1',
                    offers_group='offers_group1',
                    features={'reposition': {}, 'driver_fix': {}},
                    is_canceled=True,
                ),
                mode_rules.Patch(
                    rule_id=_RULE_ID2,
                    rule_name='custom_orders1',
                    billing_mode='billing_mode2',
                    billing_mode_rule='billing_mode_rule2',
                    display_mode='display_mode2',
                    display_profile='display_profile2',
                    offers_group='offers_group2',
                    features={'reposition': {}},
                ),
                mode_rules.Patch(
                    rule_id=_RULE_ID3,
                    rule_name='custom_orders2',
                    billing_mode='billing_mode3',
                    billing_mode_rule='billing_mode_rule3',
                    display_mode='display_mode3',
                    display_profile='display_profile3',
                    offers_group='offers_group3',
                    features={
                        'driver_fix': {},
                        'active_transport': {'type': 'bike'},
                    },
                ),
            ],
            rules={},
            mode_classes=[mode_rules.ModeClass('order_class', ['orders'])],
        ),
    ],
)
@pytest.mark.parametrize(
    'filters, expected_rules',
    [
        pytest.param(
            make_filters(work_modes=['orders', 'custom_orders1']),
            [_RULE_ID1, _RULE_ID2],
            id='work_mode',
        ),
        pytest.param(
            make_filters(billing_modes=['billing_mode1', 'billing_mode3']),
            [_RULE_ID1, _RULE_ID3],
            id='billing_mode',
        ),
        pytest.param(
            make_filters(
                billing_mode_rules=[
                    'billing_mode_rule2',
                    'billing_mode_rule3',
                ],
            ),
            [_RULE_ID2, _RULE_ID3],
            id='billing_mode_rule',
        ),
        pytest.param(
            make_filters(display_modes=['display_mode1', 'display_mode2']),
            [_RULE_ID1, _RULE_ID2],
            id='display_mode',
        ),
        pytest.param(
            make_filters(
                display_profiles=['display_profile1', 'display_profile3'],
            ),
            [_RULE_ID1, _RULE_ID3],
            id='display_profile',
        ),
        pytest.param(
            make_filters(offers_groups=['offers_group3', 'offers_group2']),
            [_RULE_ID2, _RULE_ID3],
            id='offers_group_old',
        ),
        pytest.param(
            make_filters(
                offers_groups_constraint={
                    'values': ['offers_group3', 'offers_group2'],
                },
            ),
            [_RULE_ID2, _RULE_ID3],
            id='offers_group_list',
        ),
        pytest.param(
            make_filters(offers_groups_constraint={'has_value': False}),
            [_RULE_ID1],
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        patches=[
                            mode_rules.Patch('uberdriver', rule_id=_RULE_ID1),
                        ],
                    ),
                ),
            ],
            id='offers_group_empty',
        ),
        pytest.param(
            make_filters(offers_groups_constraint={'has_value': True}),
            [_RULE_ID1, _RULE_ID2, _RULE_ID3],
            id='offers_group_exists',
        ),
        pytest.param(
            make_filters(features=['reposition']),
            [_RULE_ID1, _RULE_ID2],
            id='feature',
        ),
        pytest.param(
            make_filters(features=['reposition', 'active_transport']),
            [_RULE_ID1, _RULE_ID2, _RULE_ID3],
            id='two_features',
        ),
        pytest.param(
            make_filters(features=['missing_feature']),
            [],
            id='missing_feature',
        ),
        pytest.param(
            make_filters(is_canceled=True), [_RULE_ID1], id='canceled_true',
        ),
        pytest.param(
            make_filters(is_canceled=False),
            [_RULE_ID2, _RULE_ID3],
            id='canceled_false',
        ),
        pytest.param(
            make_filters(work_mode_classes_constraint={'has_value': True}),
            [_RULE_ID1],
            id='mode_class_exists',
        ),
        pytest.param(
            make_filters(work_mode_classes_constraint={'has_value': False}),
            [_RULE_ID2, _RULE_ID3],
            id='mode_class_empty',
        ),
        pytest.param(
            make_filters(
                work_mode_classes_constraint={
                    'values': ['order_class', 'some_class'],
                },
            ),
            [_RULE_ID1],
            id='mode_class_list',
        ),
    ],
)
async def test_admin_mode_rules_filters(
        taxi_driver_mode_subscription,
        mode_rules_data,
        filters: Dict[str, Any],
        expected_rules: List[str],
):
    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/list',
        json={'filters': filters},
        headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    rules_found = sorted(
        list(map(lambda rule: rule['rule_id'], response.json()['rules'])),
    )
    assert rules_found == expected_rules


_START_TIME_MINUS_2H = datetime.datetime.fromisoformat(
    '2020-01-01T00:00:00+03:00',
)
_START_TIME_MINUS_1H = datetime.datetime.fromisoformat(
    '2020-01-01T01:00:00+03:00',
)
_START_TIME = datetime.datetime.fromisoformat('2020-01-01T02:00:00+03:00')
_STOP_TIME = datetime.datetime.fromisoformat('2020-01-01T03:00:00+03:00')
_STOP_TIME_PLUS_1H = datetime.datetime.fromisoformat(
    '2020-01-01T04:00:00+03:00',
)
_STOP_TIME_PLUS_2H = datetime.datetime.fromisoformat(
    '2020-01-01T05:00:00+03:00',
)


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            # does not intersect
            mode_rules.Patch(
                rule_name='test_rule',
                starts_at=_START_TIME_MINUS_2H,
                stops_at=_START_TIME_MINUS_1H,
            ),
            # stop time equals new rule start time
            mode_rules.Patch(
                rule_name='test_rule',
                starts_at=_START_TIME_MINUS_1H,
                stops_at=_START_TIME,
            ),
            # intersects
            mode_rules.Patch(
                rule_name='test_rule',
                starts_at=_START_TIME,
                stops_at=_STOP_TIME,
                rule_id=_RULE_ID1,
            ),
            # start time touches new rule stop time if it exists
            mode_rules.Patch(
                rule_name='test_rule',
                starts_at=_STOP_TIME,
                stops_at=_STOP_TIME_PLUS_1H,
                rule_id=_RULE_ID2,
            ),
            # does not intersect new rule if its stop time exists
            mode_rules.Patch(
                rule_name='test_rule',
                starts_at=_STOP_TIME_PLUS_1H,
                clear_stops_at=True,
                rule_id=_RULE_ID3,
            ),
            # wrong work mode
            mode_rules.Patch(
                rule_name='orders', starts_at=_START_TIME, stops_at=_STOP_TIME,
            ),
            # canceled
            mode_rules.Patch(
                rule_name='orders',
                starts_at=_START_TIME,
                stops_at=_STOP_TIME,
                is_canceled=True,
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'new_stop_time, expected_rules',
    [
        pytest.param(_STOP_TIME, [_RULE_ID1], id='new_rule_finite'),
        pytest.param(
            None, [_RULE_ID1, _RULE_ID2, _RULE_ID3], id='new_rule_infinite',
        ),
    ],
)
async def test_find_intersecting_rules(
        taxi_driver_mode_subscription,
        mode_rules_data,
        new_stop_time: Optional[datetime.datetime],
        expected_rules: List[str],
):
    time_range = {'start': _START_TIME.isoformat()}
    if new_stop_time:
        time_range['end'] = new_stop_time.isoformat()

    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/list',
        json={
            'filters': make_filters(
                time_range=time_range,
                work_modes=['test_rule'],
                is_canceled=False,
            ),
        },
        headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    rules_found = sorted(
        list(map(lambda rule: rule['rule_id'], response.json()['rules'])),
    )
    assert rules_found == expected_rules


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_name='custom_orders',
                    features={
                        'driver_fix_old': {'roles': [{'name': 'role1'}]},
                        'tags_new': {'upload': ['driver_fix']},
                        'reposition': {'profile': 'reposition_profile'},
                        'active_transport': {'type': 'bicycle'},
                        'newbooking': {},
                    },
                    is_canceled=True,
                    schema_version=777,
                ),
                mode_rules.Patch(
                    rule_name='orders',
                    stops_at=datetime.datetime.fromisoformat(
                        '2019-05-01T05:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='uberdriver',
                    stops_at=datetime.datetime.fromisoformat(
                        '2019-05-01T05:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='driver_fix',
                    stops_at=datetime.datetime.fromisoformat(
                        '2019-05-01T05:00:00+00:00',
                    ),
                ),
            ],
            mode_classes=[mode_rules.ModeClass('old_rules', ['db_features'])],
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_admin_mode_rules_no_conversion_from_db(
        taxi_driver_mode_subscription,
):
    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/list', json={}, headers=REQUEST_HEADER,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {
        'rules': [
            {
                'is_canceled': True,
                'rule_data': {
                    'billing_settings': {
                        'mode': 'some_billing_mode',
                        'mode_rule': 'some_billing_mode_rule',
                    },
                    'display_settings': {
                        'mode': 'orders_type',
                        'profile': 'custom_orders',
                    },
                    'features': [
                        {
                            'name': 'driver_fix_old',
                            'settings': {'roles': [{'name': 'role1'}]},
                        },
                        {
                            'name': 'tags_new',
                            'settings': {'upload': ['driver_fix']},
                        },
                        {
                            'name': 'reposition',
                            'settings': {'profile': 'reposition_profile'},
                        },
                        {
                            'name': 'active_transport',
                            'settings': {'type': 'bicycle'},
                        },
                        {'name': 'newbooking', 'settings': {}},
                    ],
                    'offers_group': 'taxi',
                    'starts_at': '1970-01-01T00:00:00+00:00',
                    'work_mode': 'custom_orders',
                },
                'rule_id': 'ba3da1a93fdb58d8d1d93194e2687e85',
                'schema_version': 777,
            },
        ],
    }
