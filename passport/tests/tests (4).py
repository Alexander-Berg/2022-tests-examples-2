from passport.backend.tools.as_data_generator.utils import ipv6_to_int


def test_ipv6_to_int_ok():
    assert ipv6_to_int('::1') == 1
