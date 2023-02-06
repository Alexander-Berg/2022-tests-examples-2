import datetime

import pytest

from taxi_exp import util
from test_taxi_exp import helpers
from test_taxi_exp.helpers import db

NAME = 'EXP_name_for_remove'


@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_experiment_removing': True}},
    },
)
async def test(taxi_exp_client):
    await helpers.create_default_exp(taxi_exp_client, NAME, default_value={})
    response = await helpers.get_experiment(taxi_exp_client, NAME)
    first_last_manual_update = util.parse_and_clean_datetime(
        response['last_manual_update'],
    )

    await helpers.remove_exp(
        taxi_exp_client, NAME, response['last_modified_at'],
    )
    response = await db.get_experiment(taxi_exp_client.app, NAME)
    last_manual_update = response['exp_removed_stamp']

    dt1 = last_manual_update - first_last_manual_update
    dt2 = first_last_manual_update - last_manual_update
    excepted_delta = datetime.timedelta(minutes=5)
    assert dt1 < excepted_delta and dt2 < excepted_delta, f'{dt1}, {dt2}'
