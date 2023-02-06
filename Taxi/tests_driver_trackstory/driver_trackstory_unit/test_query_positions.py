# pylint: disable=import-error
# pylint: disable=unused-variable

from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils

SIGNAL_V2_CHANNEL = 'channel:yagr:signal_v2'


def _get_signal_v2_message(driver_id, now):
    timestamp = int(utils.timestamp(now)) * 1000
    drivers = [
        {
            'driver_id': driver_id,
            'position': [55, 37],
            'direction': 45,
            'unix_time': timestamp,
            'speed': 11.666666666666668,
            'accuracy': 1,
            'source': 'AndroidGps',
        },
    ]
    return geobus.serialize_signal_v2(drivers, now)


def _get_custom_signal_v2_message(driver_id_info, now):
    return geobus.serialize_signal_v2([driver_id_info], now)


@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 120, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': True,
            'storage': {'max_age_seconds': 60, 'max_points_count': 30},
        },
    },
)
async def test_400_on_no_algorithm_given(taxi_driver_trackstory_adv):
    request_body = {
        'driver_ids': ['dbid_uuid'],
        'max_age': 10000,
        'prefered_sources': 'all',
    }
    response = await taxi_driver_trackstory_adv.post(
        'query/positions', json=request_body,
    )
    assert response.status_code == 400


@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 120, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': True,
            'storage': {'max_age_seconds': 60, 'max_points_count': 30},
        },
    },
)
async def test_not_found_old_api(taxi_driver_trackstory_adv):
    request_body = {
        'driver_ids': ['dbid_uuid'],
        'max_age': 100,
        'prefered_sources': 'all',
        'algorithm': 'AsOfNow',
    }
    response = await taxi_driver_trackstory_adv.post(
        'query/positions', json=request_body,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['results'] == [[]]


@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 120, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': True,
            'storage': {'max_age_seconds': 60, 'max_points_count': 30},
        },
    },
)
async def test_all_of_available_positions_old_api(
        taxi_driver_trackstory_adv, testpoint, now,
):
    @testpoint('ignore_redis')
    def ignore_redis(data):
        return True

    driver_id = 'dbid_uuid_1'
    driver_1_sources = [
        'AndroidGps',
        'AndroidNetwork',
        'AndroidFused',
        'AndroidPassive',
        'YandexLbsWifi',
        'YandexLbsGsm',
        'YandexLbsIp',
        'YandexMapkit',
        'YandexNavi',
        'Unknown',
        'Realtime',
        'Camera',
    ]
    driver_1_sources_expected = [
        'U:AndroidGps',
        'U:AndroidNetwork',
        'U:AndroidFused',
        'U:AndroidPassive',
        'U:YandexLbsWifi',
        'U:YandexLbsGsm',
        'U:YandexLbsIp',
        'U:YandexMapkit',
        'U:YandexNavi',
        'U:Unknown',
        'U:Realtime',
        'U:Camera',
    ]
    messages = [
        _get_custom_signal_v2_message(
            {
                'driver_id': driver_id,
                'position': [55, 37],
                'unix_time': int(utils.timestamp(now)) * 1000,
                'source': source,
            },
            now,
        )
        for source in driver_1_sources
    ]
    for message in messages:
        await taxi_driver_trackstory_adv.sync_send_to_channel(
            SIGNAL_V2_CHANNEL, message,
        )

    driver_id2 = 'dbid_uuid_2'
    message2 = _get_signal_v2_message(driver_id2, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        SIGNAL_V2_CHANNEL, message2,
    )

    response = await taxi_driver_trackstory_adv.post(
        'query/positions',
        json={
            'driver_ids': [driver_id, driver_id2],
            'max_age': 100,
            'prefered_sources': 'all',
            'algorithm': 'AsOfNow',
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    assert len(data['results'][0]) == len(driver_1_sources_expected)
    assert len(data['results'][1]) == 1
    driver_1_response_sources = list(
        map(lambda x: x['source'], data['results'][0]),
    )
    assert sorted(driver_1_response_sources) == sorted(
        driver_1_sources_expected,
    )

    assert data['results'][1][0]['source'] == 'U:AndroidGps'


@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 120, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': True,
            'storage': {'max_age_seconds': 60, 'max_points_count': 30},
        },
    },
)
async def test_reasonably_precise_positions_old_api(
        taxi_driver_trackstory_adv, testpoint, now,
):
    @testpoint('ignore_redis')
    def ignore_redis(data):
        return True

    driver_id = 'dbid_uuid_1'
    driver_1_sources = [
        'AndroidGps',
        'AndroidNetwork',
        'AndroidFused',
        'AndroidPassive',
        'YandexLbsWifi',
        'YandexLbsGsm',
        'YandexLbsIp',
        'YandexMapkit',
        'YandexNavi',
        'Unknown',
        'Realtime',
        'Camera',
    ]
    driver_1_sources_expected = [
        'U:AndroidGps',
        'U:YandexLbsWifi',
        'U:YandexLbsGsm',
    ]
    messages = [
        _get_custom_signal_v2_message(
            {
                'driver_id': driver_id,
                'position': [55, 37],
                'unix_time': int(utils.timestamp(now)) * 1000,
                'source': source,
            },
            now,
        )
        for source in driver_1_sources
    ]
    for message in messages:
        await taxi_driver_trackstory_adv.sync_send_to_channel(
            SIGNAL_V2_CHANNEL, message,
        )

    driver_id2 = 'dbid_uuid_2'
    message2 = _get_signal_v2_message(driver_id2, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        SIGNAL_V2_CHANNEL, message2,
    )

    response = await taxi_driver_trackstory_adv.post(
        'query/positions',
        json={
            'driver_ids': [driver_id, driver_id2],
            'max_age': 100,
            'prefered_sources': 'reasonably_precise',
            'algorithm': 'AsOfNow',
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    assert len(data['results'][0]) == len(driver_1_sources_expected)
    driver_1_response_sources = list(
        map(lambda x: x['source'], data['results'][0]),
    )
    assert sorted(driver_1_response_sources) == sorted(
        driver_1_sources_expected,
    )


async def test_not_found(taxi_driver_trackstory_adv, testpoint):
    @testpoint('ignore_redis')
    def ignore_redis(data):
        return True

    request_body = {
        'driver_ids': ['dbid_uuid'],
        'max_age': 100,
        'prefered_sources': 'all',
        'parameterized_algorithm': {'algorithm': 'AsOfNow'},
    }
    response = await taxi_driver_trackstory_adv.post(
        'query/positions', json=request_body,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['results'] == [[]]


@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 120, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': True,
            'storage': {'max_age_seconds': 60, 'max_points_count': 30},
        },
    },
)
async def test_all_of_available_positions(
        taxi_driver_trackstory_adv, testpoint, now,
):
    @testpoint('ignore_redis')
    def ignore_redis(data):
        return True

    driver_id = 'dbid_uuid_1'
    driver_1_sources = [
        'AndroidGps',
        'AndroidNetwork',
        'AndroidFused',
        'AndroidPassive',
        'YandexLbsWifi',
        'YandexLbsGsm',
        'YandexLbsIp',
        'YandexMapkit',
        'YandexNavi',
        'Unknown',
        'Realtime',
        'Camera',
    ]
    driver_1_sources_expected = [
        'U:AndroidGps',
        'U:AndroidNetwork',
        'U:AndroidFused',
        'U:AndroidPassive',
        'U:YandexLbsWifi',
        'U:YandexLbsGsm',
        'U:YandexLbsIp',
        'U:YandexMapkit',
        'U:YandexNavi',
        'U:Unknown',
        'U:Realtime',
        'U:Camera',
    ]
    messages = [
        _get_custom_signal_v2_message(
            {
                'driver_id': driver_id,
                'position': [55, 37],
                'unix_time': int(utils.timestamp(now)) * 1000,
                'source': source,
            },
            now,
        )
        for source in driver_1_sources
    ]
    for message in messages:
        await taxi_driver_trackstory_adv.sync_send_to_channel(
            SIGNAL_V2_CHANNEL, message,
        )

    driver_id2 = 'dbid_uuid_2'
    message2 = _get_signal_v2_message(driver_id2, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        SIGNAL_V2_CHANNEL, message2,
    )

    response = await taxi_driver_trackstory_adv.post(
        'query/positions',
        json={
            'driver_ids': [driver_id, driver_id2],
            'max_age': 100,
            'prefered_sources': 'all',
            'parameterized_algorithm': {'algorithm': 'AsOfNow'},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    assert len(data['results'][0]) == len(driver_1_sources_expected)
    assert len(data['results'][1]) == 1
    driver_1_response_sources = list(
        map(lambda x: x['source'], data['results'][0]),
    )
    assert sorted(driver_1_response_sources) == sorted(
        driver_1_sources_expected,
    )

    assert data['results'][1][0]['source'] == 'U:AndroidGps'


@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 120, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': True,
            'storage': {'max_age_seconds': 60, 'max_points_count': 30},
        },
    },
)
@pytest.mark.config(
    PERCENT_OF_USAGE_INTERNAL_TRACKSTORY={'/query/positions': 100},
)
async def test_usage_internal_trackstory(
        taxi_driver_trackstory_adv, testpoint, mockserver, now,
):
    @testpoint('ignore_redis')
    def ignore_redis(data):
        return True

    dbid = 'dbid'
    uuid1 = 'uuid_1'
    uuid2 = 'uuid_2'
    driver_id = dbid + '_' + uuid1
    driver_id2 = dbid + '_' + uuid2
    driver_1_sources = [
        'AndroidGps',
        'AndroidNetwork',
        'AndroidFused',
        'AndroidPassive',
        'YandexLbsWifi',
        'YandexLbsGsm',
        'YandexLbsIp',
        'YandexMapkit',
        'YandexNavi',
        'Realtime',
        'Camera',
        'Adjusted',
        'Verified',
    ]
    driver_1_sources_expected = [
        'U:AndroidGps',
        'U:AndroidNetwork',
        'U:AndroidFused',
        'U:AndroidPassive',
        'U:YandexLbsWifi',
        'U:YandexLbsGsm',
        'U:YandexLbsIp',
        'U:YandexMapkit',
        'U:YandexNavi',
        'U:Realtime',
        'U:Camera',
        'Adjusted',
        'Raw',
    ]
    driver_1_sources2_expected = [
        'AndroidGps',
        'AndroidNetwork',
        'AndroidFused',
        'AndroidPassive',
        'YandexLbsWifi',
        'YandexLbsGsm',
        'YandexLbsIp',
        'YandexMapkit',
        'YandexNavi',
        'Realtime',
        'Camera',
        'AdjustedPositions',
        'RawPositions',
    ]

    @mockserver.json_handler('/internal-trackstory/taxi/bulk/positions')
    def _mock_internal_trackstory(request):
        body = request.json
        assert body['contractor_ids'][0]['uuid'] == uuid1
        assert body['contractor_ids'][0]['dbid'] == dbid
        assert body['contractor_ids'][1]['uuid'] == uuid2
        assert body['contractor_ids'][1]['dbid'] == dbid

        result = [{'contractor': {'uuid': uuid1, 'dbid': dbid}}]
        for source in driver_1_sources:
            result[0][source] = [
                {
                    'timestamp': 1552003222000,
                    'sensors': [],
                    'geodata': [
                        {
                            'positions': [{'position': [1.0, 1.0]}],
                            'time_shift': 0,
                        },
                    ],
                },
            ]
        result.append(
            {
                'contractor': {'uuid': uuid2, 'dbid': dbid},
                'AndroidGps': [
                    {
                        'timestamp': 1552003222,
                        'sensors': [],
                        'geodata': [
                            {
                                'positions': [{'position': [2.0, 2.0]}],
                                'time_shift': 0,
                            },
                        ],
                    },
                ],
            },
        )
        return result

    response = await taxi_driver_trackstory_adv.post(
        'query/positions',
        json={
            'driver_ids': [driver_id, driver_id2],
            'max_age': 100,
            'prefered_sources': 'all',
            'parameterized_algorithm': {'algorithm': 'AsOfNow'},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    assert len(data['results'][0]) == len(driver_1_sources_expected)
    assert len(data['results'][1]) == 1
    driver_1_response_sources = list(
        map(lambda x: x['source'], data['results'][0]),
    )
    assert sorted(driver_1_response_sources) == sorted(
        driver_1_sources_expected,
    )
    driver_1_response_sources2 = list(
        map(lambda x: x['source2'], data['results'][0]),
    )
    assert sorted(driver_1_response_sources2) == sorted(
        driver_1_sources2_expected,
    )

    assert data['results'][1][0]['source'] == 'U:AndroidGps'
    assert data['results'][1][0]['source2'] == 'AndroidGps'


@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 120, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': True,
            'storage': {'max_age_seconds': 60, 'max_points_count': 30},
        },
    },
)
async def test_reasonably_precise_positions(
        taxi_driver_trackstory_adv, testpoint, now,
):
    @testpoint('ignore_redis')
    def ignore_redis(data):
        return True

    driver_id = 'dbid_uuid_1'
    driver_1_sources = [
        'AndroidGps',
        'AndroidNetwork',
        'AndroidFused',
        'AndroidPassive',
        'YandexLbsWifi',
        'YandexLbsGsm',
        'YandexLbsIp',
        'YandexMapkit',
        'YandexNavi',
        'Unknown',
        'Realtime',
        'Camera',
    ]
    driver_1_sources_expected = [
        'U:AndroidGps',
        'U:YandexLbsWifi',
        'U:YandexLbsGsm',
    ]
    messages = [
        _get_custom_signal_v2_message(
            {
                'driver_id': driver_id,
                'position': [55, 37],
                'unix_time': int(utils.timestamp(now)) * 1000,
                'source': source,
            },
            now,
        )
        for source in driver_1_sources
    ]
    for message in messages:
        await taxi_driver_trackstory_adv.sync_send_to_channel(
            SIGNAL_V2_CHANNEL, message,
        )

    driver_id2 = 'dbid_uuid_2'
    message2 = _get_signal_v2_message(driver_id2, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        SIGNAL_V2_CHANNEL, message2,
    )

    response = await taxi_driver_trackstory_adv.post(
        'query/positions',
        json={
            'driver_ids': [driver_id, driver_id2],
            'max_age': 100,
            'prefered_sources': 'reasonably_precise',
            'parameterized_algorithm': {'algorithm': 'AsOfNow'},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    assert len(data['results'][0]) == len(driver_1_sources_expected)
    driver_1_response_sources = list(
        map(lambda x: x['source'], data['results'][0]),
    )
    assert sorted(driver_1_response_sources) == sorted(
        driver_1_sources_expected,
    )


# Test checks that algoritm does retries if some positions are unavailable
# (expect to do 1 retry of 3 possible)
@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 120, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': True,
            'storage': {'max_age_seconds': 60, 'max_points_count': 30},
        },
    },
)
async def test_retry_success(taxi_driver_trackstory_adv, testpoint, now):
    @testpoint('ignore_redis')
    def ignore_redis(data):
        return True

    driver_id = 'dbid_uuid'
    request_body = {
        'driver_ids': [driver_id],
        'max_age': 100,
        'prefered_sources': ['U:AndroidGps'],
        'parameterized_algorithm': {
            'algorithm': 'WithRetry',
            'timeout': 30,
            'max_retries': 3,
        },
    }

    @testpoint('add_points')
    async def add_points(data):
        message = _get_custom_signal_v2_message(
            {
                'driver_id': driver_id,
                'position': [55, 37],
                'unix_time': int(utils.timestamp(now)) * 1000,
                'source': 'AndroidGps',
            },
            now,
        )
        await taxi_driver_trackstory_adv.sync_send_to_channel(
            SIGNAL_V2_CHANNEL, message,
        )

    response = await taxi_driver_trackstory_adv.post(
        'query/positions', json=request_body,
    )

    assert response.status_code == 200
    assert add_points.times_called == 2
    data = response.json()
    assert len(data['results']) == 1
    assert len(data['results'][0]) == 1


# checks if algorithm does maximum number of retries if can't find requested
# positions (does not less than max_retries if needed)
@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 120, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': True,
            'storage': {'max_age_seconds': 60, 'max_points_count': 30},
        },
    },
)
async def test_retry_max_retries_success(
        taxi_driver_trackstory_adv, testpoint, now,
):
    @testpoint('ignore_redis')
    def ignore_redis(data):
        return True

    driver_id = 'dbid_uuid'
    max_retries = 5
    request_body = {
        'driver_ids': [driver_id],
        'max_age': 100,
        'prefered_sources': ['U:AndroidGps'],
        'parameterized_algorithm': {
            'algorithm': 'WithRetry',
            'timeout': 30,
            'max_retries': max_retries,
        },
    }

    @testpoint('add_points')
    async def add_points(data):
        if data == max_retries - 1:
            message = _get_custom_signal_v2_message(
                {
                    'driver_id': driver_id,
                    'position': [55, 37],
                    'unix_time': int(utils.timestamp(now)) * 1000,
                    'source': 'AndroidGps',
                },
                now,
            )
            await taxi_driver_trackstory_adv.sync_send_to_channel(
                SIGNAL_V2_CHANNEL, message,
            )

    response = await taxi_driver_trackstory_adv.post(
        'query/positions', json=request_body,
    )

    assert response.status_code == 200
    assert add_points.times_called == max_retries + 1
    data = response.json()
    assert len(data['results']) == 1
    assert len(data['results'][0]) == 1


# checks if algorithm does no more than max_retries
# retries even if it can't fnd requested positions
@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 120, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': True,
            'storage': {'max_age_seconds': 60, 'max_points_count': 30},
        },
    },
)
async def test_retry_max_retries_failes(
        taxi_driver_trackstory_adv, testpoint, now,
):
    @testpoint('ignore_redis')
    def ignore_redis(data):
        return True

    driver_id = 'dbid_uuid'
    max_retries = 5
    request_body = {
        'driver_ids': [driver_id],
        'max_age': 100,
        'prefered_sources': ['U:AndroidGps'],
        'parameterized_algorithm': {
            'algorithm': 'WithRetry',
            'timeout': 30,
            'max_retries': max_retries,
        },
    }

    @testpoint('add_points')
    async def add_points(data):
        pass

    response = await taxi_driver_trackstory_adv.post(
        'query/positions', json=request_body,
    )

    assert response.status_code == 200
    assert add_points.times_called == max_retries + 1
    data = response.json()
    assert len(data['results']) == 1
    assert not data['results'][0]


# checks algorithm discards too old points
@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 120, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': True,
            'storage': {'max_age_seconds': 60, 'max_points_count': 30},
        },
    },
)
async def test_discard_too_old_points(
        taxi_driver_trackstory_adv, testpoint, now,
):
    @testpoint('ignore_redis')
    def ignore_redis(data):
        return True

    driver_id = 'dbid_uuid'

    # send old point
    timestamp = int(utils.timestamp(now)) * 1000 - 2000
    drivers = [
        {
            'driver_id': driver_id,
            'position': [55, 37],
            'direction': 45,
            'unix_time': timestamp,
            'speed': 11.666666666666668,
            'accuracy': 1,
            'source': 'AndroidGps',
        },
    ]
    message = geobus.serialize_signal_v2(drivers, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        SIGNAL_V2_CHANNEL, message,
    )

    max_retries = 5
    request_body = {
        'driver_ids': [driver_id],
        'max_age': 1,
        'prefered_sources': ['U:AndroidGps'],
        'parameterized_algorithm': {
            'algorithm': 'WithRetry',
            'timeout': 100,
            'max_retries': max_retries,
        },
    }

    @testpoint('add_points')
    async def add_points(data):
        pass

    response = await taxi_driver_trackstory_adv.post(
        'query/positions', json=request_body,
    )

    assert response.status_code == 200
    assert add_points.times_called == max_retries + 1
    data = response.json()
    assert data == {'results': [[]]}


# checks algorithm returns min of the positions
@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 120, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': True,
            'storage': {'max_age_seconds': 60, 'max_points_count': 30},
        },
    },
)
async def test_min_positions_required_count_check(
        taxi_driver_trackstory_adv, testpoint, now,
):
    @testpoint('ignore_redis')
    def ignore_redis(data):
        return True

    driver_id = 'dbid_uuid'

    # send old point
    timestamp = int(utils.timestamp(now)) * 1000
    drivers = [
        {
            'driver_id': driver_id,
            'position': [55, 37],
            'direction': 45,
            'unix_time': timestamp,
            'speed': 11.666666666666668,
            'accuracy': 1,
            'source': 'AndroidGps',
        },
    ]
    message = geobus.serialize_signal_v2(drivers, now)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        SIGNAL_V2_CHANNEL, message,
    )

    max_retries = 5
    request_body = {
        'driver_ids': [driver_id],
        'max_age': 100,
        'prefered_sources': 'all',
        'parameterized_algorithm': {
            'algorithm': 'WithRetry',
            'timeout': 30,
            'max_retries': max_retries,
            'min_positions_required_count': 1,
        },
    }

    @testpoint('add_points')
    async def add_points(data):
        pass

    response = await taxi_driver_trackstory_adv.post(
        'query/positions', json=request_body,
    )

    assert response.status_code == 200

    assert add_points.times_called == 1

    data = response.json()
    assert len(data['results']) == 1
    assert len(data['results'][0]) == 1
