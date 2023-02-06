import datetime

import pytest

from taxi_exp.generated.cron import run_cron as cron_run
from test_taxi_exp.helpers import db


@pytest.mark.pgsql('taxi_exp', files=('one_history_items.sql',))
async def test_mark_one_as_non_broken(taxi_exp_client):
    await cron_run.main(['taxi_exp.stuff.check_kwargs_history', '-t', '0'])

    kwargs_history = await db.get_kwargs_history(taxi_exp_client.app)
    assert all(
        (
            not kwargs_history_item['is_broken']
            for kwargs_history_item in kwargs_history
        ),
    )


def _convert_to_json(items):
    return [{**item} for item in items]


@pytest.mark.now('2019-01-09T12:00:00')
@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(
            [
                {
                    'consumer': 'test_consumer',
                    'history': (
                        '{"kwargs": [], '
                        '"updated": "2019-01-09T12:00:00+03:00", '
                        '"metadata": {}, "library_version": "1"}'
                    ),
                    'id': 1,
                    'is_broken': False,
                    'updation_time': datetime.datetime(2019, 1, 9, 12, 0),
                },
                {
                    'consumer': 'test_consumer',
                    'history': (
                        '{"kwargs": [{"name": "phone_id", "type": "string", '
                        '"is_mandatory": false}], '
                        '"updated": "2019-01-09T13:00:00+03:00", '
                        '"metadata": {}, "library_version": "2-non-broken"}'
                    ),
                    'id': 2,
                    'is_broken': False,
                    'updation_time': datetime.datetime(2019, 1, 9, 13, 0),
                },
                {
                    'consumer': 'test_consumer',
                    'history': (
                        '{"kwargs": ['
                        '{"name": "phone_id", '
                        '"type": "datetime", "is_mandatory": false}], '
                        '"updated": "2019-01-09T14:00:00+03:00", '
                        '"metadata": {}, "library_version": "3-broken"}'
                    ),
                    'id': 3,
                    'is_broken': True,
                    'updation_time': datetime.datetime(2019, 1, 9, 14, 0),
                },
                {
                    'consumer': 'test_consumer',
                    'history': (
                        '{"kwargs": [], '
                        '"updated": "2019-01-09T15:00:00+03:00", '
                        '"metadata": {}, "library_version": "4-broken"}'
                    ),
                    'id': 4,
                    'is_broken': True,
                    'updation_time': datetime.datetime(2019, 1, 9, 15, 0),
                },
            ],
            marks=pytest.mark.pgsql('taxi_exp', files=('happy_path.sql',)),
        ),
    ],
)
async def test_mark_full_history(expected, taxi_exp_client):
    await cron_run.main(['taxi_exp.stuff.check_kwargs_history', '-t', '0'])

    kwargs_history = _convert_to_json(
        await db.get_kwargs_history(taxi_exp_client.app),
    )

    assert kwargs_history == expected
