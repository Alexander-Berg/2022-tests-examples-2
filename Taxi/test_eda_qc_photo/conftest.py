# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import contextlib

import pytest

import eda_qc_photo.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['eda_qc_photo.generated.service.pytest_plugins']


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['MDS_S3_AUTH'] = {
        'id': 'some-id',
        'bucket': 'bucket-name',
        'access_key_id': 'access-key-id',
        'secret_key': 'secret-key',
        'url': 'http://some.url',
    }
    return simple_secdist


@pytest.fixture(autouse=True)
def _mock_crons(mock_crons, patch):
    @patch('eda_qc_photo.internal.bot.updater._Distlock.locked')
    @contextlib.contextmanager
    def _locked():
        yield True

    @mock_crons('/v1/task/poll_update/lock/aquire/')
    def _aquire(request):
        return {}

    @mock_crons('/v1/task/poll_update/lock/release/')
    def _release(request):
        return {}
