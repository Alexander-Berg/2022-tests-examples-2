"""Script checks exabgp module and try to resolve "localhost",
correct check is possible with /etc/hosts records:
127.0.0.1	localhost
::1             localhost
"""


import os
import pytest
import modules.exabgp as exabgp


@pytest.yield_fixture(autouse=True, scope="session")
def filename():
    exabgp.EXABGP_IN_FN = "exabgp_test"
    exabgp.ADD_ANNOUNCE = "announce route 127.0.0.127/32 path-information 127.0.0.1 next-hop 127.0.0.1 local-preference 100 community 13238:1011\n"
    exabgp.DEL_ANNOUNCE = "withdraw route 2a02:6b8::1/128 path-information 127.0.0.1 next-hop ::1 local-preference 100 community 13238:1011\n"
    yield
    os.unlink(exabgp.EXABGP_IN_FN)


def test_add_announce():
    (is_successful, _) = exabgp.add_announce("127.0.0.127", ["localhost"])
    assert is_successful
    assert exabgp.ADD_ANNOUNCE == open(exabgp.EXABGP_IN_FN, "r").readline()


def test_remove_announce():
    (is_successful, _) = exabgp.del_announce("2a02:6b8::1", ["localhost"])
    assert is_successful
    assert exabgp.DEL_ANNOUNCE == open(exabgp.EXABGP_IN_FN, "r").readline()
