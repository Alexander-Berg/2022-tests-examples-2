import requests
from dmp_suite.http.oauth_utils import Auth


def test_auth():
    req = requests.PreparedRequest()
    req.headers = {}
    auth = Auth('test_token')
    auth(req)
    assert req.headers == {'Authorization': 'Bearer test_token'}
