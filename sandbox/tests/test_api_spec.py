import httplib

import flask
import pytest

from sandbox.serviceapi import plugins


@pytest.fixture
def app():
    return flask.Flask(__name__, static_folder=None)


def test_swagger(app):
    plugins.static.init_plugin(app)
    client = app.test_client()

    r1 = client.get("/media/swagger-ui")
    assert r1.status_code == httplib.MOVED_PERMANENTLY

    r2 = client.get(r1.headers["LOCATION"])
    assert r2.status_code == httplib.OK


def test_redoc(app):
    plugins.openapi.init_plugin(app)
    client = app.test_client()

    r1 = client.get("/api/redoc")
    assert r1.status_code == httplib.OK
