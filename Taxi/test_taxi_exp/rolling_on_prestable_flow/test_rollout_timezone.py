import datetime

import pytest

from taxi_exp import util
from taxi_exp.lib import trait_tags as trait_tags_module
from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'Exp:Correct_Name'


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'prestable_flow': True,
                'allow_write_pre_statistics': True,
            },
        },
    },
)
@pytest.mark.pgsql(
    'taxi_exp', queries=[db.ADD_CONSUMER.format('test_consumer')],
)
async def test_get_prestable_flow(taxi_exp_client):
    response = await helpers.init_exp(
        taxi_exp_client,
        experiment.generate(
            NAME,
            trait_tags=[trait_tags_module.PRESTABLE_TAG],
            prestable_flow=experiment.make_prestable_flow(wait_on_prestable=5),
        ),
    )

    # test times
    last_manual_update = util.parse_and_clean_datetime(
        response['last_manual_update'],
    )
    rollout_stable_time = util.parse_and_clean_datetime(
        response['prestable_flow']['rollout_stable_time'],
    )
    dt1 = last_manual_update - rollout_stable_time
    dt2 = rollout_stable_time - last_manual_update
    excepted_delta = datetime.timedelta(minutes=5)
    assert dt1 < excepted_delta and dt2 < excepted_delta, f'{dt1}, {dt2}'
