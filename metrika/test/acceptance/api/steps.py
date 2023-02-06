import allure
import datetime
import logging
import jinja2
import os
import os.path
import pprint
import yatest.common
from hamcrest import has_property, has_items, has_entries, equal_to
from hamcrest.core import string_description

import metrika.admin.python.cms.lib.client as lib_client
import metrika.admin.python.cms.lib.fsm.states as cms_fsm
import metrika.core.test_framework.utils.wait as wait
import metrika.admin.python.cms.test.acceptance.api.mock_agent_api as mock_agent_api
import metrika.admin.python.cms.test.acceptance.api.mock_cluster_api as mock_cluster_api
import metrika.admin.python.cms.test.acceptance.api.mock_walle_api as mock_walle_api
import metrika.core.test_framework.steps.http as http
import metrika.core.test_framework.utils.attachment as attachment
from metrika.core.test_framework.steps.verification import assume_that, VerificationSteps

logger = logging.getLogger(__name__)


def _render_template(path, env):
    return jinja2.Template(open(path).read()).render(env)


def _get_wd(name):
    wd = yatest.common.test_output_path(name)
    if not os.path.exists(wd):
        os.makedirs(wd)
    return wd


class InputSteps(http.HttpInputSteps):
    def __init__(self, port_manager):
        super(InputSteps, self).__init__(port_manager)
        self.internal_api = lib_client.InternalApi("http://localhost:{}".format(self.port))

        self.judge_queue = "judge_queue_{}".format(datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f"))
        self.judge_lock = "judge_lock_{}".format(datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f"))
        self.marshal_queue = "marshal_queue_{}".format(datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f"))
        self.marshal_lock = "marshal_lock_{}".format(datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f"))

        self.auto_unload = False
        self.auto_approve = False
        self.skip_load = False

    @allure.step("Wall-E Create Task")
    def create_task(self, walle_task):
        allure.attach("Wall-E task", pprint.pformat(walle_task))
        return self.request("/api/v1/walle/v14/tasks", method="POST", json=walle_task)

    @allure.step("Wall-E Get Task {1}")
    def get_task(self, walle_id):
        return self.request("/api/v1/walle/v14/tasks/{}".format(walle_id))

    @allure.step("Wall-E Delete Task {1}")
    def delete_task(self, walle_id):
        return self.request("/api/v1/walle/v14/tasks/{}".format(walle_id), method="DELETE")

    @allure.step("Wait for status: {2}")
    def wait_for_status(self, walle_id, expected_status):
        def predicate():
            task = self.internal_api.get_task(walle_id)
            with allure.step(f"Actual status: {task['internal_status']}"):
                logger.debug(f"Actual status: {task['internal_status']}")
                return task["internal_status"] == expected_status

        wait.wait_for(predicate, poll_period=datetime.timedelta(seconds=2), timeout=datetime.timedelta(seconds=30), initial_sleep=True)

    @allure.step
    def wait_for_audit_records(self, walle_id, matcher):
        allure.attach("matcher", str(matcher))

        def predicate():
            actual_audit = self.internal_api.get_audit(walle_id)
            allure.attach("Audit", "\n".join([pprint.pformat(a) for a in actual_audit]))
            logger.debug("Audit:\n" + "\n".join([str(a) for a in actual_audit]))
            mismatch_description = string_description.StringDescription()
            matched = matcher.matches(actual_audit, mismatch_description)
            allure.attach("Mismatch Description", str(mismatch_description))
            return matched

        wait.wait_for(predicate, poll_period=datetime.timedelta(seconds=1), timeout=datetime.timedelta(seconds=30))


class ClusterOutputSteps(http.HttpOutputSteps):
    def __init__(self, port_manager):
        super(ClusterOutputSteps, self).__init__(port_manager)

    @allure.step("Start ClusterAPI Mock")
    def start(self):
        self.start_uwsgi_app(mock_cluster_api.app)

    @allure.step("Stop ClusterAPI Mock")
    def stop(self):
        self.stop_uwsgi_app()


class AgentOutputSteps(http.HttpOutputSteps):
    def __init__(self, port_manager):
        super(AgentOutputSteps, self).__init__(port_manager)

    @allure.step("Start AgentAPI Mock")
    def start(self):
        self.start_uwsgi_app(mock_agent_api.app)

    @allure.step("Stop AgentAPI Mock")
    def stop(self):
        self.stop_uwsgi_app()


class WalleOutputSteps(http.HttpOutputSteps):
    def __init__(self, port_manager):
        super(WalleOutputSteps, self).__init__(port_manager)

    @allure.step("Start Wall-E API Mock")
    def start(self):
        self.start_uwsgi_app(mock_walle_api.app)

    @allure.step("Stop Wall-E API Mock")
    def stop(self):
        self.stop_uwsgi_app()


class OutputSteps:
    def __init__(self, cluster_output_steps: ClusterOutputSteps, agent_output_steps: AgentOutputSteps, walle_output_steps: WalleOutputSteps):
        self.cluster = cluster_output_steps
        self.agent = agent_output_steps
        self.walle = walle_output_steps


class Assert:
    def __init__(self, verification_steps: VerificationSteps):
        self.verification = verification_steps

    @allure.step
    def audit_is_expected(self, actual_audit, expected_audit_records):
        allure.attach("Actual audit", "\n".join([pprint.pformat(a) for a in actual_audit]))
        allure.attach("Expected audit", "\n".join([pprint.pformat(a) for a in expected_audit_records]))
        self.verification(actual_audit, has_items(*[has_entries(r) for r in expected_audit_records]))


class Frontend:
    def __init__(self, input_steps: InputSteps, output_steps: OutputSteps):
        self.input = input_steps
        self.output = output_steps
        self.execution = None
        self.stdout = None
        self.stderr = None

    @allure.step
    def ping_app(self):
        assume_that("пинг успешен", self.input.request("/ping/app"), has_property("status_code", equal_to(200)))

    @allure.step
    def ping_db_read(self):
        assume_that("пинг успешен", self.input.request("/ping/db_read"), has_property("status_code", equal_to(200)))

    @allure.step
    def ping_db_write(self):
        assume_that("пинг успешен", self.input.request("/ping/db_write"), has_property("status_code", equal_to(200)))

    @allure.step("Frontend manager migrate")
    @attachment.log()
    def init_db(self):
        config_path = os.path.join(_get_wd("init_db"), "config.xml")

        params = {
            "judge_queue": self.input.judge_queue,
            "marshal_queue": self.input.marshal_queue,
            "auto_unload": self.input.auto_unload,
            "auto_approve": self.input.auto_approve
        }
        env_vars = os.environ.copy()
        env_vars["CMS_CONFIG_FILE"] = config_path

        with open(config_path, "w") as f:
            f.write(_render_template(yatest.common.source_path("metrika/admin/python/cms/test/acceptance/api/templates/frontend-config.xml.jinja2"), env=params))

        with open(config_path, 'r') as f:
            allure.attach("config.xml", f.read())

        command = [yatest.common.binary_path('metrika/admin/python/cms/frontend/manage/cms-frontend-manage'), "migrate"]
        stdout = os.path.join(_get_wd("init_db"), "stdout.log")
        stderr = os.path.join(_get_wd("init_db"), "stderr.log")
        yatest.common.execute(command, stdout=stdout, stderr=stderr, timeout=120, env=env_vars)

        with open(stdout, 'r') as f:
            allure.attach("STDOUT", f.read())
        with open(stderr, 'r') as f:
            allure.attach("STDERR", f.read())

    @allure.step("Frontend Start")
    @attachment.log()
    def start(self):
        config_path = os.path.join(_get_wd("frontend"), "config.xml")

        params = {
            "judge_queue": self.input.judge_queue,
            "marshal_queue": self.input.marshal_queue,
            "auto_unload": self.input.auto_unload,
            "auto_approve": self.input.auto_approve,
            "skip_load": self.input.skip_load,
            "cluster_api": self.output.cluster.base_url,
        }
        env_vars = os.environ.copy()
        env_vars["CMS_CONFIG_FILE"] = config_path

        with open(config_path, "w") as f:
            f.write(_render_template(yatest.common.source_path("metrika/admin/python/cms/test/acceptance/api/templates/frontend-config.xml.jinja2"), env=params))

        with open(config_path, 'r') as f:
            allure.attach("config.xml", f.read())

        command = [yatest.common.binary_path('metrika/admin/python/cms/frontend/manage/cms-frontend-manage'), "runserver", "--nothreading", str(self.input.port)]
        self.stdout = os.path.join(_get_wd("frontend"), "stdout.log")
        self.stderr = os.path.join(_get_wd("frontend"), "stderr.log")
        self.execution = yatest.common.execute(command, stdout=self.stdout, stderr=self.stderr, wait=False, env=env_vars)

    @allure.step("Frontend Stop")
    @attachment.log()
    def stop(self):
        if self.execution:
            self.execution.kill()
            with open(self.stdout, 'r') as f:
                allure.attach("STDOUT", f.read())
            with open(self.stderr, 'r') as f:
                allure.attach("STDERR", f.read())


class Judge:
    def __init__(self, port_manager, input_steps: InputSteps, output_steps: OutputSteps):
        self.http = http.HttpInputSteps(port_manager)
        self.input = input_steps
        self.output = output_steps
        self.execution = None
        self.stdout = None
        self.stderr = None

    @property
    def port(self):
        return self.http.port

    @allure.step
    def ping(self):
        assume_that("пинг успешен", self.http.request("/ping"), has_property("status_code", equal_to(200)))

    @allure.step("Judge Start")
    @attachment.log()
    def start(self):
        config_path = os.path.join(_get_wd("judge"), "config.xml")

        params = {
            "port": self.port,
            "frontend": "http://localhost:{}".format(self.input.port),
            "cluster_api": self.output.cluster.base_url,
            "judge_queue": self.input.judge_queue,
            "judge_lock": self.input.judge_lock,
        }
        env_vars = os.environ.copy()
        env_vars["CMS_JUDGE_CONFIG_FILE"] = config_path

        with open(config_path, "w") as f:
            f.write(_render_template(yatest.common.source_path("metrika/admin/python/cms/test/acceptance/api/templates/judge-config.xml.jinja2"), env=params))

        with open(config_path, 'r') as f:
            allure.attach("config.xml", f.read())

        command = [yatest.common.binary_path('metrika/admin/python/cms/judge/bin/cms-judge')]
        self.stdout = os.path.join(_get_wd("judge"), "stdout.log")
        self.stderr = os.path.join(_get_wd("judge"), "stderr.log")
        self.execution = yatest.common.execute(command, stdout=self.stdout, stderr=self.stderr, wait=False, env=env_vars)

    @allure.step("Judge Stop")
    @attachment.log()
    def stop(self):
        if self.execution:
            self.execution.kill()
            with open(self.stdout, 'r') as f:
                allure.attach("STDOUT", f.read())
            with open(self.stderr, 'r') as f:
                allure.attach("STDERR", f.read())


class Marshal:
    def __init__(self, port_manager, input_steps: InputSteps, output_steps: OutputSteps):
        self.http = http.HttpInputSteps(port_manager)
        self.input = input_steps
        self.output = output_steps
        self.execution = None
        self.stdout = None
        self.stderr = None

    @property
    def port(self):
        return self.http.port

    @allure.step
    def ping(self):
        assume_that("пинг успешен", self.http.request("/ping"), has_property("status_code", equal_to(200)))

    @allure.step("Marshal Start")
    @attachment.log()
    def start(self):
        config_path = os.path.join(_get_wd("marshal"), "config.xml")

        params = {
            "port": self.port,
            "frontend": "http://localhost:{}".format(self.input.port),
            "agent_port": self.output.agent.port,
            "walle": self.output.walle.base_url,
            "marshal_queue": self.input.marshal_queue,
            "marshal_lock": self.input.marshal_lock
        }
        env_vars = os.environ.copy()
        env_vars["CMS_MARSHAL_CONFIG_FILE"] = config_path

        with open(config_path, "w") as f:
            f.write(_render_template(yatest.common.source_path("metrika/admin/python/cms/test/acceptance/api/templates/marshal-config.xml.jinja2"), env=params))

        with open(config_path, 'r') as f:
            allure.attach("config.xml", f.read())

        command = [yatest.common.binary_path('metrika/admin/python/cms/marshal/bin/cms-marshal')]
        self.stdout = os.path.join(_get_wd("marshal"), "stdout.log")
        self.stderr = os.path.join(_get_wd("marshal"), "stderr.log")
        self.execution = yatest.common.execute(command, stdout=self.stdout, stderr=self.stderr, wait=False, env=env_vars)

    @allure.step("Marshal Stop")
    @attachment.log()
    def stop(self):
        if self.execution:
            self.execution.kill()
            with open(self.stdout, 'r') as f:
                allure.attach("STDOUT", f.read())
            with open(self.stderr, 'r') as f:
                allure.attach("STDERR", f.read())


class Components:
    def __init__(self, frontend: Frontend, judge: Judge, marshal: Marshal):
        self.frontend = frontend
        self.judge = judge
        self.marshal = marshal


class Steps:
    def __init__(self, input_steps: InputSteps, output_steps: OutputSteps, components_steps: Components, assert_that: Assert):
        self.input = input_steps
        self.output = output_steps
        self.components = components_steps
        self.assert_that = assert_that

        self.walle_task_ids = []

    def setup_auto_full(self):
        self.input.auto_unload = True
        self.input.auto_approve = True
        self.input.skip_load = True
        self.setup()

    def setup_manual(self):
        self.input.auto_unload = False
        self.input.auto_approve = False
        self.input.skip_load = False
        self.setup()

    def setup(self):
        self.components.frontend.init_db()
        self.output.cluster.start()
        self.output.agent.start()
        self.output.walle.start()
        self.components.frontend.start()
        self.components.judge.start()
        self.components.marshal.start()

    def teardown(self):
        self.dump_audit()
        self.components.marshal.stop()
        self.components.judge.stop()
        self.components.frontend.stop()
        self.output.walle.stop()
        self.output.agent.stop()
        self.output.cluster.stop()

    @allure.step
    def dump_audit(self):
        for walle_task_id in self.walle_task_ids:
            audit = self.input.internal_api.get_audit(walle_task_id)
            allure.attach("Audit for {}".format(walle_task_id), "\n".join([pprint.pformat(a) for a in audit]))

    def _get_next_walle_id(self):
        return "acceptance-testing-{}".format(datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f"))

    @allure.step
    def ping_all(self):
        self.components.frontend.ping_app()
        self.components.frontend.ping_db_read()
        self.components.frontend.ping_db_write()
        self.components.judge.ping()
        self.components.marshal.ping()

    @allure.step
    def walle_create_task(self, action="reboot"):
        walle_id = self._get_next_walle_id()
        self.input.create_task(
            {
                "id": walle_id,
                "type": "manual",
                "issuer": "acceptance-test",
                "action": action,
                "hosts": [
                    "acceptance-cluster-host-01",
                ],
                "comment": "awesome-comment",
                "extra": {}
            }
        )
        self.walle_task_ids.append(walle_id)
        return walle_id

    @allure.step
    def walle_create_task_auto(self):
        walle_id = self._get_next_walle_id()
        self.input.create_task(
            {
                "id": walle_id,
                "type": "manual",
                "issuer": "acceptance-test",
                "action": "reboot",
                "hosts": [
                    "127.0.0.1",
                ],
                "comment": "awesome-comment",
                "extra": {}
            }
        )
        self.walle_task_ids.append(walle_id)
        return walle_id

    @allure.step
    def walle_delete_task(self, walle_id):
        self.input.delete_task(walle_id)

    @allure.step
    def operator_accept_walle_task(self, walle_id):
        self.input.internal_api.make_transition(walle_id, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE,
                                                subject="operator", message="manual decision", obj={})

    @allure.step
    def operator_approve_unloading(self, walle_id):
        self.input.internal_api.make_transition(walle_id, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD, cms_fsm.States.UNLOADING,
                                                subject="operator", message="allow unloading", obj={})

    @allure.step
    def operator_approve_ok_walle_task(self, walle_id):
        self.input.internal_api.make_transition(walle_id, cms_fsm.States.WAIT_FOR_APPROVAL_OK, cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE,
                                                subject="operator", message="manual approve", obj={})

    @allure.step
    def operator_load_walle_task(self, walle_id):
        self.input.internal_api.make_transition(walle_id, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, cms_fsm.States.COMPLETED,
                                                subject="operator", message="manual loading", obj={})

    @allure.step
    def operator_reject_walle_task(self, walle_id):
        self.input.internal_api.make_transition(walle_id, cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, cms_fsm.States.REJECT_WAIT_FOR_WALLE_DELETE,
                                                subject="operator", message="manual decision", obj={})

    @allure.step
    def verify_audit(self, walle_id, expected_audit_records):
        self.input.wait_for_audit_records(walle_id, has_items(*[has_entries(r) for r in expected_audit_records]))

        actual_audit = self.input.internal_api.get_audit(walle_id)
        self.assert_that.audit_is_expected(actual_audit, expected_audit_records)
        self.assert_that.verification.verify()
