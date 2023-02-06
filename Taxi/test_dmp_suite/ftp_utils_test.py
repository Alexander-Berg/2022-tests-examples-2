# coding: utf-8
from uuid import uuid4
from ftplib import error_perm
from io import BytesIO

import pytest

from dmp_suite.ftp_utils import FTPAccount, upload_file, download_file
from init_py_env import settings


@pytest.fixture(scope="module")
def account(slow_test_settings):
    with slow_test_settings():
        account = FTPAccount(**settings("ftp.connections.testing"))
    return account


@pytest.fixture
def temporary_path(account):
    path = "/test/" + uuid4().hex
    try:
        yield path
    finally:
        try:
            with account.opened_connection() as connection:
                connection.delete(path)
        except error_perm:
            pass


CONTENT = b"Some binary data: \xde\xad\xbe\xef"


@pytest.mark.slow
def test_upload_then_download(temporary_path, account):
    sent_file = BytesIO()
    write_and_rewind(sent_file, CONTENT)
    upload_file(sent_file, temporary_path, account)

    received_file = BytesIO()
    download_file(temporary_path, received_file, account)

    assert received_file.getvalue() == CONTENT


@pytest.mark.slow
def test_upload_then_download_same_connection(temporary_path, account):
    sent_file = BytesIO()
    write_and_rewind(sent_file, CONTENT)
    with account.opened_connection() as connection:
        upload_file(sent_file, temporary_path, connection)

        received_file = BytesIO()
        download_file(temporary_path, received_file, connection)

    assert received_file.getvalue() == CONTENT


@pytest.mark.slow
def test_upload_prevents_overriding(temporary_path, account):
    sent_file = BytesIO()
    write_and_rewind(sent_file, CONTENT)
    upload_file(sent_file, temporary_path, account)

    with pytest.raises(RuntimeError, match=".*already exists.*"):
        sent_file = BytesIO()
        write_and_rewind(sent_file, CONTENT)
        upload_file(sent_file, temporary_path, account)


@pytest.mark.slow
def test_download_checks_existence(temporary_path, account):
    received_file = BytesIO()
    with pytest.raises(error_perm, match="550.*"):
        download_file(temporary_path, received_file, account)


def write_and_rewind(fp, data):
    fp.write(data)
    fp.seek(0)
