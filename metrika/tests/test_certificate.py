import pytest
from datetime import datetime

import metrika.pylib.sh as mtsh
import metrika.pylib.certificate as mpc


class CertificateTestError(Exception):
    pass


def test_init_no_filename_given():
    with pytest.raises(ValueError):
        mpc.Certificate()


def test_init_given_missing_filename():
    with pytest.raises(ValueError):
        mpc.Certificate(filename='/wut?')


def test_init_no_check():
    cert = mpc.Certificate(
        filename='/wut?',
        check_filename_exist=False,
    )
    assert cert.filename == '/wut?'


def test_get_dates_returns(cert, monkeypatch):
    def mock_run(*args, **kwargs):
        return 'notBefore=Mar 12 14:13:04 2019 GMT\n'

    monkeypatch.setattr(mtsh, 'run', mock_run)

    dates = cert.get_dates()

    assert isinstance(
        dates,
        tuple,
    )

    assert isinstance(
        dates[0],
        datetime,
    )

    assert isinstance(
        dates[1],
        datetime,
    )


def test_get_date_invalid_datetype(cert):
    with pytest.raises(ValueError):
        cert.get_date('datetype')


def test_get_date_returns_datetime(cert, monkeypatch):
    def mock_run(*args, **kwargs):
        return 'notBefore=Mar 12 14:13:04 2019 GMT\n'

    monkeypatch.setattr(mtsh, 'run', mock_run)

    assert isinstance(
        cert.get_date('enddate'),
        datetime,
    )


def test_get_date_does_not_catch_mtsh_errors(cert, monkeypatch):
    def mock_run(*args, **kwargs):
        raise CertificateTestError

    monkeypatch.setattr(mtsh, 'run', mock_run)

    with pytest.raises(CertificateTestError):
        cert.get_date('startdate')


def test_get_public_key_from_cert_does_not_catch_mtsh_errors(cert, monkeypatch):
    def mock_run(*args, **kwargs):
        raise CertificateTestError

    monkeypatch.setattr(mtsh, 'run', mock_run)

    with pytest.raises(CertificateTestError):
        cert.get_public_key_from_cert()


def test_get_public_key_from_private_key_does_not_catch_mtsh_errors(cert, monkeypatch):
    def mock_run(*args, **kwargs):
        raise CertificateTestError

    monkeypatch.setattr(mtsh, 'run', mock_run)

    with pytest.raises(CertificateTestError):
        cert.get_public_key_from_private_key()
