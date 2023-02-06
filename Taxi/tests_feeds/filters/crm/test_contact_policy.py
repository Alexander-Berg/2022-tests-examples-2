# pylint: disable=W0621
# pylint: disable=W0612
import pytest

DRIVER_WALL_WITH_CRM_CONTACT_POLICY_CONFIG = {
    'driver-wall': {
        'description': 'description',
        'max_feed_ttl_hours': 24,
        'polling_delay_sec': 60,
        'filters': [
            {
                'name': 'crm/contact_policy',
                'enable': True,
                'ignore_errors': False,
                'settings': {
                    'channel': 'wall',
                    'entity_type': 'driver',
                    'request_size': '2',
                },
            },
        ],
    },
}

ALLOWED_CHANNELS = sorted(
    ['taximeter:Driver:dbid1:uuid1', 'taximeter:Country:Russia'],
)
FILTERED_CHANNELS = sorted(
    ['taximeter:Driver:dbid2:uuid2', 'uberdriver:Driver:dbid3:uuid3'],
)


@pytest.fixture
def crm_admin(mockserver):
    @mockserver.json_handler('/crm-admin/v1/campaign/backend/item')
    def create_campaign(request):
        assert request.json == {
            'entity_type': 'driver',
            'channel': 'wall',
            'source_campaign_id': 'driver-wall:request_id',
        }

        return {
            'entity_type': request.json['entity_type'],
            'channel': request.json['channel'],
            'id': '358af30761eb454db8af9c8f9666e5a8',
        }


@pytest.fixture
def crm_policy(mockserver):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message_bulk')
    def check(request):
        allowed = []
        for item in request.json['items']:
            channel = item['entity_id']
            if channel in ALLOWED_CHANNELS:
                allowed.append(True)
            elif channel in FILTERED_CHANNELS:
                allowed.append(False)
            else:
                assert False
        return {'allowed': allowed}


@pytest.mark.config(FEEDS_SERVICES=DRIVER_WALL_WITH_CRM_CONTACT_POLICY_CONFIG)
@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_contact_policy(taxi_feeds, crm_admin, crm_policy):
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'request_id',
            'service': 'driver-wall',
            'expire': '2019-12-03T12:21:48.203515Z',
            'payload': {'text': 'Happy new year'},
            'channels': [
                {'channel': channel}
                for channel in ALLOWED_CHANNELS + FILTERED_CHANNELS
            ],
        },
    )
    assert response.status_code == 200
    filtered = response.json()['filtered']
    assert sorted(item['channel'] for item in filtered) == FILTERED_CHANNELS


@pytest.mark.config(FEEDS_SERVICES=DRIVER_WALL_WITH_CRM_CONTACT_POLICY_CONFIG)
@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_contact_policy_batch(taxi_feeds, crm_admin, crm_policy):
    response = await taxi_feeds.post(
        '/v1/batch/create',
        json={
            'items': [
                {
                    'request_id': 'request_id',
                    'service': 'driver-wall',
                    'expire': '2019-12-03T12:21:48.203515Z',
                    'payload': {'text': 'Happy new year'},
                    'channels': [
                        {'channel': channel} for channel in ALLOWED_CHANNELS
                    ],
                },
                {
                    'request_id': 'request_id',
                    'service': 'driver-wall',
                    'expire': '2019-12-03T12:21:48.203515Z',
                    'payload': {'text': 'Happy new year'},
                    'channels': [
                        {'channel': channel} for channel in FILTERED_CHANNELS
                    ],
                },
            ],
        },
    )
    assert response.status_code == 200
    filtered1 = response.json()['items'][0]['filtered']
    assert filtered1 == []

    assert response.status_code == 200
    filtered2 = response.json()['items'][1]['filtered']
    assert sorted(item['channel'] for item in filtered2) == FILTERED_CHANNELS


@pytest.mark.now('2019-12-01T00:00:00Z')
@pytest.mark.parametrize(
    'ignore_errors,error_stage,expected_code',
    [
        (False, 'init', 500),
        (False, 'process', 500),
        (True, 'init', 200),
        (True, 'process', 200),
    ],
)
async def test_ignore_errors(
        taxi_feeds,
        taxi_config,
        mockserver,
        ignore_errors,
        error_stage,
        expected_code,
):
    @mockserver.json_handler('/crm-admin/v1/campaign/backend/item')
    def create_campaign(request):
        if error_stage == 'init':
            raise mockserver.TimeoutError()
        return {
            'entity_type': 'driver',
            'channel': 'wall',
            'id': '358af30761eb454db8af9c8f9666e5a8',
        }

    @mockserver.json_handler('/crm-policy/v1/check_update_send_message_bulk')
    def check(request):
        if error_stage == 'process':
            raise mockserver.TimeoutError()
        return {'allowed': [True]}

    config = DRIVER_WALL_WITH_CRM_CONTACT_POLICY_CONFIG.copy()
    config['driver-wall']['filters'][0]['ignore_errors'] = ignore_errors
    taxi_config.set_values({'FEEDS_SERVICES': config})
    await taxi_feeds.invalidate_caches()

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'request_id',
            'service': 'driver-wall',
            'expire': '2019-12-03T12:21:48.203515Z',
            'payload': {'text': 'Happy new year'},
            'channels': [{'channel': 'teximeter:Driver:dbid:uuid'}],
        },
    )
    assert response.status_code == expected_code


@pytest.mark.now('2019-12-01T00:00:00Z')
@pytest.mark.config(FEEDS_SERVICES=DRIVER_WALL_WITH_CRM_CONTACT_POLICY_CONFIG)
async def test_ignore_filters(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'request_id',
            'service': 'driver-wall',
            'expire': '2019-12-03T12:21:48.203515Z',
            'payload': {'text': 'Happy new year'},
            'channels': [{'channel': 'teximeter:Driver:dbid:uuid'}],
            'ignore_filters': True,
        },
    )

    assert response.status_code == 200
    assert response.json()['filtered'] == []
