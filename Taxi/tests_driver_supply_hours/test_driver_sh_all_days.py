import pytest

from tests_driver_supply_hours import utils

DRIVER_SH_URL = '/v1/parks/drivers-profiles/supply/retrieve/all-days'


@pytest.fixture(name='fleet_parks_default', autouse=True)
def _mock_fleet_parks(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _sh_default(request):
        return {
            'parks': [
                {
                    'id': '775',
                    'login': 'some_login',
                    'name': 'top park',
                    'is_active': True,
                    'city_id': 'msk',
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'rus',
                    'provider_config': {'type': 'production', 'clid': '777'},
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }


@pytest.mark.now('2020-03-25T01:00:00+00:00')
async def test_sh_mongo(taxi_driver_supply_hours):
    response = await taxi_driver_supply_hours.post(
        DRIVER_SH_URL,
        json={
            'query': {
                'park': {'id': 'xxx', 'driver_profile_ids': ['Ivanov']},
                'supply': {
                    'period': {
                        'from': '2020-03-24T23:00:00Z',
                        'to': '2020-03-25T01:00:00Z',
                    },
                    'aggregate_by': 'hours',
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profiles': [
            {
                'driver_profile_id': 'Ivanov',
                'supply': [
                    {
                        'from': '2020-03-24T23:00:00+00:00',
                        'to': '2020-03-25T00:00:00+00:00',
                        'seconds': 3600,
                    },
                    {
                        'from': '2020-03-25T00:00:00+00:00',
                        'to': '2020-03-25T01:00:00+00:00',
                        'seconds': 3600,
                    },
                ],
            },
        ],
    }


PARKS_HOURS_RESPONSE_HOURS = {
    'time_interval': {
        'start_at': '2020-03-24T23:00:00+0000',
        'end_at': '2020-03-24T21:00:00+0000',
        'subintervals_count': 2,
        'subintervals_duration': 3600,
    },
    'working_time': [
        {
            'park_id': 'xxx',
            'driver_profile_id': 'Ivanov',
            'subintervals_working_time': [3600, 3600],
        },
    ],
}


@pytest.mark.now('2020-03-25T01:00:00+00:00')
async def test_sh_parks(taxi_driver_supply_hours, mockserver):
    @mockserver.json_handler('/parks/driver-profiles/statistics/working-time')
    def _sh_hours(request):
        return PARKS_HOURS_RESPONSE_HOURS

    response = await taxi_driver_supply_hours.post(
        DRIVER_SH_URL,
        json={
            'query': {
                'park': {'id': 'xxx', 'driver_profile_ids': ['Ivanov']},
                'supply': {
                    'period': {
                        'from': '2020-03-24T21:00:00Z',
                        'to': '2020-03-24T23:00:00Z',
                    },
                    'aggregate_by': 'hours',
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profiles': [
            {
                'driver_profile_id': 'Ivanov',
                'supply': [
                    {
                        'from': '2020-03-24T21:00:00+00:00',
                        'to': '2020-03-24T22:00:00+00:00',
                        'seconds': 3600,
                    },
                    {
                        'from': '2020-03-24T22:00:00+00:00',
                        'to': '2020-03-24T23:00:00+00:00',
                        'seconds': 3600,
                    },
                ],
            },
        ],
    }


PARKS_HOURS_RESPONSE_DAYS = {
    'time_interval': {
        'start_at': '2020-03-23T00:00:00+0000',
        'end_at': '2020-03-24T23:00:00+0000',
        'subintervals_count': 2,
        'subintervals_duration': 86400,
    },
    'working_time': [
        {
            'park_id': 'xxx',
            'driver_profile_id': 'Ivanov',
            'subintervals_working_time': [3600, 3600],
        },
    ],
}


PARKS_HOURS_RESPONSE_WEEK = {
    'time_interval': {
        'start_at': '2020-03-18T00:00:00+0000',
        'end_at': '2020-03-25T00:00:00+0000',
        'subintervals_count': 1,
        'subintervals_duration': 604800,
    },
    'working_time': [
        {
            'park_id': 'xxx',
            'driver_profile_id': 'Ivanov',
            'subintervals_working_time': [3600],
        },
    ],
}


@pytest.mark.now('2020-03-25T01:00:00+00:00')
@pytest.mark.parametrize(
    'parks_response, supply_request, expected_supply',
    [
        (
            PARKS_HOURS_RESPONSE_HOURS,
            {
                'period': {
                    'from': '2020-03-24T21:00:00Z',
                    'to': '2020-03-25T01:00:00Z',
                },
                'aggregate_by': 'hours',
            },
            'supply_hours.json',
        ),
        (
            PARKS_HOURS_RESPONSE_WEEK,
            {
                'period': {
                    'from': '2020-03-18T00:00:00Z',
                    'to': '2020-03-25T00:00:00Z',
                },
                'aggregate_by': 'period',
            },
            'supply_week.json',
        ),
    ],
)
async def test_sh_parks_and_mongo(
        parks_response,
        supply_request,
        expected_supply,
        taxi_driver_supply_hours,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/parks/driver-profiles/statistics/working-time')
    def _sh_hours(request):
        return parks_response

    response = await taxi_driver_supply_hours.post(
        DRIVER_SH_URL,
        json={
            'query': {
                'park': {'id': 'xxx', 'driver_profile_ids': ['Ivanov']},
                'supply': supply_request,
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profiles': [
            {
                'driver_profile_id': 'Ivanov',
                'supply': load_json(expected_supply),
            },
        ],
    }


@pytest.mark.now('2020-03-25T01:00:00+00:00')
async def test_sh_parks_and_mongo_days(
        taxi_driver_supply_hours, mockserver, load_json,
):
    def get_parks_responses():
        parks_responses = [
            {
                'time_interval': {
                    'start_at': '2020-03-23T00:00:00+0000',
                    'end_at': '2020-03-24T00:00:00+0000',
                    'subintervals_count': 1,
                    'subintervals_duration': 24 * 60 * 60,
                },
                'working_time': [
                    {
                        'park_id': 'xxx',
                        'driver_profile_id': 'Ivanov',
                        'subintervals_working_time': [3600],
                    },
                ],
            },
            {
                'time_interval': {
                    'start_at': '2020-03-24T00:00:00+0000',
                    'end_at': '2020-03-24T23:00:00+0000',
                    'subintervals_count': 23,
                    'subintervals_duration': 60 * 60,
                },
                'working_time': [
                    {
                        'park_id': 'xxx',
                        'driver_profile_id': 'Ivanov',
                        'subintervals_working_time': [10] * 23,
                    },
                ],
            },
        ]
        for response in parks_responses:
            yield response

    get_parks_responses_gen = get_parks_responses()

    @mockserver.json_handler('/parks/driver-profiles/statistics/working-time')
    def _sh_hours(request):
        return next(get_parks_responses_gen)

    response = await taxi_driver_supply_hours.post(
        DRIVER_SH_URL,
        json={
            'query': {
                'park': {'id': 'xxx', 'driver_profile_ids': ['Ivanov']},
                'supply': {
                    'period': {
                        'from': '2020-03-23T00:00:00Z',
                        'to': '2020-03-25T00:00:00Z',
                    },
                    'aggregate_by': 'days',
                },
            },
        },
    )

    assert _sh_hours.times_called == 2
    utils.check_park_requests(
        _sh_hours,
        {
            'start_at': '2020-03-23T00:00:00+0000',
            'end_at': '2020-03-24T00:00:00+0000',
            'subintervals_duration': 24 * 60 * 60,
        },
        ['Ivanov'],
    )
    utils.check_park_requests(
        _sh_hours,
        {
            'start_at': '2020-03-24T00:00:00+0000',
            'end_at': '2020-03-24T23:00:00+0000',
            'subintervals_duration': 60 * 60,
        },
        ['Ivanov'],
    )

    assert response.status_code == 200
    assert response.json() == {
        'driver_profiles': [
            {
                'driver_profile_id': 'Ivanov',
                'supply': [
                    {
                        'from': '2020-03-23T00:00:00+00:00',
                        'seconds': 3600,
                        'to': '2020-03-24T00:00:00+00:00',
                    },
                    {
                        'from': '2020-03-24T00:00:00+00:00',
                        'seconds': 3830,
                        'to': '2020-03-25T00:00:00+00:00',
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2020-03-25T00:59:59+01:00')
@pytest.mark.config(
    DRIVER_SUPPLY_HOURS_TIME_RESTRICTIONS={
        'hot_hours': 2,
        'max_depth_days': 30,
    },
)
@pytest.mark.parametrize(
    'supply_request, parks_request, parks_response, expected_supply',
    [
        pytest.param(
            {
                'period': {
                    'from': '2020-03-23T00:00:00+01',
                    'to': '2020-03-24T00:00:00+01',
                },
                'aggregate_by': 'days',
            },
            {
                'start_at': '2020-03-22T23:00:00+0000',
                'end_at': '2020-03-23T23:00:00+0000',
                'subintervals_duration': 24 * 60 * 60,
            },
            {
                'time_interval': {
                    'start_at': '2020-03-22T23:00:00+0000',
                    'end_at': '2020-03-23T23:00:00+0000',
                    'subintervals_duration': 24 * 60 * 60,
                    'subintervals_count': 1,
                },
                'working_time': [
                    {
                        'park_id': 'xxx',
                        'driver_profile_id': 'Ivanov',
                        'subintervals_working_time': [60 * 60],
                    },
                ],
            },
            {
                'driver_profiles': [
                    {
                        'driver_profile_id': 'Ivanov',
                        'supply': [
                            {
                                'from': '2020-03-22T23:00:00+00:00',
                                'to': '2020-03-23T23:00:00+00:00',
                                'seconds': 60 * 60,
                            },
                        ],
                    },
                ],
            },
            id='to_time < hot_time | days',
        ),
        pytest.param(
            {
                'period': {
                    'from': '2020-03-24T00:00:00+01',
                    'to': '2020-03-25T00:00:00+01',
                },
                'aggregate_by': 'days',
            },
            {
                'start_at': '2020-03-23T23:00:00+0000',
                'end_at': '2020-03-24T21:00:00+0000',
                'subintervals_duration': 60 * 60,
            },
            {
                'time_interval': {
                    'start_at': '2020-03-23T23:00:00+0000',
                    'end_at': '2020-03-24T21:00:00+0000',
                    'subintervals_duration': 60 * 60,
                    'subintervals_count': 22,
                },
                'working_time': [
                    {
                        'park_id': 'xxx',
                        'driver_profile_id': 'Ivanov',
                        'subintervals_working_time': [100] * 22,
                    },
                ],
            },
            {
                'driver_profiles': [
                    {
                        'driver_profile_id': 'Ivanov',
                        'supply': [
                            {
                                'from': '2020-03-23T23:00:00+00:00',
                                'to': '2020-03-24T23:00:00+00:00',
                                'seconds': 100 * 22 + 1800,
                            },
                        ],
                    },
                ],
            },
            id='from_time < hot_time, to_time > hot_time | days',
        ),
        pytest.param(
            {
                'period': {
                    'from': '2020-03-24T21:00:00+01',
                    'to': '2020-03-25T00:00:00+01',
                },
                'aggregate_by': 'hours',
            },
            {
                'start_at': '2020-03-24T20:00:00+0000',
                'end_at': '2020-03-24T21:00:00+0000',
                'subintervals_duration': 60 * 60,
            },
            {
                'time_interval': {
                    'start_at': '2020-03-24T20:00:00+0000',
                    'end_at': '2020-03-24T21:00:00+0000',
                    'subintervals_duration': 60 * 60,
                    'subintervals_count': 1,
                },
                'working_time': [
                    {
                        'park_id': 'xxx',
                        'driver_profile_id': 'Ivanov',
                        'subintervals_working_time': [100],
                    },
                ],
            },
            {
                'driver_profiles': [
                    {
                        'driver_profile_id': 'Ivanov',
                        'supply': [
                            {
                                'from': '2020-03-24T20:00:00+00:00',
                                'to': '2020-03-24T21:00:00+00:00',
                                'seconds': 100,
                            },
                            {
                                'from': '2020-03-24T22:00:00+00:00',
                                'to': '2020-03-24T23:00:00+00:00',
                                'seconds': 1800,
                            },
                        ],
                    },
                ],
            },
            id='from_time < hot_time, to_time > hot_time | hours',
        ),
        pytest.param(
            {
                'period': {
                    'from': '2020-03-22T22:00:00+01',
                    'to': '2020-03-25T22:00:00+01',
                },
                'aggregate_by': 'days',
            },
            {
                'start_at': '2020-03-22T21:00:00+0000',
                'end_at': '2020-03-24T21:00:00+0000',
                'subintervals_duration': 86400,
            },
            {
                'time_interval': {
                    'start_at': '2020-03-22T21:00:00+0000',
                    'end_at': '2020-03-24T21:00:00+0000',
                    'subintervals_count': 2,
                    'subintervals_duration': 86400,
                },
                'working_time': [
                    {
                        'park_id': 'xxx',
                        'driver_profile_id': 'Ivanov',
                        'subintervals_working_time': [86400, 86400],
                    },
                ],
            },
            {
                'driver_profiles': [
                    {
                        'driver_profile_id': 'Ivanov',
                        'supply': [
                            {
                                'from': '2020-03-22T21:00:00+00:00',
                                'to': '2020-03-23T21:00:00+00:00',
                                'seconds': 86400,
                            },
                            {
                                'from': '2020-03-23T21:00:00+00:00',
                                'to': '2020-03-24T21:00:00+00:00',
                                'seconds': 86400,
                            },
                            {
                                'from': '2020-03-24T21:00:00+00:00',
                                'to': '2020-03-25T02:00:00+00:00',
                                'seconds': 9300,
                            },
                        ],
                    },
                ],
            },
            id="""from_time < hot_time, to_time > hot_time,
            last_day_begin = hot_time | days""",
        ),
        pytest.param(
            {
                'period': {
                    'from': '2020-03-24T22:00:00+01',
                    'to': '2020-03-25T22:00:00+01',
                },
                'aggregate_by': 'days',
            },
            None,
            None,
            {
                'driver_profiles': [
                    {
                        'driver_profile_id': 'Ivanov',
                        'supply': [
                            {
                                'from': '2020-03-24T21:00:00+00:00',
                                'to': '2020-03-25T02:00:00+00:00',
                                'seconds': 9300,
                            },
                        ],
                    },
                ],
            },
            id='from_time = hot_time | days',
        ),
        pytest.param(
            {
                'period': {
                    'from': '2020-03-25T00:00:00+01',
                    'to': '2020-03-26T00:00:00+01',
                },
                'aggregate_by': 'days',
            },
            None,
            None,
            {
                'driver_profiles': [
                    {
                        'driver_profile_id': 'Ivanov',
                        'supply': [
                            {
                                'from': '2020-03-24T23:00:00+00:00',
                                'to': '2020-03-25T02:00:00+00:00',
                                'seconds': 7500,
                            },
                        ],
                    },
                ],
            },
            id='from_time > hot_time | days',
        ),
        pytest.param(
            {
                'period': {
                    'from': '2020-03-25T00:00:00+01',
                    'to': '2020-03-26T00:00:00+01',
                },
                'aggregate_by': 'days',
            },
            None,
            None,
            {
                'driver_profiles': [
                    {
                        'driver_profile_id': 'Ivanov',
                        'supply': [
                            {
                                'from': '2020-03-24T23:00:00+00:00',
                                'to': '2020-03-25T02:00:00+00:00',
                                'seconds': 7500,
                            },
                        ],
                    },
                ],
            },
            id='from_time > hot_time | hours',
        ),
        pytest.param(
            {
                'period': {
                    'from': '2020-03-27T22:00:00+01',
                    'to': '2020-03-28T22:00:00+01',
                },
                'aggregate_by': 'days',
            },
            None,
            None,
            {'driver_profiles': []},
            id='from_time > now | days',
        ),
        pytest.param(
            {
                'period': {
                    'from': '2020-03-27T22:00:00+01',
                    'to': '2020-03-28T22:00:00+01',
                },
                'aggregate_by': 'hours',
            },
            None,
            None,
            {'driver_profiles': []},
            id='from_time > now | hours',
        ),
    ],
)
async def test_sh_single_parks_query(
        taxi_driver_supply_hours,
        mockserver,
        supply_request,
        parks_request,
        parks_response,
        expected_supply,
):
    @mockserver.json_handler('/parks/driver-profiles/statistics/working-time')
    def _sh_hours(request):
        return parks_response

    response = await taxi_driver_supply_hours.post(
        DRIVER_SH_URL,
        json={
            'query': {
                'park': {'id': 'xxx', 'driver_profile_ids': ['Ivanov']},
                'supply': supply_request,
            },
        },
    )

    if parks_request is None:
        assert _sh_hours.times_called == 0
    else:
        assert _sh_hours.times_called == 1
        utils.check_park_requests(_sh_hours, parks_request, ['Ivanov'])

    assert response.status_code == 200
    assert response.json() == expected_supply


@pytest.mark.now('2020-03-31T10:30:04+00:00')
@pytest.mark.parametrize(
    'parks_response, supply_request, expected_supply',
    [
        pytest.param(
            utils.create_park_response(60 * 60, [[]]),
            {
                'period': {
                    'from': '2020-02-28T07:00:00Z',
                    'to': '2020-02-28T13:00:00Z',
                },
                'aggregate_by': 'hours',
            },
            [
                {
                    'from': '2020-02-28T07:00:00+00:00',
                    'to': '2020-02-28T08:00:00+00:00',
                },
                {
                    'from': '2020-02-28T08:00:00+00:00',
                    'to': '2020-02-28T09:00:00+00:00',
                },
                {
                    'from': '2020-02-28T09:00:00+00:00',
                    'to': '2020-02-28T10:00:00+00:00',
                },
                {
                    'from': '2020-02-28T10:00:00+00:00',
                    'to': '2020-02-28T11:00:00+00:00',
                },
                {
                    'from': '2020-02-28T11:00:00+00:00',
                    'seconds': 0,
                    'to': '2020-02-28T12:00:00+00:00',
                },
                {
                    'from': '2020-02-28T12:00:00+00:00',
                    'seconds': 0,
                    'to': '2020-02-28T13:00:00+00:00',
                },
            ],
            id='hours',
        ),
        pytest.param(
            utils.create_park_response(24 * 60 * 60, [[]]),
            {
                'period': {
                    'from': '2020-02-27T13:00:00Z',
                    'to': '2020-03-02T13:00:00Z',
                },
                'aggregate_by': 'days',
            },
            [
                {
                    'from': '2020-02-27T13:00:00+00:00',
                    'to': '2020-02-28T13:00:00+00:00',
                },
                {
                    'from': '2020-02-28T13:00:00+00:00',
                    'seconds': 0,
                    'to': '2020-02-29T13:00:00+00:00',
                },
                {
                    'from': '2020-02-29T13:00:00+00:00',
                    'seconds': 0,
                    'to': '2020-03-01T13:00:00+00:00',
                },
                {
                    'from': '2020-03-01T13:00:00+00:00',
                    'seconds': 0,
                    'to': '2020-03-02T13:00:00+00:00',
                },
            ],
            id='days',
        ),
        pytest.param(
            utils.create_park_response(363600, [[]]),
            {
                'period': {
                    'from': '2020-02-27T10:00:00Z',
                    'to': '2020-03-02T15:00:00Z',
                },
                'aggregate_by': 'period',
            },
            [
                {
                    'from': '2020-02-27T10:00:00+00:00',
                    'to': '2020-03-02T15:00:00+00:00',
                    'seconds': 0,
                },
            ],
            id='period',
        ),
    ],
)
async def test_old_parks_response(
        parks_response,
        supply_request,
        expected_supply,
        taxi_driver_supply_hours,
        mockserver,
):
    @mockserver.json_handler('/parks/driver-profiles/statistics/working-time')
    def _sh_hours(request):
        return {
            'time_interval': {
                'start_at': 'start_at',
                'end_at': 'end_at',
                'subintervals_count': 0,
                'subintervals_duration': 0,
            },
            'working_time': [
                {
                    'park_id': 'xxx',
                    'driver_profile_id': 'Ivanov',
                    'subintervals_working_time': [],
                },
            ],
        }

    response = await taxi_driver_supply_hours.post(
        DRIVER_SH_URL,
        json={
            'query': {
                'park': {'id': 'xxx', 'driver_profile_ids': ['Ivanov']},
                'supply': supply_request,
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profiles': [
            {'driver_profile_id': 'Ivanov', 'supply': expected_supply},
        ],
    }


@pytest.mark.now('2020-03-31T10:30:04+00:00')
@pytest.mark.parametrize(
    'parks_response, supply_request, expected_supply',
    [
        pytest.param(
            utils.create_park_response(60 * 60, [[]]),
            {
                'period': {
                    'from': '2020-03-31T09:00:00Z',
                    'to': '2020-03-31T14:00:00Z',
                },
                'aggregate_by': 'hours',
            },
            [
                {
                    'from': '2020-03-31T09:00:00+00:00',
                    'to': '2020-03-31T10:00:00+00:00',
                    'seconds': 0,
                },
                {
                    'from': '2020-03-31T10:00:00+00:00',
                    'to': '2020-03-31T11:00:00+00:00',
                    'seconds': 0,
                },
                {
                    'from': '2020-03-31T11:00:00+00:00',
                    'to': '2020-03-31T12:00:00+00:00',
                },
                {
                    'from': '2020-03-31T12:00:00+00:00',
                    'to': '2020-03-31T13:00:00+00:00',
                },
                {
                    'from': '2020-03-31T13:00:00+00:00',
                    'to': '2020-03-31T14:00:00+00:00',
                },
            ],
            id='hours',
        ),
        pytest.param(
            utils.create_park_response(24 * 60 * 60, [[]]),
            {
                'period': {
                    'from': '2020-03-31T09:00:00Z',
                    'to': '2020-04-02T09:00:00Z',
                },
                'aggregate_by': 'days',
            },
            [
                {
                    'from': '2020-03-31T09:00:00+00:00',
                    'seconds': 0,
                    'to': '2020-04-01T09:00:00+00:00',
                },
                {
                    'from': '2020-04-01T09:00:00+00:00',
                    'to': '2020-04-02T09:00:00+00:00',
                },
            ],
            id='days',
        ),
        pytest.param(
            utils.create_park_response(568800, [[]]),
            {
                'period': {
                    'from': '2020-03-30T01:00:00Z',
                    'to': '2020-04-04T15:00:00Z',
                },
                'aggregate_by': 'period',
            },
            [
                {
                    'from': '2020-03-30T01:00:00+00:00',
                    'to': '2020-04-04T15:00:00+00:00',
                    'seconds': 0,
                },
            ],
            id='period',
        ),
    ],
)
async def test_to_greater_now(
        parks_response,
        supply_request,
        expected_supply,
        taxi_driver_supply_hours,
        mockserver,
):
    @mockserver.json_handler('/parks/driver-profiles/statistics/working-time')
    def _sh_hours(request):
        return {
            'time_interval': {
                'start_at': 'start_at',
                'end_at': 'end_at',
                'subintervals_count': 0,
                'subintervals_duration': 0,
            },
            'working_time': [
                {
                    'park_id': 'xxx',
                    'driver_profile_id': 'Ivanov',
                    'subintervals_working_time': [],
                },
            ],
        }

    response = await taxi_driver_supply_hours.post(
        DRIVER_SH_URL,
        json={
            'query': {
                'park': {'id': 'xxx', 'driver_profile_ids': ['Ivanov']},
                'supply': supply_request,
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'driver_profiles': [
            {'driver_profile_id': 'Ivanov', 'supply': expected_supply},
        ],
    }
