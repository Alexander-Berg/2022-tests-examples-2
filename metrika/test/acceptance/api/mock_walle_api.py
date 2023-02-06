import allure
import flask
import flask.json
import logging

import walle_api.constants

logger = logging.getLogger(__name__)

app = flask.Flask(__name__)


@app.route("/v1/hosts/<id>")
def get(id):
    with allure.step("MockWalleAPI route: '/hosts' {}".format(flask.request)):
        logger.info("request: {}".format(flask.request))
        json_response = flask.json.jsonify(
            {
                "status": walle_api.constants.HostStatus.READY
            }
        )
        allure.attach("response.json", json_response.data)
        return json_response
