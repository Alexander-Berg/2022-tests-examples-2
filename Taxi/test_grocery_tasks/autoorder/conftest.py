# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
# pylint: disable=protected-access
import typing

import pytest
from yql.api.v1 import client
import yt.wrapper

from grocery_tasks.autoorder.client import s3
from grocery_tasks.autoorder.data_norm import to_yt
from grocery_tasks.autoorder.international import RegionProcessor
from grocery_tasks.utils.jns_client import JNSClient


@pytest.fixture
def ignore_international(monkeypatch):
    async def dummy_async(*args, **kwargs):
        return

    def dummy(*args, **kwargs):
        return

    def dummy_list(*args, **kwargs):
        return []

    monkeypatch.setattr(RegionProcessor, 'download', dummy_async)
    monkeypatch.setattr(RegionProcessor, 'get_downloads', dummy_list)


@pytest.fixture
def mock_s3_client(monkeypatch, load_binary):
    class S3SessionMock:
        async def download_content(
                self, key, bucket_name: typing.Optional[str] = None,
        ) -> bytearray:
            bucket_subpath = ''
            if bucket_name is not None:
                bucket_subpath = f'/{bucket_name}'
            return load_binary(f's3{bucket_subpath}/{key}')

        async def upload_content(self, **kwargs):
            # feel free to implement
            pass

    class S3ClientMock(s3.S3Client):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._s3_client = S3SessionMock()

    monkeypatch.setattr(s3, 'S3Client', S3ClientMock)


@pytest.fixture
def mock_clickhouse(mockserver, load):
    @mockserver.json_handler('/clickhouse', prefix=True)
    def _get(request):
        data = load('clickhouse/sales.csv')
        return mockserver.make_response(data, status=200)


@pytest.fixture(autouse=True)
def mock_yql(monkeypatch, open_file):
    class YqlClientMock:
        class YQLRequest:
            json = {}

            def __init__(self, title='test_operation_id'):
                self.key = title

            @classmethod
            def run(cls):
                pass

            @property
            def share_url(self):
                return ''

            def get_results(self, wait=True):
                class Results:
                    def __init__(self, title='test_operation_id'):
                        self.key = title

                    @property
                    def errors(self):
                        return

                    @property
                    def status(self):
                        return 'COMPLETED'

                    @property
                    def dataframe(self):
                        ret = None
                        if self.key == 'YQL stowage_backlog':
                            ret = to_yt.stowage_backlog(
                                open_file('yql/stowage_backlog.csv'),
                            )
                        elif self.key == 'YQL israel_otw':
                            ret = to_yt.orders_on_the_way(
                                open_file('yql/israel_otw.csv'),
                            )
                        elif self.key == 'YQL stock_wms':
                            ret = to_yt.stock_wms(
                                open_file('yql/stock_wms.csv'),
                            )
                        return ret

                    def __iter__(self):
                        class Result:
                            def __init__(self):
                                pass

                            def fetch_full_data(self):
                                return

                        yield Result()

                return Results(title=self.key)

        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def query(self, query, syntax_version, title):
            return self.YQLRequest(title=title)

    monkeypatch.setattr(client, 'YqlClient', YqlClientMock)


@pytest.fixture
def mock_yt(yt_proxy, yt_client, monkeypatch):
    real_client = yt.wrapper.YtClient
    monkeypatch.setattr(
        yt.wrapper,
        'YtClient',
        lambda proxy=None, token=None, config=None: real_client(
            yt_proxy, token=token, config=config,
        ),
    )

    class YtMock:
        @staticmethod
        def remount(tables):
            # Dyntables records should be flushed on disk for read_table
            if isinstance(tables, str):
                tables = [tables]
            for table in tables:
                yt_client.unmount_table(table, sync=True)
                yt_client.mount_table(table, sync=True)

    return YtMock()


@pytest.fixture
def mock_jns(monkeypatch):
    async def post_with_retry_mock(self, *args, **kwargs):
        return

    monkeypatch.setattr(JNSClient, '_post_with_retry', post_with_retry_mock)
