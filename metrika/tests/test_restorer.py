import pytest


@pytest.mark.parametrize('new_shard, shard', [
    (True, 1),
    (False, 1337)
])
def test_donors(restorer, new_shard, shard):
    restorer.new_shard = new_shard
    restorer.donors
    assert restorer.mtapi.list.fqdn.call_args[1]['shard'] == shard
