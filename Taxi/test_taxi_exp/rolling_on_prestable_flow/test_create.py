import pytest

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
@pytest.mark.now(f'{experiment.CURRENT_YEAR}-01-01T00:00:00.000+0000')
async def test_get_prestable_flow(
        taxi_exp_client, patch_util_now, mocked_time,
):
    await helpers.init_exp(
        taxi_exp_client,
        experiment.generate(
            NAME,
            trait_tags=[trait_tags_module.PRESTABLE_TAG],
            prestable_flow=experiment.make_prestable_flow(wait_on_prestable=5),
        ),
    )

    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    check_body = await response.json()
    assert check_body['trait_tags'] == [trait_tags_module.PRESTABLE_TAG]
    assert 'prestable_flow' in check_body, check_body.keys()
    first_wait_on_prestable = check_body['prestable_flow']['wait_on_prestable']

    # check that wait_on_prestable decreases
    mocked_time.sleep(3)
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    latest_wait_on_prestable = (await response.json())['prestable_flow'][
        'wait_on_prestable'
    ]

    assert first_wait_on_prestable > latest_wait_on_prestable

    # check that wait_on_prestable return zero
    mocked_time.sleep(3)
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    latest_wait_on_prestable = (await response.json())['prestable_flow'][
        'wait_on_prestable'
    ]

    assert not latest_wait_on_prestable

    assert [
        item['changes_source']
        for item in await db.get_prestable_events(taxi_exp_client.app)
    ] == ['add']
