import json
import os
import pytest
import typing

from taxi.antifraud.salesforce_log_sync import __main__ as main
from taxi.antifraud.salesforce_log_sync import salesforce

from reactor_client import reactor_api
import yatest.common


STATIC_DIR_ROOT = 'taxi/antifraud/salesforce_log_sync/tests/static'


def _path(path: str):
    return yatest.common.source_path(os.path.join(STATIC_DIR_ROOT, path))


def _read(path: str):
    with open(_path(path), 'r') as f:
        return f.read()


def _read_json(path: str):
    with open(_path(path), 'r') as f:
        return json.load(f)


LOG_TABLE = '//log_table'
LAST_SYNC_TIME = '//last_sync_time'


@pytest.fixture(scope='module')
def yt_client(yt_stuff):
    yt_client = yt_stuff.get_yt_client()
    main.create_nodes(LOG_TABLE, LAST_SYNC_TIME, ['ApexCallout', 'LightningPageView'], '2021-12-06T11:20:32.000+0000', yt_client)
    return yt_client


def test_fetch(yt_client):
    id_to_file_info = {}

    class MockSfClient:
        calls = 0

        def __init__(self):
            pass

        def all_log_files_since(self, type_: str, since: str):
            self.calls += 1
            res = _read_json(f'fetch/{type_}.json')['records']
            for rec in res:
                id_to_file_info[rec['Id']] = rec

            return res

    class MockReactorClient:
        calls = 0

        def __init__(self):
            pass

        @property
        def artifact_instance(self):
            return self

        @staticmethod
        def instantiate(metadata, *args, **kwargs):
            MockReactorClient.calls += 1
            value = metadata.dict_obj['value']
            data = json.loads(value)
            assert data == id_to_file_info[data['Id']]

    main.fetch(
        types=['ApexCallout', 'LightningPageView'],
        artifact_path='artifact_path',
        last_sync_time_path=LAST_SYNC_TIME,
        salesforce_client=typing.cast(salesforce.SalesforceClient, MockSfClient()),
        yt_client=yt_client,
        reactor_client=typing.cast(reactor_api.ReactorAPIClientV1, MockReactorClient())
    )

    assert MockReactorClient.calls == len(id_to_file_info)


def test_to_yt(yt_client):
    class MockSfClient:
        calls = 0

        def __init__(self):
            pass

        @staticmethod
        def download_file(path_: str):
            MockSfClient.calls += 1
            assert path_ == '/services/data/v53.0/sobjects/EventLogFile/0AT7Y000002k642WAA/LogFile'
            return _read('to_yt/file.csv')

    file_info = _read_json('to_yt/file_info.json')
    sf_client = MockSfClient()

    main.to_yt(
        file_info=file_info,
        path=LOG_TABLE,
        yt_client=yt_client,
        salesforce_client=typing.cast(salesforce.SalesforceClient, sf_client)
    )

    expected_table = _read_json('to_yt/table.json')
    result_table = list(yt_client.select_rows(f'* from [{LOG_TABLE}]'))

    assert expected_table == result_table
