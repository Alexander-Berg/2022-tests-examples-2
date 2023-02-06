import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files

EXPERIMENT_NAME = 'experiment'
CONTENT = {
    'market': b'aaaaaaaaa\n',
    'not_market': b'bbbbbbbbb\n',
    None: b'ccccccccc\n',
}

NAMESPACES = ['market', 'not_market', None]


@pytest.mark.parametrize(
    'gen_func,init_func,get_func,get_files_func',
    [
        pytest.param(
            experiment.generate,
            helpers.init_exp,
            helpers.get_experiment,
            files.get_files_by_experiment,
            id='files_in_experiment',
        ),
        pytest.param(
            experiment.generate_config,
            helpers.init_config,
            helpers.get_config,
            files.get_files_by_config,
            id='files_in_config',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_files_in_experiments(
        taxi_exp_client, gen_func, init_func, get_func, get_files_func,
):
    # init exp with files in their respective namespaces
    for namespace in NAMESPACES:
        response = await files.post_file(
            taxi_exp_client,
            'file.txt',
            CONTENT[namespace],
            namespace=namespace,
        )
        assert response.status == 200, await response.text()
        file_id = (await response.json())['id']
        experiment_body = gen_func(
            name=EXPERIMENT_NAME,
            clauses=[
                experiment.make_clause(
                    'first', predicate=experiment.infile_predicate(file_id),
                ),
            ],
            namespace=namespace,
        )

        await init_func(taxi_exp_client, experiment_body, namespace=namespace)

    # get and check files for experiments in namespaces
    for namespace in NAMESPACES:
        exp = await get_func(taxi_exp_client, EXPERIMENT_NAME, namespace)
        assert exp['name'] == EXPERIMENT_NAME
        if namespace is not None:
            assert exp['namespace'] == namespace

        response = await get_files_func(
            taxi_exp_client, EXPERIMENT_NAME, namespace=namespace,
        )
        file_id = (await response.json())['files'][0]['id']
        file_body = await files.get_file_body(taxi_exp_client, file_id)
        assert file_body == CONTENT[namespace]
