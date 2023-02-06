# pylint: disable=F0401,C5521
from dap_tools.dap import dap_fixture  # noqa: F401 C5521
# pylint: enable=F0401,C5521
import pytest


_URL_PREFIX = '/driver/v1/metrics-storage'
_UDIDS_MAPPING = {
    'park-id1_driver-profile-id1': '300000000000000000000000',
    'park-id2_driver-profile-id2': '400000000000000000000000',
}

_TAXIMETER_VERSION = 'Taximeter 9.40 (1234)'


@pytest.fixture(name='unique_driver_udid_by_profile')
def _unique_driver_udid_by_profile(mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def udid_handler(data):
        ud_resp = {'uniques': []}
        for profile_id in data.json.get('profile_id_in_set', []):
            ud_item = {'park_driver_profile_id': profile_id}
            if profile_id in _UDIDS_MAPPING:
                ud_item['data'] = {
                    'unique_driver_id': _UDIDS_MAPPING[profile_id],
                }
            ud_resp['uniques'].append(ud_item)
        return ud_resp

    return udid_handler


@pytest.mark.now('2021-09-11T15:00:00Z')
@pytest.mark.pgsql('drivermetrics')
async def test_driver_v1_priority_history_screen_no_such_profile(
        taxi_driver_metrics_storage,
        mockserver,
        unique_driver_udid_by_profile,
        dap,
):
    taxi_driver_metrics_storage = dap.create_driver_wrapper(
        taxi_driver_metrics_storage,
        driver_uuid='driver-profile-id1',
        driver_dbid='park-id1',
        user_agent=_TAXIMETER_VERSION,
    )
    response = await taxi_driver_metrics_storage.get(
        _URL_PREFIX + '/v1/completion-scores/priority-history-screen',
        params={
            'timezone': 'UTC',
            'older_than': '2021-09-11T15:00:00Z',
            'limit': 30,
        },
        headers={'Accept-Language': 'en_US.UTF-8'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'ui': {
            'items': [
                {
                    'hint': 'You\'ve got no orders in last 7 days',
                    'type': 'header',
                },
            ],
        },
    }


@pytest.mark.now('2021-09-11T15:00:00Z')
@pytest.mark.pgsql('drivermetrics', files=['common.sql'])
async def test_driver_v1_priority_history_screen_no_events(
        taxi_driver_metrics_storage,
        mockserver,
        unique_driver_udid_by_profile,
        dap,
):
    taxi_driver_metrics_storage = dap.create_driver_wrapper(
        taxi_driver_metrics_storage,
        driver_uuid='driver-profile-id1',
        driver_dbid='park-id1',
        user_agent=_TAXIMETER_VERSION,
    )
    response = await taxi_driver_metrics_storage.get(
        _URL_PREFIX + '/v1/completion-scores/priority-history-screen',
        params={
            'timezone': 'UTC',
            'older_than': '2021-09-11T15:00:00Z',
            'limit': 30,
        },
        headers={'Accept-Language': 'en_US.UTF-8'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'ui': {
            'items': [
                {
                    'hint': 'You\'ve got no orders in last 7 days',
                    'type': 'header',
                },
            ],
        },
    }


def make_event(
        unique_driver_id,
        park_driver_profile_id,
        ev_type,
        descriptor_type,
        descriptor_tags,
        created,
        idempotency_token,
):
    typed_extra_data = {
        'order': {
            'activity_value': 100,
            'driver_id': '643753730233_7d1eb10d168740218fd5a03672b98f00',
            'time_to_a': 314,
            'distance_to_a': 1104,
            'tariff_class': 'business',
            'dtags': ['HadOrdersLast30Days'],
            'rtags': None,
            'sp': 1,
            'dispatch_id': '616ede7c803916004808628d',
            'sp_alpha': 1,
            'replace_activity_with_priority': None,
        },
        'dm_service_manual': {
            'operation': 'set_activity_value',
            'mode': 'additive',
            'value': 15,
            'reason': None,
        },
    }
    descriptor = {'type': descriptor_type}
    if descriptor_tags:
        descriptor['tags'] = descriptor_tags
    return {
        'idempotency_token': idempotency_token,
        'unique_driver_id': unique_driver_id,
        'type': ev_type,
        'created': created,
        'park_driver_profile_id': park_driver_profile_id,
        'extra_data': typed_extra_data[ev_type],
        'descriptor': descriptor,
        'order_id': 'order_id: 1',
        'order_alias': 'order_alias: 1',
        'tariff_zone': 'moscow',
    }


@pytest.mark.config(
    # general configs for test
    DRIVER_METRICS_STORAGE_HISTORY_SETTINGS={
        'order': {'filter_out': []},
        'dm_service_manual': {'filter_out': []},
    },
    # support configs for test
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'order': {'__default__': 8 * 24 * 60},
        'dm_service_manual': {'__default__': 8 * 24 * 60},
    },
    DRIVER_METRICS_STORAGE_EVENTS_SPLITTING=2,
    DRIVER_METRICS_STORAGE_EVENTS_PROCESSING_SETTINGS={
        'new_event_age_limit_mins': 60 * 24 * 8,
        'idempotency_token_ttl_mins': 1440,
        'default_event_ttl_hours': 168,
        'processing_ticket_ttl_secs': 60,
        'processing_lag_msecs': 200,
        'default_unprocessed_list_limit': 100,
        'round_robin_process': False,
        'non_transactional_polling': True,
        'polling_max_passes': 3,
    },
)
@pytest.mark.now('2021-09-10T15:00:00Z')
@pytest.mark.pgsql('drivermetrics', files=['common.sql'])
async def test_driver_v1_priority_history_screen_with_events(
        taxi_driver_metrics_storage,
        mockserver,
        mocked_time,
        unique_driver_udid_by_profile,
        dap,  # driver-autority-proxy
        load_json,
):
    # '300000000000000000000000'
    park_id = 'park-id1'
    driver_profile_id = 'driver-profile-id1'
    park_driver_profile_id = '_'.join([park_id, driver_profile_id])

    assert park_driver_profile_id in _UDIDS_MAPPING
    unique_driver_id = _UDIDS_MAPPING[park_driver_profile_id]

    for day in range(3, 10):
        if day == 6:
            continue
        for _repeat in range(2):
            descriptor_tags = ['long_trip', 'tariff_business']
            if day % 2 == 1:
                descriptor_tags.append(
                    'dispatch_short' if _repeat == 0 else 'dispatch_long',
                )
            ev_type, desc_type, desc_tags = (
                ('order', 'complete', descriptor_tags)
                if day != 7
                else ('dm_service_manual', 'set_activity_value', [])
            )
            response = await taxi_driver_metrics_storage.post(
                '/v2/event/new',
                json=make_event(
                    unique_driver_id,
                    park_driver_profile_id,
                    ev_type,
                    desc_type,
                    desc_tags,
                    f'2021-09-{day}T14:59:00Z',
                    f'idempotency_token-n{day}{_repeat}',
                ),
            )
            assert response.status_code == 200

    response_unproc = await taxi_driver_metrics_storage.post(
        '/v3/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 100},
    )
    assert response_unproc.status_code == 200

    offset = 0
    for item in response_unproc.json()['items']:
        for evt in item['events']:
            response = await taxi_driver_metrics_storage.post(
                '/v3/event/complete',
                json={
                    'event_id': evt['event_id'],
                    'ticket_id': -1,
                    'loyalty_increment': 2,
                    'activity': {
                        'value_to_set': 99 + offset,
                        'increment': 4 + offset,
                    },
                    'complete_score': {
                        'increment': 3 + offset,
                        'value_to_set': 3 + offset,
                    },
                    'priority': {
                        'increment': 2 + offset,
                        'absolute_value': 5 + offset,
                    },
                },
            )
            assert response.status_code == 200
            offset += 1

    taxi_driver_metrics_storage = dap.create_driver_wrapper(
        taxi_driver_metrics_storage,
        driver_dbid=park_id,
        driver_uuid=driver_profile_id,
        user_agent=_TAXIMETER_VERSION,
    )
    response = await taxi_driver_metrics_storage.get(
        _URL_PREFIX + '/v1/completion-scores/priority-history-screen',
        params={'older_than': '2021-09-10T15:00:00Z', 'limit': 30},
        headers={'Accept-Language': 'ru_RU.UTF-8'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('big_response.json')
