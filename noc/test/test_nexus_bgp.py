from noc.grad.grad.user_functions.nexus_bgp import parse_nexus_bgp_uptime


def test_functions_binding():
    assert parse_nexus_bgp_uptime("P9M2DT11H47M56S") == 23543276
    assert parse_nexus_bgp_uptime("P9M2DT11H47M") == 23543220
    assert parse_nexus_bgp_uptime("P5M18DT21M56S") == 14516516
    assert parse_nexus_bgp_uptime("P11DT14H28M20S") == 1002500
    assert parse_nexus_bgp_uptime("P11DT15H7M45S") == 1004865
    assert parse_nexus_bgp_uptime("P9M2DT13H55S") == 23547655
    assert parse_nexus_bgp_uptime("47w5d") == 28857600
    assert parse_nexus_bgp_uptime("P9M16D") == 24710400
    assert parse_nexus_bgp_uptime("1y5w") == 949104000
