import pathlib

import pytest

from taxi_exp.generated.cron import run_cron as cron_run
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import files


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.usefixtures('set_and_clean_cache_path')
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
@pytest.mark.now('2019-01-09T12:00:00')
async def test_remove_deleted_files(taxi_exp_client):
    # post file
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', b'test_content',
    )
    assert response.status == 200
    first_file_id = (await response.json())['id']

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

    # mark file is removed
    await files.delete_file(taxi_exp_client, first_file_id, 1)

    # running cron for remove file from cache
    await cron_run.main(['taxi_exp.stuff.optimize_file_cache', '-t', '0'])

    # check no file in cache
    cached_files = [
        file
        for file in pathlib.Path(
            taxi_exp_client.app.files_snapshot_path,
        ).iterdir()
    ]
    assert not cached_files
