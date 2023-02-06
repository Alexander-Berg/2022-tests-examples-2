import copy
import datetime
import json

import pytest

from taxi.util import dates

from workforce_management.common import utils
from workforce_management.storage.postgresql import db
from workforce_management.storage.postgresql import utils as pg_utils


URI = 'v1/schedule/types/modify'
SCHEDULES = {
    1: {
        'active': True,
        'duration_minutes': 720,
        'first_weekend': False,
        'schedule': [2, 2],
        'schedule_alias': '2x2/12:00-00:00',
        'schedule_type_id': 1,
        'start': datetime.time(12, 0),
        'properties': {'performance_standard': 480},
    },
    2: {
        'active': True,
        'duration_minutes': 840,
        'first_weekend': False,
        'schedule': [5, 2],
        'schedule_alias': '5x2/10:00-00:00',
        'schedule_type_id': 2,
        'start': datetime.time(10, 0),
        'properties': {'performance_standard': 420},
    },
    5: {
        'active': True,
        'schedule_type_id': 5,
        'schedule_alias': '5x2/10:00-00:00',
        'schedule': [2, 3],
        'schedule_by_minutes': [3480, 420, 1020, 420, 1020, 420, 420],
        'first_weekend': True,
        'start': datetime.time(10),
        'duration_minutes': 60 * 7,
    },
}
REVISION_ID = '2020-08-26T09:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-08-26T13:00:00.000000 +0000'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


@pytest.mark.pgsql(
    'workforce_management',
    files=['schedule_types.sql', 'extra_schedule_types.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        pytest.param(
            {
                'schedule_type_id': 1,
                'schedule_alias': '5x2/10:00-00:00',
                'properties': {'performance_standard': 480},
                'revision_id': REVISION_ID,
                'absolute_start': '2022-01-01T00:00:00Z',
                'active': False,
            },
            200,
            id='modify properties',
        ),
        pytest.param(
            {
                'schedule_type_id': 1,
                'schedule_alias': '5x2/10:00-00:00',
                'rotation_type': 'weekly',
                'revision_id': REVISION_ID,
                'offset_settings': [
                    {
                        'oebs_alias': (
                            'we really do love to build confusing systems'
                        ),
                        'offset_alias': 'bla bla',
                        'offset': 2,
                    },
                ],
            },
            200,
            id='modify schedule type',
        ),
        pytest.param(
            {'schedule_type_id': 1, 'schedule_alias': '5x2/10:00-00:00'},
            409,
            id='missing revision',
        ),
        pytest.param(
            {
                'schedule_type_id': 1,
                'schedule_alias': '5x2/10:00-00:00',
                'revision_id': WRONG_REVISION_ID,
            },
            409,
            id='wrong revision',
        ),
        pytest.param(
            {
                'schedule_alias': '5x2/10:00-00:00',
                'schedule': [2, 3],
                'first_weekend': True,
                'start': '10:00:00',
                'duration_minutes': 60 * 7,
                'rotation_type': 'sequentially',
            },
            200,
            id='create new schedule type',
        ),
        pytest.param(
            {
                'schedule_type_id': 5,
                'schedule_alias': '5x2/10:00-00:00',
                'schedule': [2, 3],
                'first_weekend': True,
                'rotation_type': 'weekly',
                'start': '10:00:00',
                'duration_minutes': 60 * 7,
            },
            400,
            id='',
        ),
        pytest.param(
            {
                'schedule_alias': '5x2/10:00-00:00',
                'schedule_by_minutes': [200, 300],
                'rotation_type': 'sequentially',
            },
            200,
            id='create new schedule type',
        ),
        pytest.param(
            {
                'schedule_alias': '5x2/10:00-00:00',
                'rotation_type': 'weekly',
                'schedule_by_minutes': [200, 300],
            },
            400,
            id='wrong rotation type',
        ),
        pytest.param(
            {
                'schedule_type_id': 11,
                'schedule_alias': '10:00-19:00',
                'schedule_by_minutes': [600, 540, 300],
                'rotation_type': 'sequentially',
            },
            400,
            id='duplicate parameters vs extra',
        ),
        pytest.param(
            {
                'schedule_alias': '10:00-19:00',
                'schedule_by_minutes': [600, 540, 300],
                'rotation_type': 'sequentially',
            },
            400,
            id='duplicate schedule type',
        ),
        pytest.param({}, 400, id='empty params'),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    body = await res.json()
    if tst_request.get('schedule_type_id'):
        assert body['schedule_type_id'] == tst_request['schedule_type_id']

    if 'schedule_type_id' not in tst_request:
        return

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master

    async with master_pool.acquire() as conn:
        res = await operators_db.get_schedule_types(
            conn, schedule_type_ids=[tst_request['schedule_type_id']],
        )
        tst_request.pop('revision_id', None)
        existing_schedule = SCHEDULES.get(tst_request['schedule_type_id'], {})
        if tst_request.get('start'):
            tst_request['start'] = datetime.time.fromisoformat(
                tst_request['start'],
            )
        if tst_request.get('absolute_start'):
            tst_request['absolute_start'] = dates.localize(
                dates.parse_timestring(tst_request['absolute_start']),
            )
        schedule = copy.deepcopy(existing_schedule)
        schedule.update(tst_request)
        assert len(res) == 1
        parsed_res = utils.skip_none(pg_utils.row_to_json(res[0]))
        parsed_res.pop('updated_at')
        for json_field in ('properties', 'offset_settings'):
            if parsed_res.get(json_field):
                parsed_res[json_field] = json.loads(parsed_res[json_field])
        filtered_res = utils.obj_to_dict([parsed_res], schedule)[0]
        assert filtered_res == schedule


@pytest.mark.pgsql('workforce_management', files=['schedule_types.sql'])
async def test_modify_existing(taxi_workforce_management_web):
    res = await taxi_workforce_management_web.post(
        'v1/schedule/types', json={'durations_minutes': [12 * 60]},
    )
    assert res.status == 200

    data = await res.json()
    assert len(data['schedule_types']) == 1
    tst_request = data['schedule_types'][0]
    tst_request.update({'schedule': [3, 2]})
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == 200

    res = await taxi_workforce_management_web.post(
        'v1/schedule/types', json={'schedule': [3, 2]},
    )
    data = await res.json()
    assert data['schedule_types']


@pytest.mark.pgsql('workforce_management')
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        pytest.param({}, 400, id='empty params'),
        pytest.param(
            {
                'schedule_alias': '5x2/10:00-00:00',
                'schedule': [2, 3],
                'first_weekend': True,
                'start': '10:00:00',
                'duration_minutes': 60 * 7,
            },
            400,
            id='no rotation type',
        ),
        pytest.param(
            {
                'schedule_alias': '0',
                'schedule': [],
                'first_weekend': True,
                'start': '10:00:00',
                'duration_minutes': 60 * 7,
            },
            400,
            id='empty schedule',
        ),
        pytest.param(
            {
                'schedule_alias': '0',
                'schedule': [0],
                'first_weekend': True,
                'start': '10:00:00',
                'duration_minutes': 60 * 7,
            },
            400,
            id='zero schedule',
        ),
        pytest.param(
            {'schedule_alias': '0', 'schedule_by_minutes': []},
            400,
            id='empty schedule_by_minutes',
        ),
        pytest.param(
            {'schedule_alias': '0', 'schedule_by_minutes': [0]},
            400,
            id='zero schedule_by_minutes',
        ),
    ],
)
async def test_empty_schedules(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
