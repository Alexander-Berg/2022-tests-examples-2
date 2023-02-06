import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'with_traits_experiment'


@pytest.mark.parametrize(
    'st_tickets,status',
    [
        pytest.param([], 200),
        pytest.param(['TAXIEXP-228'], 200),
        pytest.param(['taxiexp-228'], 200),
        pytest.param(['https://st.test.yandex-team.ru/taxiexp-228'], 200),
        pytest.param(['https://st.yandex-team.ru/taxiexp-228'], 200),
        pytest.param(['HTTPS://ST.YANDEX-TEAM.RU/TAXIEXP-228'], 200),
        pytest.param(['TAXIEXP-228', 'TAXIEXP-229'], 200),
        pytest.param(['HTTP://ST.YANDEX-TEAM.RU/TAXIEXP-228'], 400),
        pytest.param(['HTTPS://OTHER.COM/TAXIEXP-228'], 400),
        pytest.param(['TAXIEXP'], 400),
        pytest.param(['228'], 400),
    ],
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_trait_tags(taxi_exp_client, st_tickets, status):
    data = experiment.generate(st_tickets=st_tickets)
    response = await taxi_exp_client.post(
        'v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=data,
    )

    assert response.status == status, await response.text()

    if response.status != 200:
        return

    await helpers.experiment_check_tests(
        taxi_exp_client, EXPERIMENT_NAME, data,
    )
