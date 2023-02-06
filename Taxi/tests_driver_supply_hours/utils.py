import json


def create_park_response(
        subintervals_duration, driver_subintervals, subintervals_count=None,
):
    if not subintervals_count:
        subintervals_count = len(driver_subintervals[0])
    return {
        'time_interval': {
            'start_at': 'start_at',
            'end_at': 'end_at',
            'subintervals_count': subintervals_count,
            'subintervals_duration': subintervals_duration,
        },
        'working_time': [
            {
                'park_id': 'xxx',
                'driver_profile_id': 'Ivanov',
                'subintervals_working_time': subintervals,
            }
            for subintervals in driver_subintervals
        ],
    }


def check_park_requests(
        handle, expectted_time_interval, driver_profile_id=None,
):
    request = json.loads(handle.next_call()['request'].get_data())
    expected_request = {
        'query': {
            'park': {'id': 'xxx'},
            'time_interval': expectted_time_interval,
        },
    }
    if driver_profile_id:
        expected_request['query']['park'][
            'driver_profile_id'
        ] = driver_profile_id
    assert (
        request == expected_request
    ), f'request: {request} != expected_request: {expected_request}'
