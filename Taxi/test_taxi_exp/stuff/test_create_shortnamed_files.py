import pathlib

import pytest

from taxi_exp.generated.cron import run_cron as cron_run
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files

EXPERIMENT_NAME = 'fix_file'


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.usefixtures('set_and_clean_cache_path')
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
@pytest.mark.now('2019-01-09T12:00:00')
async def test_create_short_named_file(taxi_exp_client, monkeypatch):
    # post file
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content',
    )
    assert response.status == 200
    first_file_id = (await response.json())['id']

    # create an experiment using file
    exp_body = experiment.generate(
        EXPERIMENT_NAME,
        match_predicate=experiment.infile_predicate(first_file_id),
        action_time={
            'from': '2019-01-01T00:00:00+0300',
            'to': '2019-12-31T23:59:59+0300',
        },
    )
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=exp_body,
    )
    assert response.status == 200

    # check file not in cache
    cached_files = [
        file
        for file in pathlib.Path(
            taxi_exp_client.app.files_snapshot_path,
        ).iterdir()
    ]
    assert not cached_files

    # get file for filling cache
    response = await files.get_file_redirect(taxi_exp_client, first_file_id)
    assert response.status == 200

    # check file in cache
    cached_files = [
        file
        for file in pathlib.Path(
            taxi_exp_client.app.files_snapshot_path,
        ).iterdir()
    ]
    assert len(cached_files) == 1
    assert first_file_id in cached_files[0].name

    # running cron for create shortnamed file into cache
    await cron_run.main(['taxi_exp.stuff.optimize_file_cache', '-t', '0'])

    # check no file in cache
    cached_files = [
        file
        for file in pathlib.Path(
            taxi_exp_client.app.files_snapshot_path,
        ).iterdir()
    ]
    assert [True for file in cached_files if first_file_id in file.name] == [
        True,
        True,
    ]
