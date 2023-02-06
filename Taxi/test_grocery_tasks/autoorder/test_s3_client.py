import datetime
import pathlib

import pytest

from grocery_tasks.autoorder.client import s3 as s3_client
from grocery_tasks.autoorder.data_norm import to_s3


class MdsS3ClientMock:
    def __init__(self):
        self.calls = []

    async def upload_content(self, **kwargs):
        self.calls.append(kwargs)


@pytest.mark.now('2020-01-01T00:00:00')
async def test_upload(get_file_path, open_file):
    file_path = pathlib.Path(get_file_path('result/result.csv'))

    date = datetime.date.today()
    s3_client_mock = MdsS3ClientMock()
    client = s3_client.S3Client(
        s3_client=s3_client_mock,
        date=date,
        local_base_path=str(file_path.parent.absolute()),
    )

    # Act
    await client.upload(
        [
            {
                'src': '{local_base_path}/' + file_path.name,
                'dst': 'autoorder/result/result_{date}.csv',
                'content_type': 'text/csv',
                'reader': to_s3.get_result_dataframe,
            },
        ],
    )
    expected_body = open_file('result/s3_result.csv').read().encode()
    assert s3_client_mock.calls == [
        {
            'key': 'autoorder/result/result_2020-01-01.csv',
            'body': expected_body,
            'content_type': 'text/csv',
        },
    ]
