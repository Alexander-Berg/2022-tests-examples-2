import allure
import flask
import flask.json
import werkzeug.urls
import logging

logger = logging.getLogger(__name__)

app = flask.Flask(__name__)


@app.route("/get")
def get():
    with allure.step("MockClusterAPI route: '/get' {}".format(flask.request)):
        logger.info("request: {}".format(flask.request))
        fqdn = werkzeug.urls.url_unquote_plus(flask.request.args.get("fqdn", None))
        if fqdn in ["127.0.0.1", "127.0.0.2", "127.0.0.3"]:
            shard_id = "acceptance-cluster-acceptance-environment-auto"
            environment = "acceptance-environment-auto"
        else:
            shard_id = "acceptance-cluster-acceptance-environment"
            environment = "acceptance-environment"

        json_response = flask.json.jsonify(
            {
                "data": [
                    {
                        "shard_id": shard_id,
                        "environment": environment,
                        "layer": None,
                        "type": "acceptance-cluster"
                    }
                ],
                "_meta": {"total_time": 0, "parse_time": 0, "execute_query_time": 0, "data_length": 1},
                "result": True
            }
        )
        allure.attach("response.json", json_response.data)
        return json_response


@app.route("/list/fqdn")
def list():
    with allure.step("MockClusterAPI route: '/list/fqdn' {}".format(flask.request)):
        logger.info("request: {}".format(flask.request))
        fqdn = werkzeug.urls.url_unquote_plus(flask.request.args.get("fqdn", None))
        if fqdn == "!127.0.0.1":
            json_response = flask.json.jsonify(
                {
                    "data": ["127.0.0.2", "127.0.0.3"],
                    "_meta": {"total_time": 0, "parse_time": 0, "execute_query_time": 0, "data_length": 2},
                    "result": True
                }
            )
        elif fqdn == "!acceptance-cluster-host-01":
            json_response = flask.json.jsonify(
                {
                    "data": ["acceptance-cluster-host-02", "acceptance-cluster-host-03"],
                    "_meta": {"total_time": 0, "parse_time": 0, "execute_query_time": 0, "data_length": 2},
                    "result": True
                }
            )
        else:
            json_response = flask.json.jsonify({})
        allure.attach("response.json", json_response.data)
        return json_response
