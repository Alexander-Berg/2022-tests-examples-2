import datetime

import pytest

from taxi_exp import util
from test_taxi_exp import helpers
from test_taxi_exp.helpers import db

NAME = 'name_for_on_off'


@pytest.mark.parametrize(
    'create_handle,get_handle,on_off_handle',
    [
        pytest.param(
            helpers.create_default_exp,
            helpers.get_experiment,
            helpers.on_off_experiment,
            id='experiment',
        ),
        pytest.param(
            helpers.create_default_conf,
            helpers.get_config,
            helpers.on_off_config,
            id='config',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_experiment_removing': True}},
        'settings': {
            'common': {
                'departments': {'common': {'map_to_namespace': 'market'}},
            },
        },
    },
)
async def test(taxi_exp_client, create_handle, get_handle, on_off_handle):
    await create_handle(taxi_exp_client, NAME, default_value={}, enabled=True)
    response = await get_handle(taxi_exp_client, NAME)
    first_last_manual_update = util.parse_and_clean_datetime(
        response['last_manual_update'],
    )

    last_modified_at = response['last_modified_at']
    for enable in (False, True):
        on_off_response = await on_off_handle(
            taxi_exp_client, NAME, last_modified_at, enable=enable,
        )
        last_modified_at = on_off_response['last_modified_at']
        assert on_off_response['tplatform_namespace'] == 'market'
        response = await get_handle(taxi_exp_client, NAME)
        last_manual_update = util.parse_and_clean_datetime(
            response['last_manual_update'],
        )

        dt1 = last_manual_update - first_last_manual_update
        dt2 = first_last_manual_update - last_manual_update
        excepted_delta = datetime.timedelta(minutes=5)
        assert dt1 < excepted_delta and dt2 < excepted_delta, f'{dt1}, {dt2}'
