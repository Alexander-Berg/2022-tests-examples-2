from sandbox.projects.yabs.qa.utils.bstr import parse_base_filename

import pytest


@pytest.mark.parametrize(["base_filename", "base_ver", "base_name"], [
    ("3384585235.bs_st013.yabs", "3384585235", "bs_st013"),
    ("3384585235.bs_st013.yabs.zstd_7", "3384585235", "bs_st013"),
    ("3384585235..yabs", None, None),
    ("3384585235.bs_st013", None, None),
    ("bs_st013.yabs", None, None),
])
def test_parse_base_filename(base_filename, base_ver, base_name):
    assert (base_ver, base_name) == parse_base_filename(base_filename)
