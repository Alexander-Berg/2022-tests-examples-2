import allure
import logging
import pprint

import metrika.admin.python.cms.lib.client as client

logger = logging.getLogger(__name__)


class MockInternalApi:
    def __init__(self):
        self._task_mapping = {}
        self._audit_mapping = {}
        self._recorded_transitions = []
        self._recorded_audits = []
        self._not_loaded_tasks_response = []

    @property
    def task_mapping(self):
        return self._task_mapping

    @task_mapping.setter
    def task_mapping(self, value):
        allure.attach("MockInternalApi set task_mapping", pprint.pformat(value))
        self._task_mapping = value

    @property
    def audit_mapping(self):
        return self._audit_mapping

    @audit_mapping.setter
    def audit_mapping(self, value):
        allure.attach("MockInternalApi set audit_mapping", pprint.pformat(value))
        self._audit_mapping = value

    @property
    def recorded_transitions(self):
        allure.attach("MockInternalApi recorded_transitions", "\n".join([pprint.pformat(t) for t in self._recorded_transitions]))
        return self._recorded_transitions

    @property
    def recorded_audits(self):
        allure.attach("MockInternalApi recorded_audits", "\n".join([pprint.pformat(a) for a in self._recorded_audits]))
        return self._recorded_audits

    @property
    def not_loaded_tasks(self):
        allure.attach("MockInternalApi not_loaded_tasks", pprint.pformat(self._not_loaded_tasks_response))
        return self._not_loaded_tasks_response

    @not_loaded_tasks.setter
    def not_loaded_tasks(self, value):
        allure.attach("MockInternalApi set not_loaded_tasks", pprint.pformat(value))
        self._not_loaded_tasks_response = value

    @allure.step("MockInternalApi Constructor call")
    def __call__(self, url):
        return self

    @allure.step("MockInternalApi.get_task walle_id: {1}")
    def get_task(self, walle_id):
        raw_data = self.task_mapping.get(walle_id, None)
        logger.info("get_task {}: {}".format(walle_id, raw_data))
        allure.attach(str(walle_id), pprint.pformat(raw_data))
        return client.TaskSchema().load(raw_data).data if raw_data is not None else None

    def make_transition(self, walle_id, source_state, target_state, subject, message, obj):
        with allure.step(f"MockInternalApi.make_transition {source_state} -> {target_state}"):
            record = {
                "walle_id": walle_id,
                "source_state": source_state,
                "target_state": target_state,
                "subject": subject,
                "message": message,
                "obj": obj
            }
            logger.info("make_transition: {}".format(record))
            if walle_id in self.task_mapping:
                walle_task = self.task_mapping.get(walle_id, {})
                if walle_task["internal_status"] != source_state:
                    self._record_audit(walle_id, source_state=source_state, target_state=target_state,
                                       subject=subject, message=message, success=False,
                                       reason="source_state != internal_status: {} != {}".format(source_state, walle_task["internal_status"]), obj=obj)
                    raise client.TransitionError()
                else:
                    walle_task["internal_status"] = target_state
                    self._record_transition(record)
                    self._record_audit(walle_id, source_state=source_state, target_state=target_state, subject=subject, message=message, obj=obj)
            else:
                self._record_transition(record)
                self._record_audit(walle_id, source_state=source_state, target_state=target_state, subject=subject, message=message, obj=obj)

    def _record_transition(self, record):
        allure.attach("Transition record", pprint.pformat(record))
        self._recorded_transitions.append(record)

    @allure.step("MockInternalApi.add_audit")
    def add_audit(self, walle_id, **kwargs):
        """
        :param walle_id:
        :param kwargs: subject, message, success=True, reason="operation succeeded", obj=None
        :return:
        """
        self._record_audit(walle_id, **kwargs)

    def _record_audit(self, walle_id, **kwargs):
        record = {"walle_id": walle_id}
        record.update(kwargs)
        allure.attach("Audit record", pprint.pformat(record))
        self._recorded_audits.append(record)

    @allure.step("MockInternalApi.get_audit walle_id: {1}")
    def get_audit(self, walle_id):
        raw_data = self.audit_mapping.get(walle_id, None)
        logger.info("get_audit {}: {}".format(walle_id, raw_data))
        allure.attach(str(walle_id), pprint.pformat(raw_data))
        return client.AuditSchema(many=True).load(raw_data).data if raw_data is not None else None

    @allure.step("MockInternalApi.heartbeat identity: {1}")
    def heartbeat(self, identity):
        logger.info("heartbeat: {}".format(identity))

    @allure.step("MockInternalApi.get_not_loaded_tasks")
    def get_not_loaded_tasks(self):
        logger.info("get_not_loaded_tasks {}".format(self.not_loaded_tasks))
        allure.attach("get_not_loaded_tasks", pprint.pformat(self.not_loaded_tasks))
        return self.not_loaded_tasks
