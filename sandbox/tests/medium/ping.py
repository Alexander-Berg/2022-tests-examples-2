import six
import requests


def test_ping(proxy):
    assert requests.get("http://{}/http_check".format(proxy)).status_code == six.moves.http_client.OK
