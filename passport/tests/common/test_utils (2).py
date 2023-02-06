# -*- coding: utf-8 -*-
from io import BytesIO
import json

from passport.backend.takeout.common.conf import get_config
from passport.backend.takeout.common.conf.crypto import get_keys_for_encrypting
from passport.backend.takeout.common.conf.services import get_service_configs
from passport.backend.takeout.common.crypto import decrypt_stream
from passport.backend.takeout.common.utils import (
    download_file_links_and_encrypt_and_upload_to_s3,
    filename_and_key_version_to_s3_key,
    request_id_pop,
    s3_key_to_filename_and_key_version,
)
from passport.backend.takeout.test_utils.base import BaseTestCase
from passport.backend.takeout.test_utils.fake_builders import service_ok_response
from passport.backend.utils.string import smart_bytes
import pytest


@pytest.mark.parametrize(
    ['filename', 'key_version', 's3_key'],
    [
        ('test', 1, 'test.kv1'),
        ('test', '1', 'test.kv1'),
        ('test.kv1', 2, 'test.kv1.kv2'),
    ],
)
def test_filename_and_key_version_to_s3_key_ok(filename, key_version, s3_key):
    assert filename_and_key_version_to_s3_key(filename, key_version) == s3_key


@pytest.mark.parametrize(
    ['filename', 'key_version'],
    [
        ('test', None),
    ],
)
def test_filename_and_key_version_to_s3_key_error(filename, key_version):
    with pytest.raises(ValueError):
        filename_and_key_version_to_s3_key('test', None)


@pytest.mark.parametrize(
    ['s3_key', 'filename', 'key_version'],
    [
        ('test.kv1', 'test', 1),
        ('test.kv123', 'test', 123),
        ('test.kv1.kv2', 'test.kv1', 2),
    ],
)
def test_s3_key_to_filename_and_key_version_ok(s3_key, filename, key_version):
    assert s3_key_to_filename_and_key_version(s3_key) == (filename, key_version)


@pytest.mark.parametrize(
    's3_key',
    [
        'test',
        'test.',
        'test.kv',
        'test.kv1 ',
        'test.kv1.',
    ],
)
def test_s3_key_to_filename_and_key_version_error(s3_key):
    with pytest.raises(ValueError):
        s3_key_to_filename_and_key_version(s3_key)


@pytest.mark.parametrize(
    ['request_id', 'after_pop'],
    [
        ('', ''),
        ('foo', ''),
        ('foo,bar', 'foo'),
        ('foo,bar,zar', 'foo,bar'),
    ],
)
def test_request_id_pop(request_id, after_pop):
    assert request_id_pop(request_id) == after_pop


class TestCaseDownloadEncryptUpload(BaseTestCase):
    def test_ascii(self):
        self._test_integrational('content')

    def test_unicode(self):
        self._test_integrational(u'Günaydın')

    def _test_integrational(self, file_content):
        keys = get_keys_for_encrypting()
        key_version = get_config()['s3']['encryption_key_version']

        download_file_links_and_encrypt_and_upload_to_s3(
            uid=123,
            extract_id=456,
            service_name='test-service',
            builder=None,
            builder_response=json.loads(service_ok_response(
                status='ok',
                files={
                    'filename': file_content,
                },
            )),
        )
        assert len(self.s3_faker.calls_by_method('put_object')) == 1
        encrypted_fileobj = self.s3_faker.calls_by_method('put_object')[0]['Body']

        encrypted_data = []
        while True:
            read = encrypted_fileobj.read(1)
            if not read:
                break
            encrypted_data.append(read)
        encrypted_data = b''.join(encrypted_data)
        assert encrypted_data

        decrypted_fileobj = decrypt_stream(
            BytesIO(encrypted_data),
            keys,
            key_version,
            len(encrypted_data),
        )
        assert decrypted_fileobj.read() == smart_bytes(file_content)


class TestGetServiceConfigs(BaseTestCase):
    def test_no_input_services(self):
        services = get_service_configs()
        result_services_names = {'fake_async', 'fake_async_upload', 'fake_sync', 'passport'}

        assert set(services.keys()) == result_services_names

    def test_with_input_services(self):
        services = get_service_configs(services=['fake_async', 'does not exist service'])
        result_services_names = {'fake_async', }

        assert set(services.keys()) == result_services_names
