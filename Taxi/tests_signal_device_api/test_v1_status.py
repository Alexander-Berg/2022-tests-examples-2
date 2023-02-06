# pylint: disable=too-many-lines
import copy
import datetime
import time
import typing

import pytest

from tests_signal_device_api import common

AES_KEY = 'FAEE4CA3C30EE18148CE3ADA374664987D9DD7CC84B0731248B42700E521991E'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
ENDPOINT = 'v1/status'
DEVICE_ID = '13c140cb-7dde-499c-be6e-57c010a45299'
DEVICE_PRIMARY_KEY = 1
CONSUMERS = ['signal_device_api/v1_config']
SERIAL_NUMBER = 'abcdef1234567890'
SERIAL_NUMBER_MISSING = '0000001234567890'
SERIAL_NUMBERS_INVALID_EXPERIMENTS = ['invalid_serial1', 'invalid_serial2']
RESPONSE = {
    'config_fingerprint': (
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    ),
}


def check_status_states(
        pgsql, states_id: typing.Optional[int], states, rows_amount,
):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute('SELECT COUNT(*) FROM signal_device_api.status_states')
    assert list(db)[0][0] == rows_amount

    if states_id is not None:
        db = pgsql['signal_device_api_meta_db'].cursor()
        db.execute(
            'SELECT states FROM signal_device_api.status_states '
            f'WHERE id={states_id}',
        )
        result = list(db)
        assert result
        assert result[0][0] == states


def check_traffic_counters(
        pgsql, sim_imsi, expected_in_bytes, expected_out_bytes,
):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT in_bytes_spent_daily, out_bytes_spent_daily '
        'FROM signal_device_api.sim_traffic '
        f'WHERE imsi=\'{sim_imsi}\' ORDER BY updated_at DESC LIMIT 1',
    )
    result = list(db)
    assert result
    assert (result[0][0], result[0][1]) == (
        expected_in_bytes,
        expected_out_bytes,
    )


def select_uptime_total(pgsql, device_id):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT uptime_total_ms FROM signal_device_api.devices '
        f'WHERE id={device_id}',
    )
    return list(db)[0][0]


def select_status(pgsql, fields, device_public_id):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT {} FROM signal_device_api.statuses '
        'WHERE id=('
        '   SELECT id'
        '   FROM signal_device_api.devices'
        '   WHERE public_id=\'{}\')'.format(
            ','.join(fields), str(device_public_id),
        ),
    )
    return [{k: v for (k, v) in zip(fields, event)} for event in list(db)][0]


def check_no_future_events(pgsql, now):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT EXISTS ('
        'SELECT TRUE '
        'FROM signal_device_api.statuses '
        f'WHERE status_at = \'{now}\')',
    )
    now_event = list(db)[0][0]
    db.execute(
        'SELECT EXISTS ('
        'SELECT TRUE '
        'FROM signal_device_api.statuses '
        f'WHERE status_at > \'{now}\')',
    )
    return now_event and not list(db)[0][0]


def check_status_in_db(pgsql, device_public_id, status, prev_status=None):
    fields = [
        'cpu_temperature',
        'disk_bytes_free_space',
        'disk_bytes_total_space',
        'root_bytes_free_space',
        'root_bytes_total_space',
        'ram_bytes_free_space',
        'gps_position_lat',
        'gps_position_lon',
        'gnss_latitude',
        'gnss_longitude',
        'gnss_speed_kmph',
        'gnss_accuracy_m',
        'gnss_direction_deg',
        'software_version',
        'sim_iccid',
        'sim_imsi',
        'sim_phone_number',
        'uptime_ms',
        'updated_at',
        'position_updated_at',
        'states_id',
    ]
    db_status = select_status(pgsql, fields, device_public_id)
    for field in [
            f
            for f in fields
            if not f.startswith('gps_')
            and not f.startswith('gnss_')
            and not f == 'updated_at'
            and not f == 'position_updated_at'
    ]:
        assert db_status[field] == status[field]
    common.assert_now(db_status['updated_at'])

    if 'gps_position' in status:
        assert db_status['gps_position_lat'] == status['gps_position']['lat']
        assert db_status['gps_position_lon'] == status['gps_position']['lon']
    else:
        if prev_status and 'gps_position' in prev_status:
            assert (
                db_status['gps_position_lat']
                == prev_status['gps_position']['lat']
            )
            assert (
                db_status['gps_position_lon']
                == prev_status['gps_position']['lon']
            )
        else:
            for gps_field in ['gps_position_lat', 'gps_position_lon']:
                assert db_status[gps_field] is None

    if 'gnss' in status:
        assert db_status['gnss_latitude'] == status['gnss']['lat']
        assert db_status['gnss_longitude'] == status['gnss']['lon']
        assert db_status['gnss_speed_kmph'] == status['gnss']['speed_kmph']
        assert db_status['gnss_accuracy_m'] == status['gnss']['accuracy_m']
        assert (
            db_status['gnss_direction_deg'] == status['gnss']['direction_deg']
        )
    else:
        if prev_status and 'gnss' in prev_status:
            assert db_status['gnss_latitude'] == prev_status['gnss']['lat']
            assert db_status['gnss_longitude'] == prev_status['gnss']['lon']
            assert (
                db_status['gnss_speed_kmph']
                == prev_status['gnss']['speed_kmph']
            )
            assert (
                db_status['gnss_accuracy_m']
                == prev_status['gnss']['accuracy_m']
            )
            assert (
                db_status['gnss_direction_deg']
                == prev_status['gnss']['direction_deg']
            )
        else:
            for gnss_field in [
                    'gnss_latitude',
                    'gnss_longitude',
                    'gnss_speed_kmph',
                    'gnss_accuracy_m',
                    'gnss_direction_deg',
            ]:
                assert db_status[gnss_field] is None

        if 'gnss' in status or 'gps_position' in status:
            common.assert_now(db_status['position_updated_at'])


def get_states_info(pgsql):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT day, error_type, duration, is_last_state '
        'FROM signal_device_api.device_error_states ',
    )

    res = {}
    for day, error, duration, is_last_state in list(db):
        if day not in res:
            res[day] = {}
        res[day][error] = (duration, is_last_state)

    return res


STATES1 = {'some_states': {'state1': True, 'state2': False}}
STATES2 = {'some_states': {'state1': False, 'state2': False}}
STATES3 = {'some_states': {'state2': False}}
STATES4 = {'some': False}


@pytest.mark.config(
    SIGNAL_DEVICE_API_LB_STATUSES_PRODUCER_SETTINGS={
        'enabled': True,
        'throw_exception_on_fail': True,
    },
)
@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': [SERIAL_NUMBER_MISSING],
                'arg_name': 'serial_number',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='special_serial_missing',
    consumers=CONSUMERS,
    clauses=[],
    default_value={},
)
@pytest.mark.parametrize(
    'status, new_position, states, is_states_created, is_drive_device',
    [
        (common.make_ok_status(True, True), True, None, False, False),
        (common.make_ok_status(True, True), True, None, False, True),
        (common.make_ok_status(True, True, 1), True, STATES1, False, False),
        (common.make_ok_status(True, True, 4), True, STATES2, True, False),
        (common.make_ok_status(True, True, 3), True, STATES3, False, False),
        (common.make_ok_status(False, True), False, None, False, False),
        (common.make_ok_status(True, False), True, None, False, False),
        (common.make_ok_status(False, False), False, None, False, False),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['status_states.sql'])
async def test_ok(
        taxi_signal_device_api,
        pgsql,
        stq,
        testpoint,
        status,
        new_position,
        states,
        is_states_created,
        is_drive_device,
):
    @testpoint('publish-times-called-check-testpoint')
    def publish_testpoint(arg):
        pass

    @testpoint('logbroker_publish')
    def logbroker_commit(data):
        pass

    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, is_drive_device=is_drive_device,
    )
    json_body = common.make_ok_json_body(status)
    if states is not None:
        json_body['status']['states'] = states
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.json() == RESPONSE
    assert response.status_code == 200

    await publish_testpoint.wait_call()
    if is_drive_device:
        assert logbroker_commit.times_called == 1
    else:
        assert logbroker_commit.times_called == 0

    check_status_in_db(pgsql, DEVICE_ID, status)
    status_states_rows_amount = 4 if is_states_created else 3
    states_id = 4 if is_states_created else None
    check_status_states(
        pgsql=pgsql,
        states_id=states_id,
        states=states,
        rows_amount=status_states_rows_amount,
    )

    # try update

    states_id = 5 if states == STATES2 else 4
    status_2 = {
        'status_at': '2019-04-19T13:50:00Z',
        'cpu_temperature': 66,
        'disk_bytes_free_space': 100929567296,
        'disk_bytes_total_space': 100929567297,
        'root_bytes_free_space': 100929567290,
        'root_bytes_total_space': 100929567291,
        'ram_bytes_free_space': 578150656,
        'software_version': '1.1-1',
        'sim_iccid': '00310410106543789301',
        'sim_imsi': '987654321000',
        'sim_phone_number': '+7 (955) 123-45-67',
        'uptime_ms': 12638176,
        'states_id': states_id,
    }
    if new_position:
        status_2['gps_position'] = {'lat': 55.9885, 'lon': 76.3242}

    request_status = copy.deepcopy(status_2)
    request_status.pop('states_id')
    request_status['states'] = STATES4
    json_body_2 = {
        'device_id': DEVICE_ID,
        'timestamp': '2019-04-19T13:39:00Z',
        'status': request_status,
    }
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body_2,
            ),
        },
        json=json_body_2,
    )
    assert response.status_code == 200, response.text
    assert response.json() == RESPONSE
    check_status_in_db(pgsql, DEVICE_ID, status_2, status)
    check_status_states(
        pgsql=pgsql,
        states_id=states_id,
        states=STATES4,
        rows_amount=status_states_rows_amount + 1,
    )

    assert (
        stq.signal_device_api_tags.times_called == 0
    )  # no bindings – no tag requests


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='test_experiments_default',
    consumers=CONSUMERS,
    clauses=[
        {
            'title': 'experiment_invalid_serial_list',
            'value': common.SIMPLE_CONFIG,
            'predicate': {
                'init': {
                    'set': SERIAL_NUMBERS_INVALID_EXPERIMENTS,
                    'arg_name': 'serial_number',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
        {
            'title': 'experiment_default',
            'value': common.COMPLEX_CONFIG,
            'predicate': {'type': 'true'},
        },
    ],
    default_value=common.SIMPLE_CONFIG,
)
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_experiments_default(taxi_signal_device_api, pgsql):
    status = common.make_ok_status(True, True)
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    json_body = common.make_ok_json_body(status)
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'config_fingerprint': (
            '759485f8beadff787cee1f7bc7fa18453cac61e3d1c7abe9d0c87d906dcff0cb'
        ),
    }
    check_status_in_db(pgsql, DEVICE_ID, status)


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='test_experiments_serial_match',
    consumers=CONSUMERS,
    clauses=[
        {
            'title': 'experiment_invalid_serial_list',
            'value': common.COMPLEX_CONFIG,
            'predicate': {
                'init': {
                    'set': [SERIAL_NUMBER],
                    'arg_name': 'serial_number',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
        {
            'title': 'experiment_default',
            'value': common.SIMPLE_CONFIG,
            'predicate': {'type': 'true'},
        },
    ],
    default_value=common.SIMPLE_CONFIG,
)
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_experiments_serial_match(taxi_signal_device_api, pgsql):
    status = common.make_ok_status(True, True)
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, serial_number=SERIAL_NUMBER,
    )
    json_body = common.make_ok_json_body(status)
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'config_fingerprint': (
            'e8c68ddaf0c5b7796cd84b33aeaf0cbcd59c2b869ae004ac816c39d6e8f5bc73'
        ),
    }
    check_status_in_db(pgsql, DEVICE_ID, status)


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_unregistered_device(taxi_signal_device_api):
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.MISSING_JWT_HEADER_FOR_UNREGISTERED,
        json=common.make_ok_json_body(common.make_ok_status()),
    )
    assert response.json() == common.response_400_not_registered(DEVICE_ID)
    assert response.status_code == 400


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_dead_device(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, False,
    )
    json_body = common.make_ok_json_body(common.make_ok_status())
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 400, response.text
    assert response.json() == common.response_400_not_alive(DEVICE_ID)


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_403(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    json_body = common.make_ok_json_body(common.make_ok_status())
    jwt = common.generate_jwt(private_key, ENDPOINT, {}, json_body)
    mutated_jwt = jwt[:-8] + 'AAAAAAAA'
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={common.JWT_HEADER_NAME: mutated_jwt},
        json=json_body,
    )
    assert response.status_code == 403, response.text
    assert response.json() == common.RESPONSE_403_INVALID_SIGNATURE


@pytest.mark.parametrize(
    'device_pk, should_append_tag, was_tag_active, should_append_night_tag',
    [
        (1, False, False, False),
        (2, True, False, True),
        (3, False, False, False),
        (4, True, False, False),
        (5, True, False, False),
        (6, True, False, False),
        (7, False, True, True),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', ['car_binding.sql'])
@pytest.mark.now('2020-03-02T01:00:00+00:00')
async def test_stq_tags(
        taxi_signal_device_api,
        pgsql,
        stq,
        stq_runner,
        mockserver,
        device_pk,
        should_append_tag,
        was_tag_active,
        should_append_night_tag,
):
    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        assert 'remove' not in request.json
        assert append['entity_type'] == 'park_car_id'
        assert (
            len(append['tags']) == should_append_tag + should_append_night_tag
        )
        if should_append_tag:
            assert {
                'name': 'car_with_signalq_online',
                'entity': f'p1_car{device_pk}',
            } in append['tags']
        if should_append_night_tag:
            assert {
                'name': 'car_with_signalq_online_night',
                'until': '2019-04-19T02:00:00+0000',
                'entity': f'p1_car{device_pk}',
            } in append['tags']
        return {}

    assert was_tag_active == common.get_is_tag_active(
        pgsql, park_id='p1', car_id=f'car{device_pk}',
    )

    status_at = '2019-04-19T13:37:00Z'
    if should_append_night_tag:
        status_at = '2019-04-19T01:00:00Z'
    status = common.make_ok_status(
        is_gps_included=True, is_gnss_included=True, status_at=status_at,
    )
    private_key = common.add_device_return_private_key(
        pgsql, device_pk, DEVICE_ID,
    )
    json_body = common.make_ok_json_body(status)
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200

    if not should_append_tag and not should_append_night_tag:
        assert stq.signal_device_api_tags.times_called == 0
        return

    assert stq.signal_device_api_tags.times_called == 1
    tags_call = stq.signal_device_api_tags.next_call()
    await stq_runner.signal_device_api_tags.call(
        task_id=tags_call['id'],
        args=tags_call['args'],
        kwargs=tags_call['kwargs'],
    )
    assert _tags.times_called == 1
    assert common.get_is_tag_active(
        pgsql, park_id='p1', car_id=f'car{device_pk}',
    )


SECONDS_IN_WEEK = 604800


@pytest.mark.pgsql('signal_device_api_meta_db')
@pytest.mark.parametrize(
    'gnss_timestamp',
    [
        None,
        (int(time.time()) - 2),  # slightly in the past
        1607694064,  # more than a week in the past
        -1,  # some shit
    ],
)
async def test_gnss_timestamp(taxi_signal_device_api, gnss_timestamp, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    status = {
        'status_at': '2019-04-19T13:50:00Z',
        'cpu_temperature': 66,
        'disk_bytes_free_space': 100929567296,
        'disk_bytes_total_space': 100929567297,
        'root_bytes_free_space': 100929567290,
        'root_bytes_total_space': 100929567291,
        'ram_bytes_free_space': 578150656,
        'software_version': '1.1-1',
        'sim_iccid': '00310410106543789301',
        'sim_imsi': '987654321000',
        'sim_phone_number': '+7 (955) 123-45-67',
        'uptime_ms': 12638176,
        'gnss': {
            'lat': 99,
            'lon': 199,
            'speed_kmph': 4.4,
            'accuracy_m': 3.3,
            'direction_deg': 5.5,
        },
    }
    if gnss_timestamp:
        status['gnss']['timestamp'] = gnss_timestamp

    json_body = {
        'device_id': DEVICE_ID,
        'timestamp': '2019-04-19T13:39:00Z',
        'status': status,
    }
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200, response.text
    status_stored = select_status(pgsql, ['position_updated_at'], DEVICE_ID)
    assert 'position_updated_at' in status_stored
    lower_bound = int(time.time()) - SECONDS_IN_WEEK
    upper_bound = int(time.time()) + SECONDS_IN_WEEK
    if gnss_timestamp and lower_bound <= gnss_timestamp <= upper_bound:
        assert (
            int(status_stored['position_updated_at'].timestamp())
            == gnss_timestamp
        )
    else:
        assert (
            int(status_stored['position_updated_at'].timestamp())
            != gnss_timestamp
        )


async def test_total_uptime(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    status = {
        'status_at': '2019-04-19T13:50:00Z',
        'cpu_temperature': 66,
        'disk_bytes_free_space': 100929567296,
        'disk_bytes_total_space': 100929567297,
        'root_bytes_free_space': 100929567290,
        'root_bytes_total_space': 100929567291,
        'ram_bytes_free_space': 578150656,
        'software_version': '1.1-1',
        'sim_iccid': '00310410106543789301',
        'sim_imsi': '987654321000',
        'sim_phone_number': '+7 (955) 123-45-67',
        'uptime_ms': 12638176,
        'gnss': {
            'lat': 99,
            'lon': 199,
            'speed_kmph': 4.4,
            'accuracy_m': 3.3,
            'direction_deg': 5.5,
        },
    }

    json_body = {
        'device_id': DEVICE_ID,
        'timestamp': '2019-04-19T13:39:00Z',
        'status': status,
    }
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )

    assert response.status_code == 200, response.text
    uptime_total = select_uptime_total(pgsql, DEVICE_PRIMARY_KEY)
    assert uptime_total == 12638176

    # increment
    json_body['status']['uptime_ms'] += 42
    json_body['status']['status_at'] = '2019-04-19T13:51:00Z'
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )

    assert response.status_code == 200, response.text
    uptime_total = select_uptime_total(pgsql, DEVICE_PRIMARY_KEY)
    assert uptime_total == 12638218

    # reboot
    json_body['status']['uptime_ms'] = 100
    json_body['status']['status_at'] = '2019-04-19T13:52:00Z'
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )

    assert response.status_code == 200, response.text
    uptime_total = select_uptime_total(pgsql, DEVICE_PRIMARY_KEY)
    assert uptime_total == 12638318

    # retry same status
    json_body['status']['uptime_ms'] = 100
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )

    assert response.status_code == 200, response.text
    uptime_total = select_uptime_total(pgsql, DEVICE_PRIMARY_KEY)
    assert uptime_total == 12638318  # not changed

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT COUNT(DISTINCT status_at) '
        'FROM signal_device_api.status_history '
        f'WHERE device_id={DEVICE_PRIMARY_KEY}',
    )
    assert list(db)[0][0] == 3


@pytest.mark.pgsql('signal_device_api_meta_db')
@pytest.mark.parametrize(
    'upload_queue',
    [
        {'photo': 0, 'video': 0, 'log': 0},
        {'photo': 31, 'video': 15, 'log': 22},
        {'photo': 42, 'video': 23, 'log': 32, 'event': 11},
    ],
)
async def test_upload_queue(taxi_signal_device_api, upload_queue, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    status = {
        'status_at': '2019-04-19T13:50:00Z',
        'cpu_temperature': 66,
        'disk_bytes_free_space': 100929567296,
        'disk_bytes_total_space': 100929567297,
        'root_bytes_free_space': 100929567290,
        'root_bytes_total_space': 100929567291,
        'ram_bytes_free_space': 578150656,
        'software_version': '1.1-1',
        'sim_iccid': '00310410106543789301',
        'sim_imsi': '987654321000',
        'sim_phone_number': '+7 (955) 123-45-67',
        'uptime_ms': 12638176,
        'gnss': {
            'lat': 79,
            'lon': 179,
            'speed_kmph': 4.4,
            'accuracy_m': 3.3,
            'direction_deg': 5.5,
        },
    }

    status['upload_queue'] = upload_queue

    json_body = {
        'device_id': DEVICE_ID,
        'timestamp': '2019-04-19T13:39:00Z',
        'status': status,
    }
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200, response.text
    upload_queue_stored = select_status(
        pgsql,
        [
            'upload_queue_photo',
            'upload_queue_video',
            'upload_queue_log',
            'upload_queue_event',
        ],
        DEVICE_ID,
    )
    assert 'upload_queue_photo' in upload_queue_stored
    assert 'upload_queue_video' in upload_queue_stored
    assert 'upload_queue_log' in upload_queue_stored
    assert 'upload_queue_event' in upload_queue_stored
    assert upload_queue_stored['upload_queue_photo'] == upload_queue['photo']
    assert upload_queue_stored['upload_queue_video'] == upload_queue['video']
    assert upload_queue_stored['upload_queue_log'] == upload_queue['log']
    assert (
        upload_queue_stored['upload_queue_event'] == upload_queue.get('event')
        or '0'
    )

    # check update upload_queue_photo and upload_queue_event with same id
    status['status_at'] = '2019-04-19T13:52:00Z'
    status['upload_queue'] = copy.deepcopy(upload_queue)
    json_body['status'] = status
    json_body['status']['upload_queue']['photo'] += 1
    if json_body['status']['upload_queue'].get('event') is not None:
        json_body['status']['upload_queue']['event'] += 2
    else:
        json_body['status']['upload_queue']['event'] = 2
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200, response.text
    upload_queue_stored = select_status(
        pgsql, ['upload_queue_photo', 'upload_queue_event'], DEVICE_ID,
    )
    assert 'upload_queue_photo' in upload_queue_stored
    assert (
        upload_queue_stored['upload_queue_photo'] == upload_queue['photo'] + 1
    )
    if upload_queue.get('event') is not None:
        new_upload_queue_event = upload_queue.get('event') + 2
    else:
        new_upload_queue_event = 2
    assert upload_queue_stored['upload_queue_event'] == new_upload_queue_event


ERROR_STATES = [
    {'dms.analytics.CameraPose': False},
    {'dms.analytics.CameraPose': False, 'dms.analytics.TrashFrames': True},
    {'dms.analytics.CameraPose': True, 'dms.analytics.TrashFrames': True},
    {'dms.analytics.CameraPose': True, 'dms.analytics.TrashFrames': False},
]

ERROR_STATUSES = [
    common.make_ok_status(False, False, 5, '2021-08-31T23:30:00+03:00'),
    common.make_ok_status(False, False, 6, '2021-08-31T23:57:00+03:00'),
    common.make_ok_status(False, False, 6, '2021-09-01T00:03:00+03:00'),
    common.make_ok_status(False, False, 6, '2021-09-01T00:07:00+03:00'),
]

EXPECTED_DURATIONS_0 = {
    datetime.date(2021, 8, 31): {
        'bad_camera_pose': (datetime.timedelta(seconds=0), True),
    },
}

EXPECTED_DURATIONS_1 = {
    datetime.date(2021, 8, 31): {
        'bad_camera_pose': (datetime.timedelta(seconds=300), True),
    },
}

EXPECTED_DURATIONS_2 = {
    datetime.date(2021, 8, 31): {
        'bad_camera_pose': (datetime.timedelta(seconds=480), False),
    },
    datetime.date(2021, 9, 1): {
        'bad_camera_pose': (datetime.timedelta(seconds=120), False),
        'trash_frames': (datetime.timedelta(seconds=0), True),
    },
}

EXPECTED_DURATIONS_3 = {
    datetime.date(2021, 8, 31): {
        'bad_camera_pose': (datetime.timedelta(seconds=480), False),
    },
    datetime.date(2021, 9, 1): {
        'bad_camera_pose': (datetime.timedelta(seconds=120), False),
        'trash_frames': (datetime.timedelta(seconds=240), False),
    },
}

EXPECTED_DURATIONS = [
    EXPECTED_DURATIONS_0,
    EXPECTED_DURATIONS_1,
    EXPECTED_DURATIONS_2,
    EXPECTED_DURATIONS_3,
]


@pytest.mark.pgsql('signal_device_api_meta_db', files=['status_states.sql'])
async def test_v1_status_error_durations(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, aes_key=AES_KEY,
    )
    for i, error_status in enumerate(ERROR_STATUSES):
        json_body = common.make_ok_json_body(error_status)
        json_body['status']['states'] = ERROR_STATES[i]
        await taxi_signal_device_api.post(
            ENDPOINT,
            headers={
                common.JWT_HEADER_NAME: common.generate_jwt(
                    private_key, ENDPOINT, {}, json_body,
                ),
            },
            json=json_body,
        )

        assert EXPECTED_DURATIONS[i] == get_states_info(
            pgsql,
        ), f'iteration number {i}'


@pytest.mark.config(SIGNAL_DEVICE_API_ADDITIONAL_LOGS_FOR_TRAFFIC=True)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['car_binding.sql'])
@pytest.mark.now('2020-03-02T01:00:00+00:00')
@pytest.mark.parametrize(
    'sim_imsi, in_bytes, out_bytes, in_bytes_delta, out_bytes_delta, '
    'expected_in_bytes, expected_out_bytes, ',
    [
        # first day started
        ('imsi_1', 10, 30, 10, 30, 10, 30),
        # reboot happend
        ('imsi_2', 100, 30, 100, 30, 100, 1030),
        # new day started, first day exists
        ('imsi_3', 100, 200, 100, 200, 100, 200),
        # the 1st status after internet connection loss
        ('imsi_4', 150, 800, 150, 800, 150, 800),
        # the 2nd status after internet connection loss
        ('imsi_5', 40, 60, 10, 30, 120, 360),
        # day started with offset
        ('imsi_6', 240, 490, 10, 30, 40, 90),
    ],
)
async def test_traffic_counters(
        taxi_signal_device_api,
        pgsql,
        sim_imsi,
        in_bytes,
        out_bytes,
        in_bytes_delta,
        out_bytes_delta,
        expected_in_bytes,
        expected_out_bytes,
):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    lte_traffic = {
        'in_bytes': in_bytes,
        'out_bytes': out_bytes,
        'in_bytes_delta': in_bytes_delta,
        'out_bytes_delta': out_bytes_delta,
    }
    json_body = common.make_ok_json_body(
        common.make_ok_status(sim_imsi=sim_imsi, lte_traffic=lte_traffic),
    )
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200, response.text
    assert response.json() == RESPONSE
    check_traffic_counters(
        pgsql, sim_imsi, expected_in_bytes, expected_out_bytes,
    )


@pytest.mark.now('2020-03-02T01:00:00+00:00')
async def test_status_at(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    json_body = common.make_ok_json_body(
        common.make_ok_status(
            status_at='2020-03-02T15:00:00+00:00',  # noqa E501
        ),
    )
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200, response.text
    assert response.json() == RESPONSE
    assert check_no_future_events(pgsql, '2020-03-02T01:00:00+00:00')
