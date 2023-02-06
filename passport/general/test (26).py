import os
import os.path

import requests

KOLMOGOR_PORT_FILE = "kolmogor.port"


def _get_kolmogor_params():
    port = int(open(KOLMOGOR_PORT_FILE).read())
    return port


def test_kolmogor():
    assert os.path.isfile(KOLMOGOR_PORT_FILE)

    port = _get_kolmogor_params()

    r = requests.get("http://localhost:%d/ping" % port)
    assert r.text == 'OK\n'
    assert r.status_code == 200
