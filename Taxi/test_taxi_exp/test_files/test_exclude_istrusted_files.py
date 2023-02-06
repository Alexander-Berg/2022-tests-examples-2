# pylint: disable=line-too-long
import pytest

from taxi.clients import mds_s3

from test_taxi_exp.helpers import files


@pytest.mark.pgsql('taxi_exp', files=('trusted_and_non_trusted_files.sql',))
async def test_exclude_istrusted_files(taxi_exp_client, patch):
    # path mock for s3_mds
    async def download_content(key):
        obj = mds_s3.S3Object(
            Key=key, Body=b'', ETag=taxi_exp_client.app.s3_client.etag,
        )
        return obj.body

    taxi_exp_client.app.s3_client.download_content = download_content

    # search files
    response = await files.search_file(taxi_exp_client, name='trusted')
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 1
    assert (
        result['files'][0]['id']
        == 'non_trusted_c22efcd0226f40fa868a0143f344a3ef'
    )  # noqa

    # get file by experiment
    response = await files.get_files_by_experiment(
        taxi_exp_client, name='trusted_files',
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['files']) == 1
    assert (
        result['files'][0]['id']
        == 'non_trusted_c22efcd0226f40fa868a0143f344a3ef'
    )  # noqa

    # download trusted file
    response = await files.get_file_redirect(
        taxi_exp_client, 'trusted_ec2f695e09044105bce60bdffd6a36ce',
    )
    assert response.status == 200

    # download non-trusted file
    response = await files.get_file_redirect(
        taxi_exp_client, 'non_trusted_c22efcd0226f40fa868a0143f344a3ef',
    )
    assert response.status == 200
