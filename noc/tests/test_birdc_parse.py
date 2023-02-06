import pytest

import noc.traffic.monitoring.bird.lib.birdc_parse as birdc_parse


@pytest.fixture
def birdc_show_protocols_iso_time_output():
    return (
        "BIRD 2.0.7 ready.\n"
        "Name       Proto      Table      State  Since         Info\n"
        "device1    Device     ---        up     2021-08-23 14:44:47+0300  \n"
        "p_kernel4  Kernel     kernel4    up     2021-08-23 14:44:47+0300  \n"
        "p_kernel6  Kernel     kernel6    up     2021-08-23 14:44:47+0300  \n"
        "dummy255   Direct     ---        up     2021-08-23 14:44:47+0300  \n"
        "lbix4_to_kernel4 Pipe       ---        up     2021-08-23 14:44:47+0300  lbix4 <=> kernel4\n"
        "lbix6_to_kernel6 Pipe       ---        up     2021-08-23 14:44:47+0300  lbix6 <=> kernel6\n"
        "core4_1    BGP        ---        up     2021-08-23 14:44:51+0300  Established   \n"
        "core4_2    BGP        ---        up     2021-08-23 14:44:52+0300  Established   \n"
        "core6_1    BGP        ---        up     2021-08-23 14:44:53+0300  Established   \n"
        "core6_2    BGP        ---        up     2021-08-23 14:44:52+0300  Established   \n"
        "b_bfd      BFD        ---        up     2021-08-23 14:44:47+0300  \n"
        "p_kernel_wg Kernel     kernel_wg4 up     2021-08-23 14:48:25+0300  \n"
        "lbix4_to_kernel_wg4 Pipe       ---        up     2021-08-23 14:48:25+0300  lbix4 <=> kernel_wg4\n"
        "cdn_static_routes Static     cdn6       up     2021-08-23 14:48:25+0300  \n"
        "cdn6_to_lbix6 Pipe       ---        up     2021-08-23 14:48:25+0300  cdn6 <=> lbix6\n"
        "cdn6_to_kernel6 Pipe       ---        up     2021-08-23 14:48:25+0300  cdn6 <=> kernel6\n"
        "to_cdn_cdn-srv69e-dummy.cdn.yandex.net BGP        ---        start  2021-08-23 14:48:25+0300  Connect       \n"
        "to_cdn_cdn-srv69e.cdn.yandex.net BGP        ---        up     2021-08-23 14:49:03+0300  Established   \n"
        "to_cdn_cdn-srv70e.cdn.yandex.net BGP        ---        up     2021-08-23 14:49:03+0300  Established  \n"
    )


@pytest.fixture
def birdc_show_protocols_default_time_output():
    return (
        "BIRD 2.0.7 ready.\n"
        "Name       Proto      Table      State  Since         Info\n"
        "device1    Device     ---        up     14:44:47.496  \n"
    )


def test_birdc_parse_show_protocols(birdc_show_protocols_iso_time_output):
    result = birdc_parse.parse_birdc_show_protocols_output(birdc_show_protocols_iso_time_output)

    assert(len(result) == 19)
    assert(result[0].name == "device1")
    assert(result[0].proto == "device")
    assert(result[0].state == "up")
    assert(result[0].since == 1629719087)

    assert(result[3].name == "dummy255")
    assert(result[3].proto == "direct")

    assert(result[10].name == "b_bfd")
    assert(result[10].proto == "bfd")

    assert(result[11].name == "p_kernel_wg")
    assert(result[11].proto == "kernel")

    assert(result[13].name == "cdn_static_routes")
    assert(result[13].proto == "static")

    assert(result[15].name == "cdn6_to_kernel6")
    assert(result[15].proto == "pipe")

    assert(result[16].name == "to_cdn_cdn-srv69e-dummy.cdn.yandex.net")
    assert(result[16].proto == "bgp")
    assert(result[16].state == "start")


def test_birdc_parse_show_protocols_default_time_output(birdc_show_protocols_default_time_output):
    with pytest.raises(ValueError):
        birdc_parse.parse_birdc_show_protocols_output(birdc_show_protocols_default_time_output)
