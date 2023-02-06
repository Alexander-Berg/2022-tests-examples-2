import copy

#  pylint:disable=C0302
import pytest

from workforce_management.common import constants
from . import util


URI = 'v1/operators/shift/create'
GET_URI = 'v2/shifts/values'
REVISION_ID = '2020-08-25T21:00:00.000000 +0000'
REVISION_ID_UID2 = '2020-08-26T22:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-06-25T21:00:00.000000 +0000'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


OPERATORS_LIST_CHANGES = [
    {
        'departments': ['1'],
        'employment_status': 'in_staff',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['nokia', 'nokia2'],
        'source': 'taxi',
        'yandex_uid': 'uid1',
        'employee_uid': '00000000-0000-0000-0000-000000000001',
        'login': 'abd-damir',
        'full_name': 'Abdullin Damir',
        'supervisor_login': 'aladin227',
        'mentor_login': 'supervisor@unit.test',
        'phone_pd_id': '111',
        'tags': ['naruto'],
    },
    {
        'departments': ['2'],
        'employment_status': 'in_staff',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['nokia'],
        'source': 'taxi',
        'yandex_uid': 'uid2',
        'employee_uid': '00000000-0000-0000-0000-000000000002',
        'login': 'chakchak',
        'full_name': 'Gilgenberg Valeria',
        'supervisor_login': 'abd-damir',
        'supervisor': {
            'full_name': 'Abdullin Damir',
            'login': 'abd-damir',
            'yandex_uid': 'uid1',
            'state': 'ready',
        },
        'mentor_login': 'mentor@unit.test',
        'telegram_login_pd_id': 'vasya_iz_derevni',
        'tags': ['naruto', 'driver'],
    },
    {
        'created_at': '2020-07-21 00:00:00Z',
        'updated_at': '2020-07-21 00:00:00Z',
        'departments': ['999'],
        'employment_status': 'in_staff',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['iphone', 'iphone2'],
        'source': 'taxi',
        'yandex_uid': 'uid3',
        'employee_uid': '00000000-0000-0000-0000-000000000003',
        'login': 'tatarstan',
        'full_name': 'Minihanov Minihanov',
        'supervisor_login': 'abd-damir',
        'mentor_login': 'supervisor@unit.test',
        'telegram_login_pd_id': 'morozhenka',
    },
]


@pytest.mark.now('2020-08-02T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql', 'allowed_periods.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res_len, expected_schedule_id',
    [
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-09-01 11:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
            },
            400,
            None,
            None,
            id='no_active_schedule',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
            },
            200,
            1,
            4,
            id='1',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2000-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
            },
            400,
            None,
            None,
            id='outside_editing_period',
        ),
        (
            {
                'shifts': [
                    {
                        'start': '2020-07-02 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
            },
            200,
            1,
            1,
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'hokage',
                        'operator': {
                            'yandex_uid': 'uid5',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
            },
            400,
            None,
            None,
            id='deleted_operator',
        ),
        (
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': WRONG_REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
            },
            409,
            None,
            None,
        ),
        (
            {
                'shifts': [
                    {
                        'start': '2020-07-26 13:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                    },
                ],
            },
            400,  # intersection
            None,
            1,
        ),
        (
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                    },
                    {
                        'start': '2020-09-01 01:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                    },
                ],
            },
            400,  # shift intersection
            None,
            None,
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res_len,
        expected_schedule_id,
        mock_effrat_employees,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False
    else:
        data = await res.json()
        assert len(data['new_shifts']) == expected_res_len
    await util.check_shifts(
        taxi_workforce_management_web=taxi_workforce_management_web,
        tst_request=tst_request,
        success=success,
        expected_schedule_id=expected_schedule_id,
    )


@pytest.mark.now('2020-08-02T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql', 'allowed_periods.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_segments_count',
    [
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 240,
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'segments': [
                            {
                                'skill': 'order',
                                'start': '2020-09-01 00:00:00.0 +0000',
                                'duration_minutes': 120,
                            },
                            {
                                'skill': 'pokemon',
                                'start': '2020-09-01 02:00:00.0 +0000',
                                'duration_minutes': 120,
                            },
                        ],
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
            },
            200,
            2,
            id='base_case',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 240,
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'segments': [
                            {
                                'skill': 'order',
                                'start': '2020-09-01 00:00:00.0 +0000',
                                'duration_minutes': 120,
                            },
                            {
                                'skill': 'pokemon',
                                'start': '2020-09-01 01:00:00.0 +0000',
                                'duration_minutes': 120,
                            },
                        ],
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
            },
            400,
            2,
            id='shift_segments_overlap',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 240,
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'segments': [
                            {
                                'skill': 'order',
                                'start': '2020-09-01 00:00:00.0 +0000',
                                'duration_minutes': 120,
                            },
                            {
                                'skill': 'pokemon',
                                'start': '2020-09-01 03:00:00.0 +0000',
                                'duration_minutes': 120,
                            },
                        ],
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
            },
            400,
            2,
            id='shift_segment_outside_shift_1',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 240,
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'segments': [
                            {
                                'skill': 'order',
                                'start': '2020-09-01 00:00:00.0 +0000',
                                'duration_minutes': 120,
                            },
                            {
                                'skill': 'pokemon',
                                'start': '2020-09-01 04:00:00.0 +0000',
                                'duration_minutes': 120,
                            },
                        ],
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
            },
            400,
            2,
            id='shift_segment_outside_shift_2',
        ),
    ],
)
async def test_segments(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_segments_count,
        mock_effrat_employees,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    if expected_status > 200:
        return
    res = await taxi_workforce_management_web.post(
        GET_URI,
        json={
            'skill': 'order',
            'datetime_from': '2000-01-01T00:00:00Z',
            'datetime_to': '2100-01-01T00:00:00Z',
            'limit': 10,
        },
        headers=HEADERS,
    )
    data = await res.json()
    segments = data['records'][0]['shift'].get('segments')
    if expected_segments_count:
        assert len(segments) == expected_segments_count


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts_with_breaks.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res_len, expected_schedule_id',
    [
        (
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                        'events': [
                            {
                                'event_id': 0,
                                'start': '2020-09-01 00:00:00.0 +0000',
                                'duration_minutes': 60,
                            },
                        ],
                    },
                ],
            },
            200,
            1,
            4,
        ),
        (
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'events': [
                            {
                                'event_id': 0,
                                'start': '2020-09-02 23:00:00.0 +0000',
                                'duration_minutes': 60,
                            },
                        ],
                    },
                ],
            },
            400,
            None,
            None,
        ),  # shift event outside shift
        (
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'events': [
                            {
                                'event_id': 0,
                                'start': '2020-09-01 00:00:00.0 +0000',
                                'duration_minutes': 30,
                            },
                            {
                                'event_id': 0,
                                'start': '2020-09-01 00:05:00.0 +0000',
                                'duration_minutes': 30,
                            },
                        ],
                    },
                ],
            },
            400,
            None,
            None,
        ),  # shift event intersects another one
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-10 00:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'droid',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                        'events': [
                            {
                                'event_id': 0,
                                'start': '2020-07-10 00:00:00.0 +0000',
                                'duration_minutes': 60,
                            },
                        ],
                    },
                ],
                'option': 'spread_new',
            },
            200,
            1,
            1,
            id='one_break_inside_small_shift',
        ),
    ],
)
async def test_events(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res_len,
        expected_schedule_id,
        mock_effrat_employees,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    await util.check_shifts(
        taxi_workforce_management_web=taxi_workforce_management_web,
        tst_request=tst_request,
        success=success,
        check_events_on_success=lambda actual_events: len(actual_events)
        == expected_res_len,
        expected_schedule_id=expected_schedule_id,
    )


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts_with_breaks.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_breaks_count',
    [
        (
            {
                'shifts': [
                    {
                        'start': '2023-08-01 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'droid',
                        'operator': {
                            'yandex_uid': 'uid3',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
                'option': 'spread_new',
            },
            200,
            3,
        ),
        (
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 30,
                        'skill': 'droid',
                        'operator': {
                            'yandex_uid': 'uid3',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
                'option': 'spread_new',
            },
            400,
            None,
        ),
        (
            {
                'shifts': [
                    {
                        'start': '2020-07-28 12:00:00.0 +0000',
                        'duration_minutes': 180,
                        'skill': 'droid',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                        'events': [
                            {
                                'event_id': 1,
                                'start': '2020-07-28 12:00:00.0 +0000',
                                'duration_minutes': 120,
                            },
                        ],
                    },
                ],
                'option': 'spread_new',
            },
            200,
            3,
        ),  # new shift + shift event with its own breaks
    ],
)
async def test_breaks_spreading(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_breaks_count,
        mock_effrat_employees,
        pgsql,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    data = await res.json()
    assert data

    if expected_status > 200:
        return

    res = await taxi_workforce_management_web.post(
        GET_URI,
        json={
            'skill': tst_request['shifts'][0]['skill'],
            'datetime_from': '2000-01-01T00:00:00Z',
            'datetime_to': '2100-01-01T00:00:00Z',
            'limit': 10,
        },
        headers=HEADERS,
    )
    data = await res.json()
    breaks = data['records'][0]['shift']['breaks']
    assert len(breaks) == expected_breaks_count


@pytest.mark.now('2020-07-02T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_notify',
    [
        (
            {
                'shifts': [
                    {
                        'start': '2020-07-02 05:25:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                    {
                        'start': '2020-07-02 11:25:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                    {
                        'start': '2020-08-03 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid2',
                            'revision_id': REVISION_ID_UID2,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
            },
            {'messages': {'uid1': [{'message_key': 'new_shifts'}]}},
        ),
    ],
)
async def test_trigger_telegram(
        taxi_workforce_management_web,
        web_context,
        mock_effrat_employees,
        stq,
        tst_request,
        expected_notify,
):
    mock_effrat_employees()
    await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert (
        stq.workforce_management_bot_sending.next_call()['kwargs']
        == expected_notify
    )

    assert stq.workforce_management_setup_jobs.next_call()


@pytest.mark.now('2020-07-02T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql'],
)
@pytest.mark.parametrize(
    'tst_request',
    [
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-02 05:25:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                    {
                        'start': '2020-07-02 11:25:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operator': {
                            'yandex_uid': 'uid1',
                            'revision_id': REVISION_ID,
                        },
                        'type': constants.ShiftTypes.common.value,
                    },
                ],
            },
        ),
    ],
)
async def test_domain_migrated_operator(
        taxi_workforce_management_web,
        web_context,
        mock_effrat_employees,
        tst_request,
):
    mock_effrat_employees(
        operators_list=[OPERATORS_LIST_CHANGES[0], OPERATORS_LIST_CHANGES[1]],
    )
    await taxi_workforce_management_web.invalidate_caches(clean_update=False)

    res = await taxi_workforce_management_web.post(
        URI,
        json=tst_request,
        headers={'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'},
    )
    assert res.status == 200

    mock_effrat_employees(
        operators_list=[
            {
                **OPERATORS_LIST_CHANGES[0],
                'employment_status': 'fired',
                'employee_uid': '00000000-0000-0000-0000-000000000001',
            },
            {
                **OPERATORS_LIST_CHANGES[0],
                'source': 'eats',
                'employee_uid': '00000000-0000-0000-0001-000000000001',
            },
        ],
    )
    await taxi_workforce_management_web.invalidate_caches(clean_update=False)

    async def get_operator(domain: str, expect_status: int):
        res = await taxi_workforce_management_web.get(
            '/v1/operator?yandex_uid=uid1',
            headers={'X-Yandex-UID': 'uid1', 'X-WFM-Domain': domain},
        )
        assert res.status == expect_status

        return await res.json()

    old_domain_operator = await get_operator(domain='taxi', expect_status=200)
    assert old_domain_operator['state'] == 'deleted'
    old_domain_operator.pop('state')

    new_domain_operator = await get_operator(domain='eats', expect_status=200)
    assert new_domain_operator['state'] == 'ready'
    new_domain_operator.pop('state')

    assert old_domain_operator == new_domain_operator

    migrated_request = copy.deepcopy(tst_request)
    for shift in migrated_request['shifts']:
        shift['operator']['revision_id'] = new_domain_operator['revision_id']
        # shift by a day
        shift['start'] = shift['start'].replace('-02 ', '-03 ')

    res = await taxi_workforce_management_web.post(
        URI,
        json=migrated_request,
        headers={'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'eats'},
    )
    assert res.status == 200

    res_old = await get_operator(domain='taxi', expect_status=200)
    res_new = await get_operator(domain='eats', expect_status=200)
    assert res_old['revision_id'] == res_new['revision_id']
