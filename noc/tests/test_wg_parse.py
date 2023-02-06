import pytest

import noc.traffic.monitoring.wireguard.lib.wg_parse as wg_parse


@pytest.fixture
def wg_show_all_transfer_output():
    return (
        "wg0\tjVznKVdn/+MWu1DLSg/sxgTox7Pb4berAcMJVtxGfGM=\t8253523748\t115308636\n"
        "wg0\tXk3PsxG9R5v60T/Hb1xthS+nQyuqSfE5Y5orrwf58xc=\t0\t0\n"
        "\n"
        )


@pytest.fixture
def wg_show_all_latest_handshakes_output():
    return (
        "wg0\tjVznKVdn/+MWu1DLSg/sxgTox7Pb4berAcMJVtxGfGM=\t1624870612\n"
        "wg0\tXk3PsxG9R5v60T/Hb1xthS+nQyuqSfE5Y5orrwf58xc=\t0\n"
        "\n"
        )


@pytest.fixture
def wg_garbage_output():
    return "I think i'm paranoid\nAnd complicated"


def test_parse_wg_show_all_transfer_output(wg_show_all_transfer_output):
    result = wg_parse.parse_wg_show_all_transfer_output(wg_show_all_transfer_output)

    assert(len(result) == 2)
    assert(result[0].interface == "wg0")
    assert(result[0].public_key == "jVznKVdn/+MWu1DLSg/sxgTox7Pb4berAcMJVtxGfGM=")
    assert(result[0].transfer_rx == 8253523748)
    assert(result[0].transfer_tx == 115308636)

    assert(result[1].interface == "wg0")
    assert(result[1].public_key == "Xk3PsxG9R5v60T/Hb1xthS+nQyuqSfE5Y5orrwf58xc=")
    assert(result[1].transfer_rx == 0)
    assert(result[1].transfer_tx == 0)


def test_parse_wg_show_all_transfer_garbage(wg_garbage_output):
    with pytest.raises(ValueError):
        wg_parse.parse_wg_show_all_transfer_output(wg_garbage_output)


def test_parse_wg_show_all_latest_handshakes_output(wg_show_all_latest_handshakes_output):

    result = wg_parse.parse_wg_show_all_latest_handshakes_output(wg_show_all_latest_handshakes_output)

    assert(len(result) == 2)
    assert(result[0].public_key == "jVznKVdn/+MWu1DLSg/sxgTox7Pb4berAcMJVtxGfGM=")
    assert(result[0].latest_handshake == 1624870612)
    assert(result[1].public_key == "Xk3PsxG9R5v60T/Hb1xthS+nQyuqSfE5Y5orrwf58xc=")
    assert(result[1].latest_handshake == 0)


def test_parse_wg_show_all_latest_handshakes_garbage(wg_garbage_output):
    with pytest.raises(ValueError):
        wg_parse.parse_wg_show_all_latest_handshakes_output(wg_garbage_output)
