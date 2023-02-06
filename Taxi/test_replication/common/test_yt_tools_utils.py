import pytest

from replication import settings
from replication.common.yt_tools import utils


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'client_name,primary_medium,ssd_blobs_enabled,expected',
    [
        ('arni', 'default', False, 'default'),
        ('hahn', 'default', True, 'default'),
        ('hahn', None, True, None),
        ('seneca-vla', 'default', False, 'default'),
        ('seneca-vla', None, False, None),
        ('seneca-vla', None, True, 'ssd_blobs'),
    ],
)
def test_get_primary_medium(
        monkeypatch, client_name, primary_medium, ssd_blobs_enabled, expected,
):
    monkeypatch.setattr(settings, 'YT_SSD_BLOBS_ENABLED', ssd_blobs_enabled)
    assert expected == utils.get_primary_medium(client_name, primary_medium)
