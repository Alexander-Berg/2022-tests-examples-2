import copy
import datetime
import typing as tp

from taxi.util import dates

GET_SHIFTS_URI = 'v2/shifts/values'


def exclude_revision(data):
    return [
        {key: value for key, value in row.items() if key != 'revision_id'}
        for row in data
    ]


def parse_and_make_step(provided_datetime: str, hours: int = 0, days: int = 0):
    return dates.localize(
        dates.parse_timestring(provided_datetime, 'UTC')
        + datetime.timedelta(hours=hours, days=days),
    )


def remove_deprecated_fields(container: tp.Dict, *key_list):
    ccopy = copy.deepcopy(container)
    for key in key_list:
        ccopy.pop(key, None)
    return ccopy


async def check_shifts(
        taxi_workforce_management_web,
        tst_request: tp.Dict,
        success: bool,
        fetch_properties: tp.Optional[tp.Dict] = None,
        expected_schedule_id: tp.Optional[int] = None,
        check_schedule_type_id: bool = True,
        **kwargs,
):
    res = await taxi_workforce_management_web.post(
        GET_SHIFTS_URI,
        json=fetch_properties
        or {
            'yandex_uids': ['uid1', 'uid2'],
            'datetime_from': '2000-01-01T00:00:00Z',
            'datetime_to': '2100-01-01T00:00:00Z',
            'limit': 100,
        },
        headers={'X-WFM-Domain': 'taxi'},
    )
    data = await res.json()
    assert data
    for shift in tst_request['shifts']:
        found = False
        for actual_shift in data['records']:
            if dates.parse_timestring(
                    actual_shift['shift']['start'],
            ) == dates.parse_timestring(shift['start']):
                #  if shift_id provided - shift already exists
                found = 'shift_id' not in shift
                assert (
                    actual_shift['shift'].get('operators_schedule_types_id')
                    == expected_schedule_id
                ) or not check_schedule_type_id
                for object_name in ('breaks', 'events', 'segments'):
                    checker = kwargs.get(f'check_{object_name}_on_success')
                    if not checker:
                        continue
                    assert not success or checker(
                        actual_shift['shift'].get(object_name, []),
                    ), actual_shift['shift'].get(object_name, [])
                break
        assert found or not success
