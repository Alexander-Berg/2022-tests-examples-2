import pytest

from supportai_lib.tasks import base_task
from taxi.clients import mds_s3

from supportai_learn.stq import learn_processing


@pytest.mark.download_ml_resource(attrs={'type': 'base_bert'})
@pytest.mark.enable_ml_handler(url_path='/base_bert/v1')
@pytest.mark.pgsql('supportai_learn', files=['learn.sql'])
async def test_learn_model(stq3_context, patch, load_binary, create_task):
    @patch('taxi.clients.mds_s3.MdsS3Client.download_content')
    async def _download_content(*args, **kwargs):
        return load_binary('learn_data.xlsx')

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_file_multipart')
    async def _upload_content_multi(*args, **kwargs):
        return mds_s3.S3Object(
            Key='mds-id', ETag=None, Size=kwargs['file_size'],
        )

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _upload_content(*args, **kwargs):
        return mds_s3.S3Object(
            Key='mds-id', ETag=None, Size=len(kwargs['body']),
        )

    task = create_task(type_='local_learn', file_id='1')

    await learn_processing.task(stq3_context, 1, task_id=task.id)

    assert (
        task.status == base_task.TaskStatus.COMPLETED.value
    ), task.error_message
