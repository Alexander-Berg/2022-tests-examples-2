import pytest

from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files

EXPERIMENT_NAME = 'experiment'
CONTENT = b"""aaaaaaaaa
bbbbbbbb
cccccccc
dddddddd
eeeeeeee"""


@pytest.mark.parametrize('need_remove_self_ok', [True, False])
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {'common': {'in_set_max_elements_count': 100}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_experiments_history(taxi_exp_client, need_remove_self_ok):
    response = await files.post_file(taxi_exp_client, 'file.txt', CONTENT)
    assert response.status == 200, await response.text()
    first_file_id = (await response.json())['id']

    response = await files.post_file(taxi_exp_client, 'file2.txt', CONTENT)
    assert response.status == 200, await response.text()
    second_file_id = (await response.json())['id']

    data = experiment.generate(
        EXPERIMENT_NAME,
        match_predicate=(
            experiment.allof_predicate(
                [
                    experiment.inset_predicate([1, 2, 3], set_elem_type='int'),
                    experiment.inset_predicate(
                        ['msk', 'spb'],
                        set_elem_type='string',
                        arg_name='city_id',
                    ),
                    experiment.gt_predicate(
                        '1.1.1',
                        arg_name='app_version',
                        arg_type='application_version',
                    ),
                    experiment.infile_predicate(first_file_id),
                    experiment.infile_predicate(second_file_id),
                ],
            )
        ),
        applications=[
            {
                'name': 'android',
                'version_range': {'from': '3.14.0', 'to': '3.20.0'},
            },
        ],
        consumers=[{'name': 'test_consumer'}, {'name': 'launch'}],
        owners=[],
        watchers=[],
        trait_tags=[],
        st_tickets=['TAXIEXP-228'],
    )
    if need_remove_self_ok:
        data.pop('self_ok', None)

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME},
        json=data,
    )
    assert response.status == 200, await response.text()

    # update experiment
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
        json=data,
    )
    assert response.status == 200, await response.text()

    # get experiment by revision
    response = await taxi_exp_client.get(
        '/v1/history/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'revision': 1},
    )
    assert response.status == 200, await response.text()
    content = await response.json()
    assert set(content['files']) == {first_file_id, second_file_id}

    content['body'].pop('created')
    content['body'].pop('last_manual_update')

    # this parameters not presented on normal job
    content['body'].pop('removed')
    content['body'].pop('last_modified_at')
    assert content['body'].pop('self_ok') is False
    assert content['body'].pop('biz_revision') == 1
    if not need_remove_self_ok:
        data.pop('self_ok', None)
    data['name'] = EXPERIMENT_NAME
    assert content['body'] == data
