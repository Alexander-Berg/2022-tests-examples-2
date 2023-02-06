import json

import pytest

from tests_driver_fix import common


class TagsContext:
    def __init__(self):
        self.reset()

    def reset(self):
        self.calls_count = 0
        self.expected_tag_chunks = []


SUBVENTION_RULE_MOCK = {
    'tariff_zones': ['moscow'],
    'geoareas': ['subv_zone1', 'subv_zone2'],
    'status': 'enabled',
    'start': '2018-08-01T12:59:23.231000+00:00',
    'end': '2018-08-10T12:59:23.231000+00:00',
    'type': 'driver_fix',
    'is_personal': False,
    'taxirate': 'TAXIRATE-21',
    'subvention_rule_id': '_id/1',
    'cursor': '1',
    'tags': [],
    'time_zone': {'id': 'Europe/Moscow', 'offset': '+03'},
    'currency': 'RUB',
    'updated': '2018-08-01T12:59:23.231000+00:00',
    'visible_to_driver': True,
    'week_days': ['mon'],
    'hours': [],
    'log': [],
    'profile_payment_type_restrictions': 'online',
    'profile_tariff_classes': ['business', 'econom'],
    'rates': [
        {'week_day': 'mon', 'start': '00:00', 'rate_per_minute': '5.0'},
        {'week_day': 'mon', 'start': '05:00', 'rate_per_minute': '5.5'},
        {'week_day': 'mon', 'start': '13:00', 'rate_per_minute': '6.0'},
        {'week_day': 'tue', 'start': '01:02', 'rate_per_minute': '4.8'},
        {'week_day': 'wed', 'start': '12:00', 'rate_per_minute': '4.5'},
        {'week_day': 'thu', 'start': '12:00', 'rate_per_minute': '4.5'},
        {'week_day': 'fri', 'start': '12:00', 'rate_per_minute': '4.5'},
        {'week_day': 'sat', 'start': '12:00', 'rate_per_minute': '4.5'},
        {'week_day': 'sun', 'start': '12:00', 'rate_per_minute': '4.5'},
    ],
    'commission_rate_if_fraud': '90.90',
}

TARIFFS_TRANSLATION_MAP = {
    'econom': 'econom',
    'comfort': 'business',
    'bussines': 'vip',
    'miniven': 'minivan',
    'touring': 'universal',
    'comfortplus': 'comfortplus',
    # "comfortplus": "business2",
    'express': 'express',
    'pool': 'pool',
    'start': 'start',
    'standard': 'standart',
    'child_tariff': 'child_tariff',
    'ultimate': 'ultimate',
    'mkk': 'mkk',
    'selfdriving': 'selfdriving',
    'maybach': 'maybach',
    'demostand': 'demostand',
    'promo': 'promo',
    'premium_van': 'premium_van',
    'premium_suv': 'premium_suv',
    'suv': 'suv',
    'personal_driver': 'personal_driver',
    'cargo': 'cargo',
    'night': 'night',
    'mkk_antifraud': 'mkk_antifraud',
}


@pytest.mark.parametrize(
    'on_start, check_enabled', [(True, False), (True, True), (False, False)],
)
@pytest.mark.parametrize(
    'subvention_rule_id, response_code, error_code, tags',
    [
        (None, 400, 'FAILED_TO_GET_SUBVENTION_RULE_ID', {'common': ['t1']}),
        ('missing_rule', 404, 'SUBVENTION_RULE_NOT_FOUND', {'common': ['t1']}),
        ('multi_rule', 500, None, {'common': ['t1']}),
        ('empty_zone_rule', 500, None, {'common': ['t1']}),
        ('multi_zone_rule', 500, None, {'common': ['t1']}),
        ('normal_rule', 200, None, {}),
        ('normal_rule', 200, None, {'spb': ['t1']}),
        ('normal_rule', 200, None, {'common': ['t1']}),
        ('normal_rule', 200, None, {'moscow': ['t1']}),
        ('normal_rule', 200, None, {'common': ['t1'], 'moscow': ['t2']}),
    ],
)
async def test_on_start_on_stop_basic(
        taxi_driver_fix,
        stq,
        on_start,
        check_enabled,
        subvention_rule_id,
        response_code,
        error_code,
        tags,
        mockserver,
        taxi_config,
):
    taxi_config.set_values(
        dict(
            DRIVER_FIX_STQ_CONFIG=[
                {
                    'enabled': check_enabled,
                    'reschedule_timeshift_ms': 2000,
                    'schedule_timeshift_ms': 2000,
                    'check_settings': {'check_type': 'subvention_rule'},
                },
                {
                    'enabled': check_enabled,
                    'reschedule_timeshift_ms': 2000,
                    'schedule_timeshift_ms': 2000,
                    'check_settings': {'check_type': 'required_tags'},
                },
            ],
        ),
    )

    if tags:
        common_tags = tags.pop('common', None)
        if common_tags:
            taxi_config.set_values(
                dict(
                    DRIVER_FIX_DRIVER_TAGS={
                        'common_tags': {'tags_list': common_tags},
                    },
                ),
            )
        if tags:
            additional_tags_by_zone = {
                key: {'tags_list': value} for key, value in tags.items()
            }
            taxi_config.set_values(
                dict(
                    DRIVER_FIX_DRIVER_TAGS={
                        'additional_tags_by_zone': additional_tags_by_zone,
                    },
                ),
            )

    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        data = json.loads(request.get_data())
        assert data['merge_policy'] == 'append' if on_start else 'remove'
        assert data['tags']
        return {'status': 'ok'}

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _v1_rules_select(request):
        data = json.loads(request.get_data())
        rule_id = data['rule_ids'][0]
        subventions = []
        if rule_id != 'missing_rule':
            subventions.append(dict(SUBVENTION_RULE_MOCK))
            if rule_id == 'multi_rule':
                subventions.append(dict(SUBVENTION_RULE_MOCK))
            elif rule_id == 'empty_zone_rule':
                subventions[0]['tariff_zones'] = []
            elif rule_id == 'multi_zone_rule':
                subventions[0]['tariff_zones'] = ['moscow', 'spb']
        return {'subventions': subventions}

    mode_settings = {'shift_close_time': '03:00:00+03:00'}
    if subvention_rule_id:
        mode_settings['rule_id'] = subvention_rule_id

    response = await taxi_driver_fix.post(
        'v1/mode/on_start/' if on_start else 'v1/mode/on_stop/',
        json={
            'driver_profile_id': 'id',
            'park_id': 'id',
            'mode_settings': mode_settings,
        },
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == response_code
    if error_code:
        response_body = response.json()
        assert response_body['code'] == error_code
        assert response_body.get('message')
        assert stq.driver_fix.times_called == 0
    elif response_code != 500 and on_start and check_enabled:
        sync_cfg = taxi_config.get('DRIVER_FIX_STQ_CONFIG')
        required_syncs = 0
        for settings_for_mode in sync_cfg:
            if settings_for_mode['enabled']:
                required_syncs += 1
        assert stq.driver_fix.times_called == required_syncs
    else:
        assert stq.driver_fix.times_called == 0


@pytest.mark.parametrize(
    'enable_online_time_tags, check_enabled,'
    'zone_tags_config, common_tags_config, remove_tags',
    (
        (False, False, None, None, None),
        (False, True, None, None, None),
        (True, False, None, None, None),
        (True, True, None, None, None),
        (
            True,
            True,
            {600: {'add_tags': ['t0'], 'remove_tags': []}},
            None,
            ['t0'],
        ),
        (
            True,
            True,
            {600: {'add_tags': ['t0'], 'remove_tags': ['t0']}},
            None,
            None,
        ),
        (
            True,
            True,
            {600: {'add_tags': [], 'remove_tags': ['t0']}},
            None,
            None,
        ),
        (
            True,
            True,
            {600: {'add_tags': [], 'remove_tags': ['t0']}},
            {600: {'add_tags': ['t0'], 'remove_tags': []}},
            None,
        ),
        (
            True,
            True,
            {
                600: {'add_tags': ['t0_0'], 'remove_tags': ['t0_1']},
                601: {'add_tags': ['t1_1'], 'remove_tags': ['t1_1']},
            },
            {
                600: {'add_tags': ['t0_2'], 'remove_tags': ['t0_1']},
                601: {'add_tags': ['t1_3'], 'remove_tags': ['t1_4']},
            },
            ['t0_0', 't0_2', 't1_3'],
        ),
    ),
)
async def test_on_stop_online_time_tags(
        taxi_driver_fix,
        stq,
        mockserver,
        taxi_config,
        enable_online_time_tags,
        check_enabled,
        zone_tags_config,
        common_tags_config,
        remove_tags,
):
    taxi_config.set_values(
        dict(
            DRIVER_FIX_ONLINE_TIME_TAGS_ENABLED=enable_online_time_tags,
            DRIVER_FIX_STQ_CONFIG=[
                {
                    'enabled': check_enabled,
                    'reschedule_timeshift_ms': 2000,
                    'schedule_timeshift_ms': 2000,
                    'check_settings': {'check_type': 'online_time_tags'},
                },
            ],
        ),
    )

    tags_config = common.generate_online_time_tags_config(
        'moscow', zone_tags_config, common_tags_config,
    )

    if tags_config:
        taxi_config.set_values(dict(DRIVER_FIX_DRIVER_TAGS=tags_config))

    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        data = json.loads(request.get_data())
        assert data['merge_policy'] == 'remove'
        assert data['tags']
        return {'status': 'ok'}

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _v1_rules_select(request):
        return {'subventions': [SUBVENTION_RULE_MOCK]}

    mode_settings = {
        'shift_close_time': '03:00:00+03:00',
        'rule_id': 'normal_rule_id',
    }

    response = await taxi_driver_fix.post(
        'v1/mode/on_stop/',
        json={
            'driver_profile_id': 'id',
            'park_id': 'id',
            'mode_settings': mode_settings,
        },
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200
    assert stq.driver_fix.times_called == bool(remove_tags)
    if stq.driver_fix.times_called:
        kwargs = stq.driver_fix.next_call()['kwargs']
        check_settings_str = kwargs['check_settings']
        check_settings = json.loads(check_settings_str)['check_settings']
        assert check_settings['check_type'] == 'online_time_tags'
        assert not check_settings['add_tags']
        assert check_settings['remove_tags'] == remove_tags


@pytest.mark.config(
    DRIVER_FIX_STQ_CONFIG=[
        {
            'enabled': True,
            'reschedule_timeshift_ms': 2000,
            'schedule_timeshift_ms': 2000,
            'check_settings': {'check_type': 'subvention_rule'},
        },
        {
            'enabled': True,
            'reschedule_timeshift_ms': 2000,
            'schedule_timeshift_ms': 2000,
            'check_settings': {'check_type': 'required_tags'},
        },
    ],
)
@pytest.mark.parametrize('enable', [True, False])
async def test_on_start_on_stop_missing_mode_settings(
        taxi_driver_fix, stq, mockserver, enable,
):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _v1_rules_select(request):
        pass

    @mockserver.json_handler('/driver-categories-api/v2/drivers/categories')
    def _v2_drivers_categories(request):
        pass

    response = await taxi_driver_fix.post(
        'v1/mode/on_start/' if enable else 'v1/mode/on_stop/',
        json={'driver_profile_id': 'id', 'park_id': 'id'},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 400
    response_body = response.json()
    assert (
        response_body['code']
        == 'FAILED_TO_GET_SUBVENTION_RULE_ID_NO_MODE_SETTINGS'
    )
    assert response_body.get('message')
    assert stq.driver_fix.times_called == 0


@pytest.mark.config(
    DRIVER_FIX_DRIVER_TAGS={'common_tags': {'tags_list': ['t1']}},
    DRIVER_FIX_STQ_CONFIG=[
        {
            'enabled': True,
            'reschedule_timeshift_ms': 2000,
            'schedule_timeshift_ms': 2000,
            'check_settings': {'check_type': 'subvention_rule'},
        },
        {
            'enabled': True,
            'reschedule_timeshift_ms': 2000,
            'schedule_timeshift_ms': 2000,
            'check_settings': {'check_type': 'required_tags'},
        },
    ],
)
@pytest.mark.parametrize('enable', [True, False])
async def test_on_start_on_stop_tags_fail(
        taxi_driver_fix, stq, enable, mockserver,
):
    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        pass

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _v1_rules_select(request):
        return {'subventions': [SUBVENTION_RULE_MOCK]}

    response = await taxi_driver_fix.post(
        'v1/mode/on_start/' if enable else 'v1/mode/on_stop/',
        json={
            'driver_profile_id': 'id',
            'park_id': 'id',
            'mode_settings': {
                'rule_id': 'normal_rule',
                'shift_close_time': '03:00:00+03:00',
            },
        },
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 500
    assert stq.driver_fix.times_called == 0


@pytest.mark.config(
    DRIVER_FIX_DRIVER_TAGS={'common_tags': {'tags_list': ['t1']}},
    DRIVER_FIX_STQ_CONFIG=[
        {
            'enabled': True,
            'reschedule_timeshift_ms': 2000,
            'schedule_timeshift_ms': 2000,
            'check_settings': {'check_type': 'subvention_rule'},
        },
        {
            'enabled': True,
            'reschedule_timeshift_ms': 2000,
            'schedule_timeshift_ms': 2000,
            'check_settings': {'check_type': 'required_tags'},
        },
    ],
)
@pytest.mark.parametrize('enable', [True, False])
async def test_on_start_on_stop_billing_subvention_fail(
        taxi_driver_fix, stq, enable, mockserver,
):
    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        return {'status': 'ok'}

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _v1_rules_select(request):
        pass

    response = await taxi_driver_fix.post(
        'v1/mode/on_start/' if enable else 'v1/mode/on_stop/',
        json={
            'driver_profile_id': 'id',
            'park_id': 'id',
            'mode_settings': {
                'rule_id': 'normal_rule',
                'shift_close_time': '03:00:00+03:00',
            },
        },
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 500
    assert stq.driver_fix.times_called == 0


@pytest.mark.parametrize('set_payment_type', (True, False))
@pytest.mark.parametrize(
    'use_robot_set, tariff_merge_policy',
    ((True, 'append'), (False, 'append'), (False, 'replace')),
)
@pytest.mark.parametrize(
    'subvention_rule_id, response_code, tariff_classes',
    [
        ('missing_rule', 404, {'econom'}),
        ('multi_rule', 500, {'econom'}),
        ('normal_rule', 500, {}),
        ('normal_rule', 200, {'econom'}),
        ('normal_rule', 200, {'econom', 'vip'}),
    ],
)
async def test_prepare_basic(
        taxi_driver_fix,
        mockserver,
        set_payment_type,
        use_robot_set,
        tariff_merge_policy,
        subvention_rule_id,
        response_code,
        tariff_classes,
        taxi_config,
):
    if use_robot_set:
        taxi_config.set_values(
            dict(DRIVER_FIX_SET_TARIFFS_BY_ROBOT_SET=use_robot_set),
        )
    taxi_config.set_values(
        dict(
            DRIVER_FIX_SET_PAYMENT_TYPE=set_payment_type,
            DRIVER_FIX_DRIVER_CATEGORIES_API_MERGE_POLICY=tariff_merge_policy,
        ),
    )

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _v1_rules_select(request):
        data = json.loads(request.get_data())
        rule_id = data['rule_ids'][0]
        subventions = []
        if rule_id != 'missing_rule':
            subventions.append(dict(SUBVENTION_RULE_MOCK))
            if rule_id == 'multi_rule':
                subventions.append(dict(SUBVENTION_RULE_MOCK))
            elif tariff_classes is not None:
                subventions[0]['profile_tariff_classes'] = list(tariff_classes)
        return {'subventions': subventions}

    @mockserver.json_handler('/driver-categories-api/v2/drivers/categories')
    def _v2_drivers_categories(request):
        data = json.loads(request.get_data())
        assert data['merge_policy'] == tariff_merge_policy
        assert len(data['categories']) == len(tariff_classes)
        for category in data['categories']:
            assert category['name'] in tariff_classes
        return dict()

    @mockserver.json_handler('/driver-payment-types/service/v1/payment-type')
    def _service_v1_payment_type(request):
        assert set_payment_type
        data = json.loads(request.get_data())
        assert data == {
            'payment_type': 'online',
            'source': 'driver-fix',
            'reason': ('driver_fix rule #' + subvention_rule_id),
        }
        return dict()

    @mockserver.json_handler('/taximeter-basis-minor/driver/robot/set')
    def _robot_set(request):
        data = request.args
        assert data['db'] == 'dbid'
        assert data['session'] == 'driver_session1'
        assert TARIFFS_TRANSLATION_MAP[data['type']] in tariff_classes
        assert data['value'] == '1'
        return {'success': True}

    response = await taxi_driver_fix.post(
        'v1/mode/prepare/',
        json={
            'park_id': 'dbid',
            'driver_profile_id': 'uuid',
            'mode_settings': {
                'rule_id': subvention_rule_id,
                'shift_close_time': '03:00:00+03:00',
            },
        },
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == response_code


async def test_prepare_missing_mode_settings(taxi_driver_fix, mockserver):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _v1_rules_select(request):
        pass

    @mockserver.json_handler('/driver-categories-api/v2/drivers/categories')
    def _v2_drivers_categories(request):
        pass

    response = await taxi_driver_fix.post(
        'v1/mode/prepare/',
        json={'driver_profile_id': 'id', 'park_id': 'id'},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 400
    response_body = response.json()
    assert response_body['code'] == 'BAD_REQUEST'
    assert response_body.get('message')


async def test_prepare_billing_subvention_failed(taxi_driver_fix, mockserver):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _v1_rules_select(request):
        data = json.loads(request.get_data())
        assert data['rule_ids'][0] == 'id'

    @mockserver.json_handler('/driver-categories-api/v2/drivers/categories')
    def _v2_drivers_categories(request):
        return dict()

    response = await taxi_driver_fix.post(
        'v1/mode/prepare/',
        json={
            'driver_profile_id': 'id',
            'park_id': 'id',
            'mode_settings': {
                'rule_id': 'id',
                'shift_close_time': '03:00:00+03:00',
            },
        },
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 500


@pytest.mark.parametrize('tariff_merge_policy', ('append', 'replace'))
async def test_prepare_driver_categories_api_failed(
        taxi_driver_fix, mockserver, taxi_config, tariff_merge_policy,
):
    taxi_config.set_values(
        dict(
            DRIVER_FIX_DRIVER_CATEGORIES_API_MERGE_POLICY=tariff_merge_policy,
        ),
    )

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _v1_rules_select(request):
        data = json.loads(request.get_data())
        assert data['rule_ids'][0] == 'id'
        subventions = []
        subventions.append(dict(SUBVENTION_RULE_MOCK))
        subventions[0]['profile_tariff_classes'] = ['econom']
        return {'subventions': subventions}

    @mockserver.json_handler('/driver-categories-api/v2/drivers/categories')
    def _v2_drivers_categories(request):
        data = json.loads(request.get_data())
        assert len(data['categories']) == 1
        assert data['merge_policy'] == tariff_merge_policy
        assert data['categories'][0]['name'] == 'econom'

    response = await taxi_driver_fix.post(
        'v1/mode/prepare/',
        json={
            'driver_profile_id': 'id',
            'park_id': 'id',
            'mode_settings': {
                'rule_id': 'id',
                'shift_close_time': '03:00:00+03:00',
            },
        },
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 500


@pytest.mark.config(DRIVER_FIX_SET_PAYMENT_TYPE=True)
async def test_prepare_payment_type_failed(taxi_driver_fix, mockserver):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _v1_rules_select(request):
        subventions = []
        subventions.append(dict(SUBVENTION_RULE_MOCK))
        subventions[0]['profile_tariff_classes'] = ['econom']
        return {'subventions': subventions}

    @mockserver.json_handler('/driver-categories-api/v2/drivers/categories')
    def _v2_drivers_categories(request):
        return dict()

    @mockserver.json_handler('/driver-payment-types/service/v1/payment-type')
    def _service_v1_payment_type(request):
        pass

    response = await taxi_driver_fix.post(
        'v1/mode/prepare/',
        json={
            'park_id': 'dbid',
            'driver_profile_id': 'uuid',
            'mode_settings': {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '03:00:00+03:00',
            },
        },
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 500
