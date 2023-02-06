# -*- coding: utf-8 -*-
from io import BytesIO
import json

import mock
from passport.backend.core.builders.base.faker.fake_builder import BaseFakeBuilder
from passport.backend.takeout.common.builders import (
    AsyncServiceBuilder,
    AsyncUploadServiceBuilder,
    STATUS_OK,
    SyncServiceBuilder,
)


def service_ok_response(status=STATUS_OK, files=None, file_links=None, job_id=None):
    rv = {'status': status}
    if files is not None:
        rv['data'] = files
    if file_links is not None:
        rv['file_links'] = file_links
    if job_id is not None:
        rv['job_id'] = job_id
    return json.dumps(rv).encode('utf-8')


def service_error_response(error):
    return json.dumps(dict(
        status='error',
        error=error,
    )).encode('utf-8')


def raw_file_response(file_name, content, content_disposition=None, status_code=200):
    return mock.Mock(
        status_code=status_code,
        content=content,
        raw=BytesIO(content),
        headers={
            'content-disposition': content_disposition or 'attachment; filename=%s' % file_name,
        },
        encoding='utf-8',
    )


class FakeSyncServiceBuilder(BaseFakeBuilder):
    def __init__(self):
        super(FakeSyncServiceBuilder, self).__init__(SyncServiceBuilder)


class FakeAsyncServiceBuilder(BaseFakeBuilder):
    def __init__(self):
        super(FakeAsyncServiceBuilder, self).__init__(AsyncServiceBuilder)


class FakeAsyncUploadServiceBuilder(BaseFakeBuilder):
    def __init__(self):
        super(FakeAsyncUploadServiceBuilder, self).__init__(AsyncUploadServiceBuilder)
