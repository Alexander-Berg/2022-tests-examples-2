import pytest

from metrika.admin.python.mtapi.lib.test_utils import dump_response
from flask import request


def test_ping(client):
    response = client.get("/cluster/ping")

    dump_response(response)

    assert response.status_code == 200


@pytest.mark.parametrize('params', [
    {'root_group': 'mtkek'},
    {'root_group': ['mtkek']},
])
def test_params(client, params):
    response = client.get("/cluster/list/fqdn", data=params)
    assert response.status_code < 500
    assert request.args == {'root_group': 'mtkek'}
