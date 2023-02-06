import datetime

import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


FILE_NAME = 'file.txt'


@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test(taxi_exp_client):
    now_timestamp = await db.get_current_timestamp(taxi_exp_client.app)
    mds_id = await db.add_or_update_file(taxi_exp_client.app, FILE_NAME)
    await helpers.create_default_exp(
        taxi_exp_client,
        'exp',
        clauses=[
            experiment.make_clause(
                'clause', predicate=experiment.infile_predicate(mds_id),
            ),
        ],
    )
    last_timestamp = (await db.get_history(taxi_exp_client.app))[0][
        'updation_time'
    ]

    dt1 = last_timestamp - now_timestamp
    dt2 = now_timestamp - last_timestamp
    excepted_delta = datetime.timedelta(minutes=5)
    assert dt1 < excepted_delta and dt2 < excepted_delta, f'{dt1}, {dt2}'
