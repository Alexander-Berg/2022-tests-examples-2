import datetime

import pytest

from taxi.util import dates

from taxi_exp import util
from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


@pytest.mark.parametrize(
    'params,check_time,expected_names',
    [
        ({}, '2020-03-01T00:00:12.000+0000', ['first', 'second', 'third']),
        (
            {'show_active': 'true', 'show_expired': 'true'},
            '2020-03-02T00:00:50.000+0000',
            ['first', 'second', 'third'],
        ),
        (
            {'show_active': 'true'},
            '2020-03-01T00:00:50.000+0000',
            ['first', 'second', 'third'],
        ),
        ({'show_expired': 'true'}, '2020-03-01T00:00:50.000+0000', []),
        (
            {'show_active': 'true'},
            '2020-03-02T00:00:50.000+0000',
            ['second', 'third'],
        ),
        ({'show_expired': 'true'}, '2020-03-02T00:00:50.000+0000', ['first']),
        ({'show_active': 'true'}, '2020-03-04T00:00:50.000+0000', []),
        (
            {'show_expired': 'true'},
            '2020-03-04T00:00:50.000+0000',
            ['first', 'second', 'third'],
        ),
    ],
)
@pytest.mark.now('2020-03-01T00:00:12.000+0000')
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test(
        taxi_exp_client,
        patch_util_now,
        mocked_time,
        params,
        check_time,
        expected_names,
):
    data = experiment.generate_default()
    last_day = datetime.datetime.now() - datetime.timedelta(days=1)
    current_day = datetime.datetime.now()
    next_day = datetime.datetime.now() + datetime.timedelta(days=1)
    next_next_day = datetime.datetime.now() + datetime.timedelta(days=2)

    # adding experiments
    for name, action_time in (
            (
                'first',
                {
                    'from': util.to_moscow_isoformat(last_day),
                    'to': util.to_moscow_isoformat(next_day),
                },
            ),
            (
                'second',
                {
                    'from': util.to_moscow_isoformat(last_day),
                    'to': util.to_moscow_isoformat(next_next_day),
                },
            ),
            (
                'third',
                {
                    'from': util.to_moscow_isoformat(current_day),
                    'to': util.to_moscow_isoformat(next_next_day),
                },
            ),
    ):
        data['match']['action_time'] = action_time
        data['name'] = name
        await helpers.add_checked_exp(taxi_exp_client, data)
    assert len(await db.get_all_experiments(taxi_exp_client.app)) == 3

    # setup check time
    mocked_time.set(dates.parse_timestring(check_time))

    # obtaining list
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    assert response.status == 200
    result = await response.json()
    assert [item['name'] for item in result['experiments']] == expected_names
