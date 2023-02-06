import allure
import logging
import json
import functools

from hamcrest import has_property, equal_to

import metrika.admin.python.cms.agent.lib.steps.provider as provider
import metrika.admin.python.cms.agent.lib.steps.manager as manager
import metrika.admin.python.cms.agent.lib.steps.step as step

import metrika.admin.python.cms.test_framework.utils as utils
import metrika.core.test_framework.utils.wait as wait
from metrika.core.test_framework.steps.verification import assume_that

logger = logging.getLogger(__name__)


class Steps:
    def __init__(self, monkeypatch, agent, client, httpserver, verification_steps, assert_that):
        self.monkeypatch = monkeypatch
        self.agent = agent
        self.client = client
        self.httpserver = httpserver
        self.verification = verification_steps
        self.assert_that = assert_that

    def _assume_status_code(self, response, expected_code, message="запрос завершился успешно"):
        utils.attach_flask_response(response)
        assume_that(message, response, has_property("status_code", equal_to(expected_code)))
        return response

    @allure.step
    def get_host_status(self):
        response = self.client.get("/status")
        return self._assume_status_code(response, 200).get_json()

    @allure.step
    def get_unloading_status(self):
        response = self.client.get("/unload")
        return self._assume_status_code(response, 200).get_json()

    @allure.step
    def start_unloading(self):
        response = self.client.post("/unload")
        self._assume_status_code(response, 204)

    @allure.step
    def cancel_unloading(self):
        response = self.client.delete("/unload")
        self._assume_status_code(response, 204)

    def wait_for_unloading_status(self, *statuses):
        with allure.step(f"Wait for unloading status {', '.join([str(s) for s in statuses])}"):
            wait.wait_for(lambda: self.get_unloading_status()["state"] in statuses)

    @allure.step
    def get_load_initiate_status(self):
        response = self.client.get("/load/initiate")
        return self._assume_status_code(response, 200).get_json()

    @allure.step
    def start_load_initiate(self):
        response = self.client.post("/load/initiate")
        self._assume_status_code(response, 204)

    @allure.step
    def cancel_load_initiate(self):
        response = self.client.delete("/load/initiate")
        self._assume_status_code(response, 204)

    def wait_for_load_initiate_status(self, *statuses):
        with allure.step(f"Waif for load initiate status {', '.join([str(s) for s in statuses])}"):
            wait.wait_for(lambda: self.get_load_initiate_status()["state"] in statuses)

    @allure.step
    def get_loading_status(self):
        response = self.client.get("/load/poll")
        return self._assume_status_code(response, 200).get_json()

    def wait_for_loading_status(self, *statuses):
        with allure.step(f"Waif for loading status {', '.join([str(s) for s in statuses])}"):
            wait.wait_for(lambda: self.get_loading_status()["state"] in statuses)

    @allure.step
    def get_load_finalize_status(self):
        response = self.client.get("/load/finalize")
        return self._assume_status_code(response, 200).get_json()

    @allure.step
    def start_load_finalize(self):
        response = self.client.post("/load/finalize")
        self._assume_status_code(response, 204)

    @allure.step
    def cancel_load_finalize(self):
        response = self.client.delete("/load/finalize")
        self._assume_status_code(response, 204)

    def wait_for_load_finalize_status(self, *statuses):
        with allure.step(f"Waif for load finalize status {', '.join([str(s) for s in statuses])}"):
            wait.wait_for(lambda: self.get_load_finalize_status()["state"] in statuses)

    @allure.step
    def setup_set_cluster(self, name):
        self.monkeypatch.setitem(self.agent.config, "cluster", name)

    @allure.step
    def setup_long_running_step(self, step_duration, step_timeout):
        def get(*args, **kwargs):
            return manager.StepsManager(
                self.agent,
                step.check_running_operation(self.agent),
                step.check_shell(self.agent, "step_1", "Sleep for {} seconds".format(step_duration), ["sleep", "{}".format(step_duration)])
            )

        self.monkeypatch.setattr(provider.StepsManagerProvider, "get", get)
        self.monkeypatch.setitem(self.agent.config, "steps", {"timeout": step_timeout})

    @allure.step
    def setup_long_running_operation_step(self, step_duration, step_timeout):
        def get(*args, **kwargs):
            return manager.StepsManager(
                self.agent,
                step.check_shell(self.agent, "step_1", "Sleep for {} seconds".format(step_duration), ["sleep", "{}".format(step_duration)])
            )

        self.monkeypatch.setattr(provider.StepsManagerProvider, "get", get)
        self.monkeypatch.setitem(self.agent.config, "steps", {"step_1": {"timeout": step_timeout}})

    @allure.step
    def setup_http_server(self, content, code, headers):
        self.httpserver.serve_content(
            content=content, code=code,
            headers=headers
        )

        return content

    @allure.step
    def setup_http_server_reply_ok(self):
        return self.setup_http_server("OK.", 200, {'content-type': 'text/plain'})

    @allure.step
    def setup_http_server_reply_service_unavailable(self):
        return self.setup_http_server("OK.", 500, {'content-type': 'text/plain'})

    @allure.step
    def setup_http_server_reply_pretend_clickhouse(self):
        content = {
            "meta": [
                {
                    "name": "database",
                    "type": "String"
                },
                {
                    "name": "name",
                    "type": "String"
                }
            ],
            "data": [
                {
                    "database": "aleksmia",
                    "name": "capture_rate"
                }
            ],
            "rows": 1,
            "rows_before_limit_at_least": 1,
            "statistics": {
                "elapsed": 0.000332156,
                "rows_read": 1,
                "bytes_read": 38
            }
        }

        self.setup_http_server(json.dumps(content), 200, {'content-type': 'application/json'})

        return content

    @allure.step
    def setup_http_step(self, method="GET", body=None, predicate=functools.partial(step.predicate_statuscode, value=200)):
        def get(*args, **kwargs):
            return manager.StepsManager(
                self.agent,
                step.check_running_operation(self.agent),
                step.check_http(self.agent, "step_1", "HTTP {} to {}".format(method, self.httpserver.url), self.httpserver.url, method=method, body=body, predicate=predicate)
            )

        self.monkeypatch.setattr(provider.StepsManagerProvider, "get", get)

    @allure.step
    def setup_http_step_expect_ok(self):
        self.setup_http_step()

    @allure.step
    def setup_http_step_expect_text(self, text):
        self.setup_http_step(predicate=functools.partial(step.predicate_body_text, value=text))

    @allure.step
    def setup_http_step_expect_json(self, object):
        self.setup_http_step(method="POST", body="select database, name from system.tables limit 1 format JSON", predicate=functools.partial(step.predicate_body_json, value=object))
