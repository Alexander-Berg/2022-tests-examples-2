import allure
import flask

from functools import wraps

import metrika.admin.python.cms.lib.flask.response as response
import metrika.admin.python.cms.lib.agent.steps.state as state
import metrika.admin.python.cms.test_framework.utils as utils


app = flask.Flask(__name__)


def enter_step_attach_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with allure.step("Mock Agent API {}".format(flask.request)):
            resp = func(*args, **kwargs)
            utils.attach_flask_response(resp)
            return resp
    return wrapper


@app.route("/ping", methods=['GET'])
@enter_step_attach_response
def ping():
    return flask.Response("OK", status=200)


@app.route("/status", methods=['GET'])
@enter_step_attach_response
def status():
    return response.to_json({"state": state.State.SUCCESS})


@app.route("/unload", methods=['GET', 'POST', 'DELETE'])
@enter_step_attach_response
def unload():
    if flask.request.method == 'GET':
        return response.to_json({"state": state.State.SUCCESS})
    elif flask.request.method == 'POST':
        return flask.make_response("", 204)
    elif flask.request.method == 'DELETE':
        return flask.make_response("", 204)
    else:
        return flask.make_response("", 405)


@app.route("/load/initiate", methods=['GET', 'POST', 'DELETE'])
@enter_step_attach_response
def initiate_loading():
    if flask.request.method == 'GET':
        return response.to_json({"state": state.State.SUCCESS})
    elif flask.request.method == 'POST':
        return flask.make_response("", 204)
    elif flask.request.method == 'DELETE':
        return flask.make_response("", 204)
    else:
        return flask.make_response("", 405)


@app.route("/load/finalize", methods=['GET', 'POST', 'DELETE'])
@enter_step_attach_response
def finalize_loading():
    if flask.request.method == 'GET':
        return response.to_json({"state": state.State.SUCCESS})
    elif flask.request.method == 'POST':
        return flask.make_response("", 204)
    elif flask.request.method == 'DELETE':
        return flask.make_response("", 204)
    else:
        return flask.make_response("", 405)


@app.route("/load/poll", methods=['GET'])
@enter_step_attach_response
def poll_loading():
    return response.to_json({"state": state.State.SUCCESS})
