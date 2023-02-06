import dataclasses

import pytest

from tests_signal_device_configs import web_common

ENDPOINT = 'fleet/signal-device-configs/v1/events/fixated'

IDEMPOTENCY_TOKEN = 'afm2klskafm2klskafm2klsk'


@dataclasses.dataclass(frozen=True)
class TableCounts:
    events_fixated: int
    patches: int
    device_patches: int


def get_table_counts(pgsql, need_increment=False) -> TableCounts:
    db = pgsql['signal_device_configs'].cursor()
    query = f"""
      SELECT
        (SELECT COUNT(*)
         FROM signal_device_configs.events_fixated),
        (SELECT COUNT(*)
         FROM signal_device_configs.patches),
        (SELECT COUNT(*)
         FROM signal_device_configs.device_patches)
    """
    db.execute(query)
    db_res = list(db)[0]
    if not need_increment:
        return TableCounts(db_res[0], db_res[1], db_res[2])
    return TableCounts(db_res[0] + 1, db_res[1] + 1, db_res[2] + 1)


def select_events_fixated(pgsql, *, park_id):
    db = pgsql['signal_device_configs'].cursor()
    query = f"""
      SELECT ef.event_types
      FROM signal_device_configs.events_fixated ef
      WHERE ef.park_id = '{park_id}'
    """
    db.execute(query)
    result = list(db)
    assert len(result) == 1
    return result[0][0]


def select_events_patch_for_park(pgsql, *, park_id):
    db = pgsql['signal_device_configs'].cursor()
    query = f"""
      SELECT p.id, p.patch, p.action_history
      FROM signal_device_configs.patches p
      JOIN signal_device_configs.device_patches dp
      ON p.id = dp.patch_id
      WHERE dp.park_id = '{park_id}' AND dp.config_name = 'features.json'
    """
    db.execute(query)
    result = list(db)
    if not result:
        return None
    assert len(result) == 1
    return result[0]


def select_patch_by_id(pgsql, *, patch_id):
    db = pgsql['signal_device_configs'].cursor()
    query = f"""
      SELECT id, patch, action_history
      FROM signal_device_configs.patches
      WHERE id = '{patch_id}'
    """
    db.execute(query)
    result = list(db)
    if not result:
        return None
    return result[0]


def select_features_patch_info(pgsql, park_id):
    db = pgsql['signal_device_configs'].cursor()
    query = f"""
      SELECT
        dp.park_id,
        dp.config_name,
        dp.idempotency_token,
        dp.patch_id,
        p.patch
      FROM signal_device_configs.device_patches dp
      JOIN signal_device_configs.patches p
      ON (dp.patch_id = p.id)
      WHERE dp.park_id = '{park_id}'
            AND dp.config_name = 'features.json'
    """
    db.execute(query)
    result = list(db)
    assert len(result) == 1
    return result[0]


def select_last_added_preset(pgsql):
    db = pgsql['signal_device_configs'].cursor()
    query = f"""
      SELECT patch
      FROM signal_device_configs.patch_presets
      ORDER BY updated_at DESC
      LIMIT 1
    """
    db.execute(query)
    result = list(db)
    if not result:
        return None
    return result[0][0]


async def set_events_fixated(
        pgsql,
        taxi_signal_device_configs,
        park_id,
        event_types,
        idempotency_token=IDEMPOTENCY_TOKEN,
):
    headers = {
        **web_common.YA_TEAM_HEADERS,
        'X-Park-Id': park_id,
        'X-Idempotency-Token': 'some_idempotency_token',
    }
    body = {'event_types': event_types}
    response = await taxi_signal_device_configs.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 200
    return response


WHITELIST = [
    {
        'event_type': 'tired',
        'is_critical': True,
        'is_violation': False,
        'fixation_config_path': 'drowsiness.events.tired.enabled',
    },
    {
        'event_type': 'smoking',
        'is_critical': False,
        'is_violation': False,
        'fixation_config_path': 'smoking.events.smoking.enabled',
    },
    {
        'event_type': 'seatbelt',
        'is_critical': False,
        'is_violation': False,
        'fixation_config_path': 'seatbelt.events.seatbelt.enabled',
    },
    {
        'event_type': 'distraction',
        'is_critical': True,
        'is_violation': False,
        'fixation_config_path': 'distraction.events.distraction.enabled',
    },
    {
        'event_type': 'bad_camera_pose',
        'is_critical': False,
        'is_violation': False,
        'fixation_config_path': 'general.events.bad_camera_pose.enabled',
    },
    {
        'event_type': 'alarm',
        'is_critical': False,
        'is_violation': False,
        'fixation_config_path': 'general.events.alarm.enabled',
    },
]


def add_nested_objects_by_paths(json, paths, idx):
    if idx == len(paths) - 1:
        json[paths[idx]] = False
        return
    if json.get(paths[idx]) is None:
        json[paths[idx]] = {}
    add_nested_objects_by_paths(json[paths[idx]], paths, idx + 1)


def make_patch_from_event_types(event_types):
    patch = {}
    for item in WHITELIST:
        if item['event_type'] not in event_types:
            add_nested_objects_by_paths(
                patch, item['fixation_config_path'].split('.'), 0,
            )
    return patch


def test_make_patch():
    assert make_patch_from_event_types(['smoking', 'distraction']) == {
        'drowsiness': {'events': {'tired': {'enabled': False}}},
        'seatbelt': {'events': {'seatbelt': {'enabled': False}}},
        'general': {
            'events': {
                'bad_camera_pose': {'enabled': False},
                'alarm': {'enabled': False},
            },
        },
    }


def make_request_body(event_types):
    result = []
    for item in WHITELIST:
        if item['event_type'] not in event_types:
            result.append(item['event_type'])
    return result


DUPLICATE_IDEMPOTENCY_TOKEN = 'some_idempotency_token0'


@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
@pytest.mark.config(SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=WHITELIST)
@pytest.mark.parametrize(
    'park_id, event_types, idempotency_token, are_new_rows, response_code',
    [
        ('p1', ['tired', 'smoking'], DUPLICATE_IDEMPOTENCY_TOKEN, False, 200),
        ('p1', ['tired', 'smoking'], 'some_idempotency_new_1', False, 200),
        (
            'p3',
            ['tired', 'smoking', 'bad_camera_pose'],
            'some_idempotency_new_1',
            True,
            200,
        ),
        (
            'p1',
            ['distraction', 'unreal_event_type'],
            IDEMPOTENCY_TOKEN,
            False,
            400,
        ),
    ],
)
async def test_events_fixated_post(
        taxi_signal_device_configs,
        pgsql,
        park_id,
        event_types,
        are_new_rows,
        idempotency_token,
        response_code,
):
    prev_patch = None
    if idempotency_token == DUPLICATE_IDEMPOTENCY_TOKEN:
        prev_patch = select_features_patch_info(pgsql=pgsql, park_id=park_id)

    prev_table_counts = get_table_counts(
        pgsql=pgsql, need_increment=are_new_rows,
    )
    headers = {
        **web_common.YA_TEAM_HEADERS,
        'X-Park-Id': park_id,
        'X-Idempotency-Token': idempotency_token,
    }

    body = {'event_types': event_types}
    response = await taxi_signal_device_configs.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == response_code
    if response.status_code == 400:
        return

    curr_table_counts = get_table_counts(pgsql=pgsql)
    assert prev_table_counts == curr_table_counts

    if idempotency_token == DUPLICATE_IDEMPOTENCY_TOKEN:
        assert prev_patch == select_features_patch_info(
            pgsql=pgsql, park_id=park_id,
        )
        return

    assert select_events_fixated(pgsql=pgsql, park_id=park_id) == event_types
    new_patch = select_features_patch_info(pgsql=pgsql, park_id=park_id)
    assert new_patch[0] == park_id
    assert new_patch[1] == 'features.json'
    assert new_patch[4] == make_patch_from_event_types(event_types)


PARK_ID_EXISTING_PATCH1 = 'p7'
PARK_ID_EXISTING_PATCH2 = 'p10'
PARK_ID_NO_PATCH = 'p8'
PARK_ID_NO_HISTORY = 'p11'
PARK_ID_NO_ONLY_EVENTS = 'p12'
PARK_ID_NO_EVENTS = 'p13'

EXISTING_EVENT_TYPES1 = ['bad_camera_pose', 'distraction']
EXISTING_EVENT_TYPES2 = ['distraction']
NEW_EVENT_TYPES = ['alarm', 'bad_camera_pose']
NON_EXISTING_EVENT_TYPES = ['some_event']

EXISTING_PATCH_ID1 = 7
EXISTING_PATCH_ID2 = 8
EXISTING_PATCH_ID_NO_HISTORY = 9
EXISTING_PATCH_ID_NOT_ONLY_EVENTS = 10
EXISTING_PATCH_ID_NO_EVENTS = 11


# change existing patch
@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
@pytest.mark.config(SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=WHITELIST)
async def test_events_patching_existing_patch(
        pgsql, taxi_signal_device_configs,
):
    park_id = PARK_ID_EXISTING_PATCH1
    old_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)
    body = make_request_body(EXISTING_EVENT_TYPES1)
    assert old_patch is not None
    await set_events_fixated(
        pgsql=pgsql,
        taxi_signal_device_configs=taxi_signal_device_configs,
        park_id=park_id,
        event_types=body,
    )
    new_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)
    assert old_patch[1] == new_patch[1]


# delete existing patch, use existing
@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
@pytest.mark.config(SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=WHITELIST)
async def test_events_patching_replace_with_existing(
        pgsql, taxi_signal_device_configs,
):
    park_id = PARK_ID_EXISTING_PATCH1
    old_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)
    assert old_patch is not None
    assert old_patch[1] == make_patch_from_event_types(
        make_request_body(EXISTING_EVENT_TYPES1),
    )
    body = make_request_body(EXISTING_EVENT_TYPES2)
    await set_events_fixated(
        pgsql=pgsql,
        taxi_signal_device_configs=taxi_signal_device_configs,
        park_id=park_id,
        event_types=body,
    )
    new_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)
    assert new_patch[1] == make_patch_from_event_types(body)


# delete existing patch, create new
@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
@pytest.mark.config(SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=WHITELIST)
async def test_events_patching_replace_with_new(
        pgsql, taxi_signal_device_configs,
):
    park_id = PARK_ID_EXISTING_PATCH2
    old_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)
    assert old_patch is not None
    assert old_patch[0] == EXISTING_PATCH_ID2
    body = make_request_body(NEW_EVENT_TYPES)
    await set_events_fixated(
        pgsql=pgsql,
        taxi_signal_device_configs=taxi_signal_device_configs,
        park_id=park_id,
        event_types=body,
    )
    new_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)
    assert new_patch[1] == make_patch_from_event_types(body)
    assert len(new_patch[2]) == len(NEW_EVENT_TYPES)

    deleted_patch = select_patch_by_id(pgsql=pgsql, patch_id=old_patch[0])
    assert deleted_patch is None


@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
@pytest.mark.config(SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=WHITELIST)
async def test_events_patching_old_patch_format(
        pgsql, taxi_signal_device_configs,
):
    park_id = PARK_ID_NO_HISTORY
    event_types = ['tired', 'smoking']
    old_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)
    assert old_patch is not None
    assert old_patch[0] == EXISTING_PATCH_ID_NO_HISTORY
    body = make_request_body(event_types)
    await set_events_fixated(
        pgsql=pgsql,
        taxi_signal_device_configs=taxi_signal_device_configs,
        park_id=park_id,
        event_types=body,
    )
    new_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)
    assert new_patch[1] == make_patch_from_event_types(body)
    assert len(new_patch[2]) == len(event_types)


# create new preset
@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=(
        WHITELIST
        + [
            {
                'event_type': 'some_event',
                'is_critical': False,
                'is_violation': False,
                'fixation_config_path': 'general.events.some_event.enabled',
            },
        ]
    ),
)
async def test_event_patching_create_preset(pgsql, taxi_signal_device_configs):
    park_id = PARK_ID_NO_PATCH
    old_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)
    assert old_patch is None
    body = make_request_body(NON_EXISTING_EVENT_TYPES)
    await set_events_fixated(
        pgsql=pgsql,
        taxi_signal_device_configs=taxi_signal_device_configs,
        park_id=park_id,
        event_types=body,
    )
    new_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)
    assert new_patch[1] == {
        'general': {'events': {'some_event': {'enabled': False}}},
    }
    assert len(new_patch[2]) == 1

    last_preset = select_last_added_preset(pgsql=pgsql)
    print(last_preset)
    assert last_preset == [
        {
            'name': 'features.json',
            'update': {
                'general': {'events': {'some_event': {'enabled': False}}},
            },
        },
    ]


@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
@pytest.mark.config(SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=WHITELIST)
async def test_events_patching_not_only_events(
        pgsql, taxi_signal_device_configs,
):
    park_id = PARK_ID_NO_ONLY_EVENTS
    event_types = NEW_EVENT_TYPES
    old_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)
    assert old_patch is not None
    assert old_patch[0] == EXISTING_PATCH_ID_NOT_ONLY_EVENTS
    body = make_request_body(event_types)
    await set_events_fixated(
        pgsql=pgsql,
        taxi_signal_device_configs=taxi_signal_device_configs,
        park_id=park_id,
        event_types=body,
    )
    new_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)

    true_patch = make_patch_from_event_types(body)
    true_patch['stream_meta'] = True

    assert new_patch[1] == true_patch
    assert len(new_patch[2]) == len(event_types) + 1


@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
@pytest.mark.config(SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=WHITELIST)
async def test_events_patching_no_events(pgsql, taxi_signal_device_configs):
    park_id = PARK_ID_NO_EVENTS
    event_types = NEW_EVENT_TYPES
    old_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)
    assert old_patch is not None
    assert old_patch[0] == EXISTING_PATCH_ID_NO_EVENTS
    body = make_request_body(event_types)
    await set_events_fixated(
        pgsql=pgsql,
        taxi_signal_device_configs=taxi_signal_device_configs,
        park_id=park_id,
        event_types=body,
    )
    new_patch = select_events_patch_for_park(pgsql=pgsql, park_id=park_id)

    true_patch = make_patch_from_event_types(body)
    true_patch['stream_meta'] = True

    assert new_patch[1] == true_patch
    assert len(new_patch[2]) == len(event_types) + 1
