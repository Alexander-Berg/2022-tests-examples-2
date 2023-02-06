import pytest
import requests


@pytest.mark.usefixtures("serviceapi")
def test_run_serviceapi_binary(host, serviceapi_port):

    api = "http://{}:{}/api/v1.0".format(host, serviceapi_port)
    r = requests.get(api + "/user/current/groups")
    r.raise_for_status()

    assert len(r.json()) == 1
