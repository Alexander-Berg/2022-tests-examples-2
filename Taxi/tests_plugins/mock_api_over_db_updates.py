import datetime
import json
import os
from typing import NamedTuple

import pytest
import pytz


def revision_to_timestamp(revision):
    split = revision.split('_')
    if len(split) == 3:
        # mongo
        split_ints = [int(v) for v in split[1:]]
        return split_ints
    elif len(split) == 2:
        # postgres
        timestr = split[0]
        time = datetime.datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%S+0000')
        return [int(time.timestamp()), int(split[1])]
    else:
        raise ValueError(
            f'invalid api-over-db revision in mock: \'{revision}\'',
        )


def revision_to_datetime(revision):
    timestamp = revision_to_timestamp(revision)
    time = datetime.datetime.fromtimestamp(int(timestamp[0]), pytz.utc)
    return time.strftime('%Y-%m-%dT%H:%M:%SZ')


def mock_updates_handler(
        mockserver, request, array_name, revision_field, docs_array,
):
    last_known_revision = request.json.get('last_known_revision')
    if last_known_revision:
        last_known_ts = revision_to_timestamp(last_known_revision)
        docs_array = [
            p
            for p in docs_array
            if revision_to_timestamp(p[revision_field]) > last_known_ts
        ]
    if docs_array:
        last_revision = docs_array[-1][revision_field]
    else:
        last_revision = last_known_revision
    response_json = {
        'last_modified': revision_to_datetime(last_revision),
        'last_revision': last_revision,
        array_name: docs_array,
    }
    return mockserver.make_response(
        json.dumps(response_json), 200, headers={'X-Polling-Delay-Ms': '0'},
    )


class UpdatesMockInfo(NamedTuple):
    docs_array: list
    array_name: str
    revision_field: str


class UpdatesMock:
    updates_mocks: dict = {}

    def __init__(self, load_json, search_path):
        self.load_json = load_json
        self.search_path = search_path

    def add_updates_mock(
            self, path, docs_filename, array_name, revision_field='revision',
    ):
        dir_paths = list(self.search_path('api_over_db', True))
        docs_array = []
        for dir_path in dir_paths:
            docs_full_filename = os.path.join(dir_path, docs_filename)
            if os.path.isfile(docs_full_filename):
                docs_array = self.load_json(docs_full_filename)
                break
        if not docs_array:
            print(
                f'WARNING: {docs_filename} not found at paths {dir_paths}'
                + ', empty cache mock',
            )
        self.updates_mocks[path] = UpdatesMockInfo(
            docs_array, array_name, revision_field,
        )

    def make_handler_mocks(self, mockserver):
        for path, mock_info in self.updates_mocks.items():

            @mockserver.handler(path)
            def _func(mockserver_request, mock_info=mock_info):
                docs_array = mock_info.docs_array
                array_name = mock_info.array_name
                revision_field = mock_info.revision_field
                return mock_updates_handler(
                    mockserver,
                    mockserver_request,
                    array_name,
                    revision_field,
                    docs_array,
                )


@pytest.fixture(name='api_over_db_updates')
def _mock_api_over_db_updates(load_json, search_path):
    updates_mock = UpdatesMock(load_json, search_path)
    return updates_mock
