from unittest.mock import patch

from bird_proto import check_bird_bgp, parse_birdc_show_proto
from tt_main.constants import CRIT_STATUS, OK_STATUS, WARN_STATUS

OUTPUT_SKEL = """BIRD 1.6.8 ready.
name     proto    table    state  since       info
direct0  Direct   master   up     2020-11-27
kernel1  Kernel   master   up     2020-11-27
device1  Device   master   up     2020-11-27
b_core_2 BGP      master   up     2020-11-27  Established
b_core_4 BGP      master   up     15:13:01    Established
b_bfd    BFD      master   up     2020-11-27
b_vrf_hbf_3 BGP      master   up     2020-12-01  Established
b_vrf_hbf_5 BGP      master   up     15:13:00    Established"""


def test_bgp_is_good():
    v6_output = v4_output = OUTPUT_SKEL
    p1 = patch("bird_proto.system.make_cmd_call",
               side_effect=[v4_output.splitlines(),
                            v6_output.splitlines()])
    p2 = patch("bird_proto.os.access", return_value=True)
    p1.start()
    p2.start()
    status, res = check_bird_bgp()
    assert status == OK_STATUS
    assert res == "OK"


def test_session_down():
    v4_output = OUTPUT_SKEL
    v6_output = OUTPUT_SKEL + \
        "\nb_core_6 BGP master start 14:45:41 Connect  Error: BFD session down"
    p1 = patch("bird_proto.system.make_cmd_call",
               side_effect=[v4_output.splitlines(),
                            v6_output.splitlines()])
    p2 = patch("bird_proto.os.access", return_value=True)
    p1.start()
    p2.start()
    status, res = check_bird_bgp()
    assert status == CRIT_STATUS
    assert res == "birdc6: b_core_6 is not established"


def test_no_birdc():
    v6_output = OUTPUT_SKEL
    p1 = patch("bird_proto.system.make_cmd_call",
               side_effect=[v6_output.splitlines(),
                            v6_output.splitlines()])
    p2 = patch("bird_proto.os.access", side_effect=[False, True])
    p1.start()
    p2.start()
    status, res = check_bird_bgp()
    assert status == CRIT_STATUS
    assert res == "/usr/sbin/birdc is not executable"


def test_cmd_call_returned_nothing():
    v6_output = OUTPUT_SKEL
    p1 = patch("bird_proto.system.make_cmd_call",
               side_effect=[[],
                            v6_output.splitlines()])
    p2 = patch("bird_proto.os.access", return_value=True)
    p1.start()
    p2.start()
    status, res = check_bird_bgp()
    assert status == WARN_STATUS
    assert res == "birdc: no BGP sessions found"


def test_session_disabled():
    v6_output = OUTPUT_SKEL
    v4_output = OUTPUT_SKEL + \
        "\nb_core_6 BGP      master   down   14:31:43"
    p1 = patch("bird_proto.system.make_cmd_call",
               side_effect=[v4_output.splitlines(),
                            v6_output.splitlines()])
    p2 = patch("bird_proto.os.access", return_value=True)
    p1.start()
    p2.start()
    status, res = check_bird_bgp()
    assert status == CRIT_STATUS
    assert res == "birdc: b_core_6 is not established"


def test_no_bgp_sessions():
    v4_output = OUTPUT_SKEL[:100]
    v6_output = OUTPUT_SKEL[:100]
    p1 = patch("bird_proto.system.make_cmd_call",
               side_effect=[v4_output.splitlines(),
                            v6_output.splitlines()])
    p2 = patch("bird_proto.os.access", return_value=True)
    p1.start()
    p2.start()
    status, res = check_bird_bgp()
    assert status == WARN_STATUS
    assert "birdc: no BGP sessions found; birdc6: no BGP" in res


def test_multiple_sessions_down():
    v4_output = OUTPUT_SKEL + \
        "\nb_core_6 BGP      master   down   14:31:43"
    v6_output = OUTPUT_SKEL + \
        "\nb_core_6 BGP master start 14:45:41 Connect  Error: xxx" + \
        "\nb_core_8 BGP master start 14:45:41 Connect  Error: xxx"
    p1 = patch("bird_proto.system.make_cmd_call",
               side_effect=[v4_output.splitlines(),
                            v6_output.splitlines()])
    p2 = patch("bird_proto.os.access", return_value=True)
    p1.start()
    p2.start()
    status, res = check_bird_bgp()
    assert status == CRIT_STATUS
    assert "birdc: b_core_6" in res
    assert "birdc6: b_core_6" in res
    assert "birdc6: b_core_8" in res


def test_multiple_problems():
    v4_output = OUTPUT_SKEL + \
        "\nb_core_6 BGP      master   down   14:31:43"
    v6_output = OUTPUT_SKEL[:100]
    p1 = patch("bird_proto.system.make_cmd_call",
               side_effect=[v4_output.splitlines(),
                            v6_output.splitlines()])
    p2 = patch("bird_proto.os.access", return_value=True)
    p1.start()
    p2.start()
    status, res = check_bird_bgp()
    assert status == CRIT_STATUS
    assert "birdc6: no BGP sessions found" in res
    assert "birdc: b_core_6" in res


def test_parse_show_proto_header():
    line = "name     proto    table    state  since       info"
    res = parse_birdc_show_proto(line)
    assert len(res) == 6
    assert res["proto"] == "proto"


def test_parse_show_proto_ok():
    line = "b_vrf_hbf_3 BGP      master   up     2020-12-01  Established"
    res = parse_birdc_show_proto(line)
    assert len(res) == 6
    assert res["proto"] == "BGP"
    assert res["info"] == "Established"


def test_parse_show_proto_non_bgp():
    line = "direct0  Direct   master   up     2020-11-27"
    res = parse_birdc_show_proto(line)
    assert len(res) == 5
    assert res["proto"] == "Direct"
    assert "info" not in res


def test_parse_show_proto_too_short():
    line = "direct0  Direct   master"
    assert not parse_birdc_show_proto(line)
