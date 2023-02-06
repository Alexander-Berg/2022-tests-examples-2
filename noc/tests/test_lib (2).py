from noc.packages.mondata_server.mondata.lib.lib import expand_hosts


def test_hostslist():
    result = expand_hosts("test")
    assert result.fqdns == ["test"]
    assert result.names == ["test"]
    assert result.juggler_native_group is False
