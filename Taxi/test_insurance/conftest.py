# pylint: disable=redefined-outer-name
import uuid

import pytest

import insurance.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['insurance.generated.service.pytest_plugins']


@pytest.fixture
def mock_uuid_uuid4(monkeypatch, mock):
    @mock
    def _dummy_uuid4():
        return uuid.UUID(int=0, version=4)

    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)
