import unittest.mock

import pytest

import meta_etl.layer.yt.raw.staff.person.impl


@pytest.fixture
def mock_pd_id_dict():
    return {
        '+79991234567': 'pd_id_1',
    }


@pytest.fixture
def mock_get_pd_id_mapping(monkeypatch, mock_pd_id_dict):
    mock = unittest.mock.Mock(
        return_value=mock_pd_id_dict,
    )

    monkeypatch.setattr(
        meta_etl.layer.yt.raw.staff.person.impl,
        'get_pd_id_mapping',
        mock,
    )
    return mock
