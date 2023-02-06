

import pytest

from app.utils import AppSecDiscoveryClient


@pytest.mark.filterwarnings("ignore")
def test_owner_resolver():
    fqdn = 'bbsrvt01f.browser.yandex.net'
    owners = AppSecDiscoveryClient.get_resp_by_fqdn(fqdn)
    assert len(owners) == 2
