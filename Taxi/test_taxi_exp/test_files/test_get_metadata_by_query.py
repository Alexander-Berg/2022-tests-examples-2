import pytest

from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files

NAME = 'n1'


@pytest.mark.parametrize(
    'add_url, get_url, is_config',
    [('configs', 'by_config', True), ('experiments', 'by_experiment', False)],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_get_history_files_by_experiment(
        taxi_exp_client, add_url, get_url, is_config,
):
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content',
    )
    assert response.status == 200
    file_id = (await response.json())['id']

    generator = (
        experiment.generate_config
        if is_config
        else experiment.generate_default
    )

    body = generator(
        clauses=[
            experiment.make_clause(
                'title', predicate=experiment.infile_predicate(file_id),
            ),
        ],
    )
    response = await taxi_exp_client.post(
        f'/v1/{add_url}/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': NAME},
        json=body,
    )
    assert response.status == 200

    response = await taxi_exp_client.get(
        f'/v1/files/{get_url}/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'n1'},
    )
    data = await response.json()
    assert data == {
        'files': [
            {
                'experiment_name': None,
                'file_type': 'string',
                'namespace': None,
                'id': file_id,
                'metadata': {
                    'file_format': 'string',
                    'file_size': 13,
                    'lines': 1,
                    'sha256': (
                        'fd697d20f5d280279e4bab06823d149db'
                        '6d1cf176f25c7a7c1cfb58430ee36fa'
                    ),
                },
                'name': 'file_1.txt',
                'removed': False,
                'version': 1,
            },
        ],
        'linked_files': [],
    }
