import pytest
import requests

import sandbox.common.types.misc as ctm


@pytest.mark.usefixtures("serviceapi")
def test_response_headers(host, serviceapi_port):
    api = "http://{}:{}/api/v1.0/".format(host, serviceapi_port)
    r = requests.get(api + "/user/current/groups")

    assert ctm.HTTPHeader.API_QUOTA_CONSUMPTION not in r.headers
    rid = r.headers[ctm.HTTPHeader.REQUEST_ID]
    assert rid.startswith("_")
