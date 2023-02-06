# pylint: disable=import-error
from driver_fix.fbs import ConstraintsData as fbs_cd
import pytest

from tests_driver_fix import common

VIRTUAL_BY_DRIVER_RESPONSE = {
    'subventions': [
        {
            'type': 'driver_fix',
            'subvention_rule_id': 'subvention_rule_id',
            'payoff': {'amount': '0', 'currency': 'RUB'},
            'period': {
                'start_time': '2019-01-01T00:00:01+03:00',
                'end_time': '2019-01-02T00:00:00+03:00',
            },
            'commission_info': {
                'payoff_commission': {'amount': '10', 'currency': 'RUB'},
            },
            'details': {
                'accounted_time_seconds': 600,
                'cash_income': {'amount': '0', 'currency': 'RUB'},
                'guarantee': {'amount': '1000', 'currency': 'RUB'},
                'cash_commission': {'amount': '0', 'currency': 'RUB'},
            },
        },
    ],
}

MODE_INFO_RESPONSE = {
    'mode': {
        'name': 'driver_fix',
        'started_at': '2019-01-01T08:00:00+0300',
        'features': [
            {
                'name': 'driver_fix',
                'settings': {
                    'rule_id': 'subvention_rule_id',
                    'shift_close_time': '00:00:00+03:00',
                },
            },
            {'name': 'tags'},
        ],
    },
}

MODE_INFO_RESPONSE_OTHER_RULE = {
    'mode': {
        'name': 'driver_fix',
        'started_at': '2019-01-01T08:00:00+0300',
        'features': [
            {
                'name': 'driver_fix',
                'settings': {
                    'rule_id': 'subvention_rule_id_other',
                    'shift_close_time': '00:00:00+03:00',
                },
            },
            {'name': 'tags'},
        ],
    },
}


def _get_request(handler, json_request=True):
    res = handler.next_call()['request']
    return res.json if json_request else res


def _check_mode_info_request(mode_info, times_called=1):
    assert mode_info.times_called == times_called

    request = _get_request(mode_info, json_request=False)
    assert request.args['driver_profile_id'] == 'uuid'
    assert request.args['park_id'] == 'dbid'


def _check_retrieve_by_profiles_request(unique_drivers, times_called=1):
    assert (
        unique_drivers.mock_retrieve_by_profiles.times_called == times_called
    )

    request = _get_request(unique_drivers.mock_retrieve_by_profiles)
    assert request == {'profile_id_in_set': ['dbid_uuid']}


def _check_v2_event_new_request(
        v2_event_new,
        times_called=1,
        constraints_new=None,
        constraints_fixed=None,
):
    assert v2_event_new.times_called == times_called
    if times_called == 0:
        return

    expected_request_common = {
        'type': 'constraints',
        'created': '2019-01-01T09:00:00+00:00',
        'unique_driver_id': 'very_unique_id',
        'park_driver_profile_id': 'dbid_uuid',
    }

    expected_request_started: dict = {
        'descriptor': {'type': 'start', 'tags': ['driver_fix']},
        'extra_data': {'constraints': constraints_new},
    }
    expected_request_started.update(expected_request_common)

    expected_request_ended: dict = {
        'extra_data': {'constraints': constraints_fixed},
        'descriptor': {'type': 'end', 'tags': ['driver_fix']},
    }
    expected_request_ended.update(expected_request_common)

    def check_request(request, expected_request):
        for key, value in expected_request.items():
            if key != 'extra_data':
                assert value == request[key]
                continue
            request_extra_data = request['extra_data']
            expected_constraints = value['constraints']
            assert 'constraints' not in request_extra_data
            request_constraints_data = request_extra_data['constraints_data']
            constraints = set()
            for constraint in request_constraints_data:
                constraints.add(constraint['name'])
                assert 'id' in constraint
            assert constraints == set(expected_constraints)

    for _i in range(times_called):
        request = _get_request(v2_event_new)
        if request['descriptor']['type'] == 'start':
            check_request(request, expected_request_started)
        else:
            check_request(request, expected_request_ended)


def _params(lon=37.63361316, lat=55.75419758):
    return {
        'tz': 'Europe/Moscow',
        'park_id': 'dbid',
        'lon': lon,
        'lat': lat,
        'supported_features': 'native_restrictions',
    }


def _check_virtual_by_driver_request(virtual_by_driver, times_called=1):
    assert virtual_by_driver.times_called == times_called

    request = _get_request(virtual_by_driver)
    assert request == {
        'driver': {'db_id': 'dbid', 'uuid': 'uuid'},
        'types': ['driver_fix'],
    }


def _check_constraints_cache(redis_store, expected_content: set):
    assert set() == redis_store.smembers('dbid_uuid:constraints')

    redis_data = redis_store.get('dbid_uuid:constraints_data')
    assert redis_data
    fbs_data = fbs_cd.ConstraintsData.GetRootAsConstraintsData(
        bytearray(redis_data), 0,
    )
    assert len(expected_content) == fbs_data.ConstraintsLength()
    constraints = set()
    for i in range(fbs_data.ConstraintsLength()):
        fbs_constraint = fbs_data.Constraints(i)
        assert fbs_constraint.Id()
        constraints.add(fbs_constraint.Name())
    assert constraints == expected_content


SEND_CONSTRAINTS_TO_DMS_CONFIG = {
    'enabled': True,
    'cache_ttl_in_seconds': 1000000,
    'send_constraint_end': True,
    'cache_command_control': {
        'max_retries': 2,
        'timeout_all_ms': 10000,
        'timeout_single_ms': 10000,
    },
}


@pytest.mark.config(
    DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True,
    DRIVER_FIX_SEND_CONSTRAINTS_TO_DMS=SEND_CONSTRAINTS_TO_DMS_CONFIG,
    DRIVER_FIX_COORDINATE_NOT_FOUND_CONSTRAINT=True,
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_dms_called_once(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        redis_store,
        unique_drivers,
        taxi_config,
):
    common.set_native_restrictions_cfg(taxi_config, enabled=True)
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']
    mock_offer_requirements.profiles_value['position'] = [0, 0]
    mock_offer_requirements.set_position_fallback([37.63361316, 55.75419758])

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _dms_mode_info(request):
        return MODE_INFO_RESPONSE

    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    async def _event_new(request):
        return {}

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        return VIRTUAL_BY_DRIVER_RESPONSE

    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=_params(),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200

    def get_restriction_id(view_status_response):
        return view_status_response.json()['restriction']['id']

    restriction_id = get_restriction_id(response)
    assert restriction_id
    _check_mode_info_request(_dms_mode_info)
    _check_retrieve_by_profiles_request(unique_drivers)
    _check_v2_event_new_request(
        _event_new, constraints_new=['coordinate_not_found'],
    )
    _check_virtual_by_driver_request(_get_by_driver)

    _check_constraints_cache(redis_store, {b'coordinate_not_found'})
    assert redis_store.get('dbid_uuid:rule:id') == b'subvention_rule_id'

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=_params(),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200

    _check_mode_info_request(_dms_mode_info)
    _check_retrieve_by_profiles_request(unique_drivers)
    _check_virtual_by_driver_request(_get_by_driver)
    _check_v2_event_new_request(_event_new, times_called=0)
    assert restriction_id == get_restriction_id(response)


@pytest.mark.config(
    DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True,
    DRIVER_FIX_SEND_CONSTRAINTS_TO_DMS=SEND_CONSTRAINTS_TO_DMS_CONFIG,
    DRIVER_FIX_COORDINATE_NOT_FOUND_CONSTRAINT=True,
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_dms_called_on_switching_rule(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        redis_store,
        unique_drivers,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']
    mock_offer_requirements.profiles_value['position'] = [0, 0]
    mock_offer_requirements.set_position_fallback([37.63361316, 55.75419758])
    rule_changed = False

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _dms_mode_info(request):
        return (
            MODE_INFO_RESPONSE_OTHER_RULE
            if rule_changed
            else MODE_INFO_RESPONSE
        )

    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    async def _event_new(request):
        return {}

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        return VIRTUAL_BY_DRIVER_RESPONSE

    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=_params(),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200

    _check_mode_info_request(_dms_mode_info)
    _check_retrieve_by_profiles_request(unique_drivers)
    _check_v2_event_new_request(
        _event_new, constraints_new=['coordinate_not_found'],
    )
    _check_virtual_by_driver_request(_get_by_driver)

    _check_constraints_cache(redis_store, {b'coordinate_not_found'})
    assert redis_store.get('dbid_uuid:rule:id') == b'subvention_rule_id'

    rule_changed = True
    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=_params(),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200

    _check_mode_info_request(_dms_mode_info)
    _check_retrieve_by_profiles_request(unique_drivers)
    _check_virtual_by_driver_request(_get_by_driver)
    _check_v2_event_new_request(
        _event_new, constraints_new=['coordinate_not_found'],
    )

    _check_constraints_cache(redis_store, {b'coordinate_not_found'})

    assert redis_store.get('dbid_uuid:rule:id') == b'subvention_rule_id_other'


@pytest.mark.config(
    DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'],
    DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True,
    DRIVER_FIX_SEND_CONSTRAINTS_TO_DMS=SEND_CONSTRAINTS_TO_DMS_CONFIG,
    DRIVER_FIX_COORDINATE_NOT_FOUND_CONSTRAINT=True,
    DRIVER_FIX_CONSTRAINTS_ON_TAGS={
        'frozen_timer': {
            'violate_if': ['frozen_timer_tag'],
            'should_freeze_timer': True,
            'show_in_status_panel': False,
            #                       ^^^^^
            # even if we don't show restriction
            # we should send its state
        },
        'frozen_timer_recently': {
            'violate_if': ['frozen_timer_recently_tag'],
            'should_freeze_timer': True,
            'show_in_status_panel': True,
        },
    },
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_constraints_changed(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        redis_store,
        driver_tags_mocks,
        unique_drivers,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _dms_mode_info(request):
        return MODE_INFO_RESPONSE

    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    async def _event_new(request):
        return {}

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        return VIRTUAL_BY_DRIVER_RESPONSE

    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')
    # set position outside of zone
    lon, lat = 30.0, 50.0
    mock_offer_requirements.set_position_fallback([lon, lat])
    # trigger coordinate not found constraint
    mock_offer_requirements.profiles_value['position'] = [0, 0]

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=_params(lon=lon, lat=lat),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200

    _check_mode_info_request(_dms_mode_info)
    _check_retrieve_by_profiles_request(unique_drivers)
    _check_v2_event_new_request(
        _event_new, constraints_new=['coordinate_not_found', 'zone'],
    )
    _check_virtual_by_driver_request(_get_by_driver)

    _check_constraints_cache(redis_store, {b'zone', b'coordinate_not_found'})
    assert redis_store.get('dbid_uuid:rule:id') == b'subvention_rule_id'

    # add frozen timer constraint
    driver_tags_mocks.set_tags_info('dbid', 'uuid', ['frozen_timer_tag'])
    # fix zone constraint
    mock_offer_requirements.set_position_fallback([37.63361316, 55.75419758])
    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=_params(),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200

    _check_mode_info_request(_dms_mode_info)
    _check_retrieve_by_profiles_request(unique_drivers)
    _check_virtual_by_driver_request(_get_by_driver)
    # dms should be invoked two times :
    # one for new constraints and one for fixed
    _check_v2_event_new_request(
        _event_new,
        times_called=2,
        constraints_new=['frozen_timer'],
        constraints_fixed=['zone'],
    )

    _check_constraints_cache(
        redis_store, {b'frozen_timer', b'coordinate_not_found'},
    )
    assert redis_store.get('dbid_uuid:rule:id') == b'subvention_rule_id'


@pytest.mark.config(
    DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'],
    DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True,
    DRIVER_FIX_SEND_CONSTRAINTS_TO_DMS=SEND_CONSTRAINTS_TO_DMS_CONFIG,
    DRIVER_FIX_CONSTRAINTS_ON_TAGS={
        'test_constraint_on_tags': {
            'violate_if': [],  # means violate always
            'show_in_status_panel': False,
        },
    },
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_dms_called_even_for_not_status_constrains(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        redis_store,
        driver_tags_mocks,
        unique_drivers,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']
    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')

    # trigger 'coordinate not found'
    mock_offer_requirements.profiles_value['position'] = [0, 0]
    lon, lat = 30.0, 50.0
    mock_offer_requirements.set_position_fallback([lon, lat])

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _dms_mode_info(request):
        return MODE_INFO_RESPONSE

    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    async def _event_new(request):
        return {}

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        return VIRTUAL_BY_DRIVER_RESPONSE

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=_params(lon=lon, lat=lat),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200

    _check_v2_event_new_request(
        _event_new,
        constraints_new=[
            'coordinate_not_found',
            'zone',
            'test_constraint_on_tags',
        ],
    )

    _check_constraints_cache(
        redis_store,
        {b'coordinate_not_found', b'zone', b'test_constraint_on_tags'},
    )
