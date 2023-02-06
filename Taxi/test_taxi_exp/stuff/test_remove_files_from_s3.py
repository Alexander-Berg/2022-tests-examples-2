import pytest

from taxi_exp.generated.cron import run_cron as cron_run
from taxi_exp.lib.app_configs import s3_cleaning_settings
from taxi_exp.stuff import clean_files
from taxi_exp.util import pg_helpers
from test_taxi_exp.helpers import db


@pytest.fixture(autouse=True)
async def _mock_s3(mds_s3_client, patch):
    @patch('taxi.clients.mds_s3.MdsS3Client.delete_objects')
    async def _delete_objects(*args, **kwargs):
        return await mds_s3_client.delete_objects(*args, **kwargs)


@pytest.mark.pgsql(
    'taxi_exp', queries=[db.INIT_QUERY], files=['removed_files.sql'],
)
async def test_remove_files(taxi_exp_client, mds_s3_client):
    # fill s3 before remove
    mds_s3_client._storage = {  # pylint: disable=protected-access
        'aaaaaaaa': b'',
        'bbbbbbbb': b'',
        'cccccccc': b'',
        # 'dddddddd': b'',  # file not existed in s3
    }

    # run
    await clean_files.clean_removed_files_from_s3(
        app=taxi_exp_client.app,
        remove_settings=s3_cleaning_settings.RemoveSettings(),
        real_run=True,
    )

    # check
    assert all(
        not mds_s3_client.has_object(key)
        for key in (
            'aaaaaaaa',
            'bbbbbbbb',
            # 'cccccccc',  # file not marked as removed
            'ddddddd',
        )
    ), 'All files must be removed from s3'
    assert [
        item['mds_id']
        for item in await pg_helpers.fetch(
            taxi_exp_client.app['pool'],
            'SELECT mds_id FROM clients_schema.files;',
        )
    ] == ['cccccccc'], 'All files must be removed from postgres'


@pytest.mark.pgsql(
    'taxi_exp', queries=[db.INIT_QUERY], files=['tags_for_mark.sql'],
)
async def test_mark_tags(taxi_exp_client):
    # run
    await clean_files.mark_tags_as_removed(
        app=taxi_exp_client.app,
        mark_settings=s3_cleaning_settings.MarkSettings(
            chunk_size=10,
            global_threshold=1,
            groups_settings={
                '__default__': s3_cleaning_settings.MarkGroupSettings(
                    limit=10, threshold=1, enabled=True,
                ),
                'taxi': s3_cleaning_settings.MarkGroupSettings(),
            },
        ),
        real_run=True,
    )

    # check
    result = await pg_helpers.fetch(
        taxi_exp_client.app['pool'],
        'SELECT mds_id, removed FROM clients_schema.files;',
    )
    assert all(
        item['removed']
        for item in result
        if item['mds_id'] in {'aaaaaaaa', 'bbbbbbbb'}
    ), result


@pytest.mark.pgsql(
    'taxi_exp', queries=[db.INIT_QUERY], files=['files_for_mark.sql'],
)
async def test_mark_files(taxi_exp_client):
    # run
    await clean_files.mark_files_as_removed(
        app=taxi_exp_client.app,
        mark_settings=s3_cleaning_settings.MarkSettings(
            chunk_size=2,
            global_threshold=1,
            groups_settings={
                '__default__': s3_cleaning_settings.MarkGroupSettings(
                    limit=10, threshold=1, enabled=True,
                ),
                'taxi.non_processed': s3_cleaning_settings.MarkGroupSettings(),
                'common.another': s3_cleaning_settings.MarkGroupSettings(
                    limit=10, threshold=1, enabled=True,
                ),
            },
        ),
        real_run=True,
    )

    # check
    result = await pg_helpers.fetch(
        taxi_exp_client.app['pool'],
        'SELECT mds_id, removed FROM clients_schema.files;',
    )
    assert all(
        item['removed']
        for item in result
        if item['mds_id'] in {'zzzzzzzz', 'yyyyyyyy'}
    ), result


@pytest.mark.pgsql(
    'taxi_exp',
    queries=[db.INIT_QUERY],
    files=['files_for_mark.sql', 'tags_for_mark.sql'],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {},
        'settings': {
            'backend': {
                's3_cleaning': {
                    'real_run': True,
                    'remove_settings': {
                        'chunk_size': 100,
                        'max_iterations': 100,
                    },
                    'files_marking_settings': {
                        'chunk_size': 2,
                        'global_threshold': 1,
                        'groups_settings': {
                            '__default__': {
                                'limit': 10,
                                'threshold': 1,
                                'enabled': True,
                            },
                            'taxi.non_processed': {'enabled': False},
                            'common.another': {
                                'limit': 10,
                                'threshold': 1,
                                'enabled': True,
                            },
                        },
                    },
                    'tags_marking_settings': {
                        'chunk_size': 10,
                        'global_threshold': 1,
                        'groups_settings': {
                            '__default__': {
                                'limit': 10,
                                'threshold': 1,
                                'enabled': True,
                            },
                            'taxi': {
                                'limit': 10,
                                'threshold': 1,
                                'enabled': True,
                            },
                        },
                    },
                },
            },
        },
    },
)
async def test_run_crontask(taxi_exp_client, mds_s3_client):
    # fill s3 before remove
    mds_s3_client._storage = {  # pylint: disable=protected-access
        'aaaaaaaa': b'',
        'bbbbbbbb': b'',
        'cccccccc': b'',
        # 'dddddddd': b'',  # file not existed in s3
        'eeeeeeee': b'',
        'ffffffff': b'',
        'zzzzzzzz': b'',
        'yyyyyyyy': b'',
        'xxxxxxxx': b'',
        'tttttttt': b'',
        'rrrrrrrr': b'',
        'wwwwwwww': b'',
    }

    # run
    await cron_run.main(['taxi_exp.stuff.clean_files', '-t', '0'])

    # check mds
    assert all(
        not mds_s3_client.has_object(key)
        for key in (
            'aaaaaaaa',
            'bbbbbbbb',
            # 'cccccccc',  # file not marked as removed
            # 'ddddddd',  # file not existed in s3
            'eeeeeeee',
            'ffffffff',
            'tttttttt',
            'rrrrrrrr',
            'wwwwwwww',
        )
    ), 'All files must be removed from s3'

    # check postgres
    result = await pg_helpers.fetch(
        taxi_exp_client.app['pool'],
        'SELECT mds_id, removed FROM clients_schema.files;',
    )
    assert sorted(item['mds_id'] for item in result) == sorted(
        (
            'cccccccc',
            'dddddddd',
            'ffffffff',
            'tttttttt',
            'rrrrrrrr',
            'wwwwwwww',
            'xxxxxxxx',
        ),
    )
