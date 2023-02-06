import pytest

from tests_driver_supply_hours import utils

DRIVER_SH_URL = '/v1/parks/supply/retrieve/all-days'


@pytest.mark.now('2020-03-31T10:30:04+00:00')
@pytest.mark.parametrize(
    'parks_response, from_time, to_time, parks_request, expected_supply',
    [
        pytest.param(
            # parks_response
            utils.create_park_response(60 * 60, [[1800, 900, 1000, 500, 700]]),
            '2020-03-23T21:00:00Z',  # from_time
            '2020-03-24T02:00:00Z',  # to_time
            {
                'start_at': '2020-03-23T21:00:00+0000',
                'end_at': '2020-03-24T02:00:00+0000',
                'subintervals_duration': 60 * 60,
            },
            # expected_supply
            [
                {
                    'from': '2020-03-23T21:00:00+00:00',
                    'to': '2020-03-23T22:00:00+00:00',
                    'seconds': 1800,
                },
                {
                    'from': '2020-03-23T22:00:00+00:00',
                    'to': '2020-03-23T23:00:00+00:00',
                    'seconds': 900,
                },
                {
                    'from': '2020-03-23T23:00:00+00:00',
                    'to': '2020-03-24T00:00:00+00:00',
                    'seconds': 1000,
                },
                {
                    'from': '2020-03-24T00:00:00+00:00',
                    'to': '2020-03-24T01:00:00+00:00',
                    'seconds': 500,
                },
                {
                    'from': '2020-03-24T01:00:00+00:00',
                    'to': '2020-03-24T02:00:00+00:00',
                    'seconds': 700,
                },
            ],
            id='Different days',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(
                60 * 60, [[1800, 900, 1000], [500, 700, 0]],
            ),
            '2020-03-23T21:00:00Z',  # from_time
            '2020-03-24T02:00:00Z',  # to_time
            {
                'start_at': '2020-03-23T21:00:00+0000',
                'end_at': '2020-03-24T02:00:00+0000',
                'subintervals_duration': 3600,
            },
            # expected_supply
            [
                {
                    'from': '2020-03-23T21:00:00+00:00',
                    'to': '2020-03-23T22:00:00+00:00',
                    'seconds': 2300,
                },
                {
                    'from': '2020-03-23T22:00:00+00:00',
                    'to': '2020-03-23T23:00:00+00:00',
                    'seconds': 1600,
                },
                {
                    'from': '2020-03-23T23:00:00+00:00',
                    'to': '2020-03-24T00:00:00+00:00',
                    'seconds': 1000,
                },
            ],
            id='Many drivers',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(
                60 * 60, [[], []], subintervals_count=3,
            ),
            '2020-03-23T23:00:00Z',  # from_time
            '2020-03-24T02:00:00Z',  # to_time
            {
                'start_at': '2020-03-23T23:00:00+0000',
                'end_at': '2020-03-24T02:00:00+0000',
                'subintervals_duration': 60 * 60,
            },
            # expected_supply
            [
                {
                    'from': '2020-03-23T23:00:00+00:00',
                    'to': '2020-03-24T00:00:00+00:00',
                    'seconds': 0,
                },
                {
                    'from': '2020-03-24T00:00:00+00:00',
                    'to': '2020-03-24T01:00:00+00:00',
                    'seconds': 0,
                },
                {
                    'from': '2020-03-24T01:00:00+00:00',
                    'to': '2020-03-24T02:00:00+00:00',
                    'seconds': 0,
                },
            ],
            id='Empty parks response',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(
                60 * 60, [[], []], subintervals_count=3,
            ),
            '2020-02-27T23:00:00Z',  # from_time
            '2020-03-28T14:00:00Z',  # to_time
            {
                'start_at': '2020-02-28T11:00:00+0000',
                'end_at': '2020-03-28T14:00:00+0000',
                'subintervals_duration': 60 * 60,
            },
            # expected_supply
            [
                {
                    'from': '2020-02-27T23:00:00+00:00',
                    'to': '2020-02-28T00:00:00+00:00',
                },
                {
                    'from': '2020-02-28T00:00:00+00:00',
                    'to': '2020-02-28T01:00:00+00:00',
                },
                {
                    'from': '2020-02-28T01:00:00+00:00',
                    'to': '2020-02-28T02:00:00+00:00',
                },
                {
                    'from': '2020-02-28T02:00:00+00:00',
                    'to': '2020-02-28T03:00:00+00:00',
                },
                {
                    'from': '2020-02-28T03:00:00+00:00',
                    'to': '2020-02-28T04:00:00+00:00',
                },
                {
                    'from': '2020-02-28T04:00:00+00:00',
                    'to': '2020-02-28T05:00:00+00:00',
                },
                {
                    'from': '2020-02-28T05:00:00+00:00',
                    'to': '2020-02-28T06:00:00+00:00',
                },
                {
                    'from': '2020-02-28T06:00:00+00:00',
                    'to': '2020-02-28T07:00:00+00:00',
                },
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
                {
                    'from': '2020-02-28T13:00:00+00:00',
                    'seconds': 0,
                    'to': '2020-02-28T14:00:00+00:00',
                },
            ],
            id='Old period',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(
                60 * 60, [[], []], subintervals_count=2,
            ),
            '2020-03-31T09:00:00Z',  # from_time
            '2020-04-01T01:00:00Z',  # to_time
            {
                'start_at': '2020-03-31T09:00:00+0000',
                'end_at': '2020-03-31T11:00:00+0000',
                'subintervals_duration': 60 * 60,
            },
            # expected_supply
            [
                {
                    'from': '2020-03-31T09:00:00+00:00',
                    'seconds': 0,
                    'to': '2020-03-31T10:00:00+00:00',
                },
                {
                    'from': '2020-03-31T10:00:00+00:00',
                    'seconds': 0,
                    'to': '2020-03-31T11:00:00+00:00',
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
                {
                    'from': '2020-03-31T14:00:00+00:00',
                    'to': '2020-03-31T15:00:00+00:00',
                },
                {
                    'from': '2020-03-31T15:00:00+00:00',
                    'to': '2020-03-31T16:00:00+00:00',
                },
                {
                    'from': '2020-03-31T16:00:00+00:00',
                    'to': '2020-03-31T17:00:00+00:00',
                },
                {
                    'from': '2020-03-31T17:00:00+00:00',
                    'to': '2020-03-31T18:00:00+00:00',
                },
                {
                    'from': '2020-03-31T18:00:00+00:00',
                    'to': '2020-03-31T19:00:00+00:00',
                },
                {
                    'from': '2020-03-31T19:00:00+00:00',
                    'to': '2020-03-31T20:00:00+00:00',
                },
                {
                    'from': '2020-03-31T20:00:00+00:00',
                    'to': '2020-03-31T21:00:00+00:00',
                },
                {
                    'from': '2020-03-31T21:00:00+00:00',
                    'to': '2020-03-31T22:00:00+00:00',
                },
                {
                    'from': '2020-03-31T22:00:00+00:00',
                    'to': '2020-03-31T23:00:00+00:00',
                },
                {
                    'from': '2020-03-31T23:00:00+00:00',
                    'to': '2020-04-01T00:00:00+00:00',
                },
                {
                    'from': '2020-04-01T00:00:00+00:00',
                    'to': '2020-04-01T01:00:00+00:00',
                },
            ],
            id='To > now',
        ),
    ],
)
async def test_ok_hours(
        mockserver,
        taxi_driver_supply_hours,
        _parks_mock,
        parks_response,
        from_time,
        to_time,
        parks_request,
        expected_supply,
):
    _parks_mock.set_parks_response(parks_response)
    response = await taxi_driver_supply_hours.post(
        DRIVER_SH_URL,
        json={
            'query': {
                'park': {'id': 'xxx'},
                'supply': {
                    'period': {'from': from_time, 'to': to_time},
                    'aggregate_by': 'hours',
                },
            },
        },
    )

    assert _parks_mock.statistics_working_time.times_called == 1
    utils.check_park_requests(
        _parks_mock.statistics_working_time, parks_request,
    )

    assert response.status_code == 200
    assert response.json() == {'supply': expected_supply}


@pytest.mark.now('2020-03-31T10:30:04+00:00')
@pytest.mark.parametrize(
    'parks_response, from_time, to_time, parks_request, expected_supply',
    [
        pytest.param(
            # parks_response
            utils.create_park_response(24 * 60 * 60, [[3600, 1800, 900]]),
            '2020-03-21T02:00:00Z',  # from_time
            '2020-03-24T02:00:00Z',  # to_time
            {
                'start_at': '2020-03-21T02:00:00+0000',
                'end_at': '2020-03-24T02:00:00+0000',
                'subintervals_duration': 24 * 60 * 60,
            },
            # expected_supply
            [
                {
                    'from': '2020-03-21T02:00:00+00:00',
                    'to': '2020-03-22T02:00:00+00:00',
                    'seconds': 3600,
                },
                {
                    'from': '2020-03-22T02:00:00+00:00',
                    'to': '2020-03-23T02:00:00+00:00',
                    'seconds': 1800,
                },
                {
                    'from': '2020-03-23T02:00:00+00:00',
                    'to': '2020-03-24T02:00:00+00:00',
                    'seconds': 900,
                },
            ],
            id='One driver',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(
                24 * 60 * 60, [[3600, 1800, 900], [3, 2, 1]],
            ),
            '2020-03-21T02:00:00Z',  # from_time
            '2020-03-24T02:00:00Z',  # to_time
            {
                'start_at': '2020-03-21T02:00:00+0000',
                'end_at': '2020-03-24T02:00:00+0000',
                'subintervals_duration': 24 * 60 * 60,
            },
            # expected_supply
            [
                {
                    'from': '2020-03-21T02:00:00+00:00',
                    'to': '2020-03-22T02:00:00+00:00',
                    'seconds': 3603,
                },
                {
                    'from': '2020-03-22T02:00:00+00:00',
                    'to': '2020-03-23T02:00:00+00:00',
                    'seconds': 1802,
                },
                {
                    'from': '2020-03-23T02:00:00+00:00',
                    'to': '2020-03-24T02:00:00+00:00',
                    'seconds': 901,
                },
            ],
            id='Many drivers',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(
                24 * 60 * 60, [[], []], subintervals_count=3,
            ),
            '2020-03-21T02:00:00Z',  # from_time
            '2020-03-24T02:00:00Z',  # to_time
            {
                'start_at': '2020-03-21T02:00:00+0000',
                'end_at': '2020-03-24T02:00:00+0000',
                'subintervals_duration': 24 * 60 * 60,
            },
            # expected_supply
            [
                {
                    'from': '2020-03-21T02:00:00+00:00',
                    'to': '2020-03-22T02:00:00+00:00',
                    'seconds': 0,
                },
                {
                    'from': '2020-03-22T02:00:00+00:00',
                    'to': '2020-03-23T02:00:00+00:00',
                    'seconds': 0,
                },
                {
                    'from': '2020-03-23T02:00:00+00:00',
                    'to': '2020-03-24T02:00:00+00:00',
                    'seconds': 0,
                },
            ],
            id='Empty parks response',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(
                24 * 60 * 60, [[], []], subintervals_count=1,
            ),
            '2020-02-26T02:00:00Z',  # from_time
            '2020-02-29T02:00:00Z',  # to_time
            {
                'start_at': '2020-02-28T02:00:00+0000',
                'end_at': '2020-02-29T02:00:00+0000',
                'subintervals_duration': 24 * 60 * 60,
            },
            # expected_supply
            [
                {
                    'from': '2020-02-26T02:00:00+00:00',
                    'to': '2020-02-27T02:00:00+00:00',
                },
                {
                    'from': '2020-02-27T02:00:00+00:00',
                    'to': '2020-02-28T02:00:00+00:00',
                },
                {
                    'from': '2020-02-28T02:00:00+00:00',
                    'seconds': 0,
                    'to': '2020-02-29T02:00:00+00:00',
                },
            ],
            id='Old period',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(
                24 * 60 * 60, [[], []], subintervals_count=1,
            ),
            '2020-03-31T09:00:00Z',  # from_time
            '2020-04-03T09:00:00Z',  # to_time
            {
                'start_at': '2020-03-31T09:00:00+0000',
                'end_at': '2020-04-01T09:00:00+0000',
                'subintervals_duration': 24 * 60 * 60,
            },
            # expected_supply
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
                {
                    'from': '2020-04-02T09:00:00+00:00',
                    'to': '2020-04-03T09:00:00+00:00',
                },
            ],
            id='To > now',
        ),
    ],
)
async def test_ok_days(
        mockserver,
        taxi_driver_supply_hours,
        _parks_mock,
        parks_response,
        from_time,
        to_time,
        parks_request,
        expected_supply,
):
    _parks_mock.set_parks_response(parks_response)

    response = await taxi_driver_supply_hours.post(
        DRIVER_SH_URL,
        json={
            'query': {
                'park': {'id': 'xxx'},
                'supply': {
                    'period': {'from': from_time, 'to': to_time},
                    'aggregate_by': 'days',
                },
            },
        },
    )
    assert _parks_mock.statistics_working_time.times_called == 1
    utils.check_park_requests(
        _parks_mock.statistics_working_time, parks_request,
    )

    assert response.status_code == 200
    assert response.json() == {'supply': expected_supply}


@pytest.mark.now('2020-03-31T10:30:04+00:00')
@pytest.mark.parametrize(
    'parks_response, from_time, to_time, parks_request, expected_supply',
    [
        pytest.param(
            # parks_response
            utils.create_park_response(5 * 60 * 60, [[1800]]),
            '2020-03-23T21:00:00Z',  # from_time
            '2020-03-24T02:00:00Z',  # to_time
            {
                'start_at': '2020-03-23T21:00:00+0000',
                'end_at': '2020-03-24T02:00:00+0000',
                'subintervals_duration': 5 * 60 * 60,
            },
            # expected_supply
            [
                {
                    'from': '2020-03-23T21:00:00+00:00',
                    'to': '2020-03-24T02:00:00+00:00',
                    'seconds': 1800,
                },
            ],
            id='Basic',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(60 * 60, [[1800, 700, 500]]),
            '2020-03-01T21:00:00Z',  # from_time
            '2020-03-24T02:00:00Z',  # to_time
            {
                'start_at': '2020-03-01T21:00:00+0000',
                'end_at': '2020-03-24T02:00:00+0000',
                'subintervals_duration': 60 * 60,
            },
            # expected_supply
            [
                {
                    'from': '2020-03-01T21:00:00+00:00',
                    'to': '2020-03-24T02:00:00+00:00',
                    'seconds': 3000,
                },
            ],
            id='Big interval',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(
                60 * 60, [[1800, 201], [1001, 103], [12000, 1]],
            ),
            '2020-03-01T21:00:00Z',  # from_time
            '2020-03-24T02:00:00Z',  # to_time
            {
                'start_at': '2020-03-01T21:00:00+0000',
                'end_at': '2020-03-24T02:00:00+0000',
                'subintervals_duration': 60 * 60,
            },
            # expected_supply
            [
                {
                    'from': '2020-03-01T21:00:00+00:00',
                    'to': '2020-03-24T02:00:00+00:00',
                    'seconds': 15106,
                },
            ],
            id='Many drivers',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(
                60 * 60, [[], []], subintervals_count=1,
            ),
            '2020-03-10T21:00:00Z',  # from_time
            '2020-03-24T02:00:00Z',  # to_time
            {
                'start_at': '2020-03-10T21:00:00+0000',
                'end_at': '2020-03-24T02:00:00+0000',
                'subintervals_duration': 3600,
            },
            # expected_supply
            [
                {
                    'from': '2020-03-10T21:00:00+00:00',
                    'to': '2020-03-24T02:00:00+00:00',
                    'seconds': 0,
                },
            ],
            id='Empty parks response',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(82800, [[], []], subintervals_count=1),
            '2020-02-26T02:00:00Z',  # from_time
            '2020-02-29T10:00:00Z',  # to_time
            {
                'start_at': '2020-02-28T11:00:00+0000',
                'end_at': '2020-02-29T10:00:00+0000',
                'subintervals_duration': 82800,
            },
            # expected_supply
            [
                {
                    'from': '2020-02-26T02:00:00+00:00',
                    'seconds': 0,
                    'to': '2020-02-29T10:00:00+00:00',
                },
            ],
            id='Old period',
        ),
        pytest.param(
            # parks_response
            utils.create_park_response(122400, [[], []], subintervals_count=1),
            '2020-03-30T01:00:00Z',  # from_time
            '2020-04-04T15:00:00Z',  # to_time
            {
                'start_at': '2020-03-30T01:00:00+0000',
                'end_at': '2020-03-31T11:00:00+0000',
                'subintervals_duration': 122400,
            },
            # expected_supply
            [
                {
                    'from': '2020-03-30T01:00:00+00:00',
                    'to': '2020-04-04T15:00:00+00:00',
                    'seconds': 0,
                },
            ],
            id='To > now',
        ),
    ],
)
async def test_ok_period(
        mockserver,
        taxi_driver_supply_hours,
        _parks_mock,
        parks_response,
        from_time,
        to_time,
        parks_request,
        expected_supply,
):
    _parks_mock.set_parks_response(parks_response)
    response = await taxi_driver_supply_hours.post(
        DRIVER_SH_URL,
        json={
            'query': {
                'park': {'id': 'xxx'},
                'supply': {
                    'period': {'from': from_time, 'to': to_time},
                    'aggregate_by': 'period',
                },
            },
        },
    )

    assert _parks_mock.statistics_working_time.times_called == 1
    utils.check_park_requests(
        _parks_mock.statistics_working_time, parks_request,
    )

    assert response.status_code == 200
    assert response.json() == {'supply': expected_supply}


@pytest.mark.now('2020-03-31T00:00:00+00:00')
@pytest.mark.parametrize(
    'from_time, to_time, aggregate_by, code, expected_response',
    [
        pytest.param(
            '2020-03-24T00:00:00Z',
            '2020-03-23T00:00:00Z',
            'period',
            400,
            {
                'code': 'bad_period',
                'message': 'period.from should be less then period.to',
            },
            id='from > to',
        ),
        pytest.param(
            '2021-03-31T00:00:00Z',
            '2021-03-23T00:00:00Z',
            'period',
            400,
            {
                'code': 'bad_period',
                'message': 'period.from should be less then period.to',
            },
            id='from > now',
        ),
        pytest.param(
            '2020-03-23T01:00:00Z',
            '2020-03-23T01:00:00Z',
            'period',
            400,
            {
                'code': 'bad_period',
                'message': 'period.from should be less then period.to',
            },
            id='from == to',
        ),
        pytest.param(
            '2020-03-23T01:01:00Z',
            '2020-03-24T00:00:00Z',
            'period',
            400,
            {
                'code': 'bad_period',
                'message': 'period.from must be round to hours',
            },
            id='from not round to hours',
        ),
        pytest.param(
            '2020-03-23T00:00:00Z',
            '2020-03-24T01:01:00Z',
            'period',
            400,
            {
                'code': 'bad_period',
                'message': 'period.to must be round to hours',
            },
            id='to not round to hours',
        ),
        pytest.param(
            '2020-03-23T00:00:00Z',
            '2020-03-24T01:00:00Z',
            'days',
            400,
            {
                'code': 'bad_period',
                'message': 'interval must divide on 86400 seconds',
            },
            id='interval not divide to days',
        ),
    ],
)
async def test_time_error(
        mockserver,
        taxi_driver_supply_hours,
        from_time,
        to_time,
        aggregate_by,
        code,
        expected_response,
):
    response = await taxi_driver_supply_hours.post(
        DRIVER_SH_URL,
        json={
            'query': {
                'park': {'id': 'xxx'},
                'supply': {
                    'period': {'from': from_time, 'to': to_time},
                    'aggregate_by': aggregate_by,
                },
            },
        },
    )

    assert response.status_code == code
    assert response.json() == expected_response
