import allure
import json
import logging
import copy
import contextlib
import pprint

import metrika.pylib.structures.dotdict as dotdict

from hamcrest import has_property, equal_to, has_length, has_entry, has_entries, empty, not_, has_item, greater_than_or_equal_to, less_than, all_of
from metrika.core.test_framework.steps.verification import assume_that

logger = logging.getLogger(__name__)


class Steps:
    def __init__(self, client, assert_that, config):
        self.client = client
        self.assert_that = assert_that
        self.config = config

    def verify(self):
        self.assert_that.verification.verify()

    def make_task(self, internal_status, action="reboot"):
        # pytestmark = pytest.mark.django_db - работает только для тестов, но не для фикстур
        import metrika.admin.python.cms.frontend.cms.models as cms_models
        with allure.step("Создать задачу Wall-E в состоянии {1} для действия {2}"):
            id = cms_models.Task.objects_for_frontend.create(
                walle_id="internal-0000",
                walle_hosts=["localhost"],
                internal_status=internal_status,
                walle_action=action
            ).walle_id
            with allure.step(f"Задача создана {id}"):
                return id

    @allure.step("Получить задачу Wall-E {1}")
    def get_task(self, id):
        import metrika.admin.python.cms.frontend.cms.models as cms_models
        return cms_models.Task.objects_for_frontend.get(walle_id=id)

    @allure.step("Перевести задачу {1} {2} -> {3}")
    def make_transition(self, id, source_state, target_state):
        """
        Действие - перевод заданной walle-таски из одного состояния в другое посредством внутреннего API и сбор информации.
        :param client:
        :param id:
        :param source_state:
        :param target_state:
        :return: словарь из ответа на попытку совершить перевод, ответа на запрос таски через внутреннее API, аудит
        """
        response = self.client.get('/api/v1/internal/task/{id}'.format(id=id))
        logger.debug("Task Before: {}".format(response.content))

        request = json.dumps({"source_state": source_state, "target_state": target_state, "subject": "test", "obj": "{}", "message": "test"})
        logger.debug("Transition Request: {}".format(request))
        transition_response = self.client.put(
            '/api/v1/internal/task/{id}/transition'.format(id=id),
            request,
            content_type='application/json')
        logger.debug("Transition Response: {}".format(transition_response.content))

        task_response = self.client.get('/api/v1/internal/task/{id}'.format(id=id))
        logger.debug("Task After: {}".format(task_response.content))

        task_walle_response = self.client.get('/api/v1/walle/v14/tasks/{id}'.format(id=id))
        logger.debug("Wall-E Task After: {}".format(task_walle_response.content))

        audit_response = self.client.get('/api/v1/internal/task/{id}/audit'.format(id=id))
        logger.debug("Audit: {}".format(audit_response.content))

        points = {
            'transition_response': transition_response,
            'task_response': task_response,
            'task_walle_response': task_walle_response,
            'audit_response': audit_response
        }

        for k, v in points.items():
            allure.attach(k, v.content)

        return points

    @allure.step("Wall-E удаляет задачу {1}")
    def walle_delete(self, id):
        response = self.client.delete('/api/v1/walle/v14/tasks/{id}'.format(id=id))
        allure.attach("Response", response.content)
        return response

    @allure.step("Wall-E получает список задач")
    def walle_poll(self):
        response = self.client.get('/api/v1/walle/v14/tasks')
        allure.attach("Response", response.content)
        return response

    @allure.step("Wall-E получает задачу {1}")
    def walle_get(self, id):
        response = self.client.get('/api/v1/walle/v14/tasks/{id}'.format(id=id))
        allure.attach("Response", response.content)
        return response

    @allure.step("Добавить запись аудита к задаче {1}")
    def add_audit(self, id, subject, success, message, reason, obj):
        request = json.dumps({"reason": reason, "success": success, "subject": subject, "obj": obj, "message": message})
        allure.attach("Audit Request", request)
        logger.debug("Audit Request: {}".format(request))

        audit_response = self.client.post(
            '/api/v1/internal/task/{id}/audit'.format(id=id),
            request,
            content_type='application/json')
        allure.attach("Audit Response", audit_response.content)
        logger.debug("Audit Response: {}".format(audit_response.content))

        return audit_response

    @allure.step("Получить аудит задачи {1}")
    def get_audit(self, id):
        audit_response = self.client.get(
            '/api/v1/internal/task/{id}/audit'.format(id=id),
            content_type='application/json')

        logger.debug("Audit Response: {}".format(audit_response.content))

        allure.attach("Audit Response", audit_response.content)

        return audit_response

    @allure.step("Проверяем, что Wall-E-таск '{1}' существует")
    def assert_that_walle_task_exists(self, id):
        poll_response = self.walle_poll()
        self.assert_that.contains_task(poll_response.json()["result"], id)
        self.assert_that.check_response_code(self.walle_get(id), 200)

    @allure.step("Проверяем, что Wall-E-таск '{1}' не существует")
    def assert_that_walle_task_does_not_exist(self, id):
        poll_response = self.walle_poll()
        self.assert_that.not_contains_task(poll_response.json()["result"], id)
        self.assert_that.check_response_code(self.walle_get(id), 404)


class Config:
    def __init__(self):
        self.original = None

    @contextlib.contextmanager
    @allure.step("Изменить конфиг")
    def override(self, new_config_obj):
        allure.attach("Изменения конфига", pprint.pformat(new_config_obj))
        from django.conf import settings
        self.original = settings.CONFIG
        settings.CONFIG = dotdict.DotDict.from_dict(copy.deepcopy(self.original))
        settings.CONFIG.update(new_config_obj)
        allure.attach("Результирующий конфиг", pprint.pformat(settings.CONFIG))
        yield settings.CONFIG
        settings.CONFIG = self.original


class Assert:
    def __init__(self, verification_steps):
        self.verification = verification_steps

    def contains_task(self, tasks, id):
        self.verification.assert_that(f"список тасок содержит таску {id}", tasks, has_item(has_entry("id", id)))

    def not_contains_task(self, tasks, id):
        self.verification.assert_that(f"список тасок не содержит таску {id}", tasks, not_(has_item(has_entry("id", id))))

    def check_response_code(self, response, expected_code):
        self.verification.assert_that(f"код ответа {expected_code}", response, has_property("status_code", equal_to(expected_code)))

    def success_response(self, response):
        self.verification.assert_that("код ответа положительный", response, has_property("status_code", all_of(greater_than_or_equal_to(200), less_than(400))))

    def failed_response(self, response):
        self.verification.assert_that("код ответа негативный", response, has_property("status_code", greater_than_or_equal_to(400)))

    def success_auto_transition(self, transition_response, task_response, task_walle_response, audit_response, target_state, expected_audit, is_walle_deleted=False):
        self.check_response_code(transition_response, 204)
        self.check_response_code(task_response, 200)
        self.check_response_code(task_walle_response, 404 if is_walle_deleted else 200)
        self.check_response_code(audit_response, 200)

        self.verification.assert_that(f"состояние задачи - {target_state}", task_response.json(), has_entry("internal_status", target_state))

        audit_data = audit_response.json()
        assume_that("записи аудита присутствуют", audit_data, not_(empty()))
        for source, target in expected_audit:
            self.verification.assert_that(f"запись аудита перехода {source} -> {target} присутствуе", audit_data, has_item(has_entries(success=True, source_state=source, target_state=target)))

    def success(self, transition_response, task_response, task_walle_response, audit_response, source_state, target_state, is_walle_deleted=False):
        """
        Проверка того, что действие было успешным
        :return:
        """
        self.check_response_code(transition_response, 204)
        self.check_response_code(task_response, 200)
        self.check_response_code(task_walle_response, 404 if is_walle_deleted else 200)
        self.check_response_code(audit_response, 200)

        self.verification.assert_that(f"состояние задачи - {target_state}", task_response.json(), has_entry("internal_status", target_state))

        audit_data = audit_response.json()
        assume_that("записи аудита присутствуют", audit_data, not_(empty()))
        self.verification.assert_that("аудит соответствует ожидаемому", audit_data, has_item(has_entries(success=True, source_state=source_state, target_state=target_state)))

    def fail_transition(self, transition_response, task_response, task_walle_response, audit_response, source_state, target_state, is_walle_deleted):
        """
        Проверка того, что переход, которого нет в FSM не будет совершён
        """
        self.check_response_code(transition_response, 422)
        self.check_response_code(task_response, 200)
        self.check_response_code(task_walle_response, 404 if is_walle_deleted else 200)
        self.check_response_code(audit_response, 200)

        self.verification.assert_that("состояние задачи не изменилось", task_response.json(), has_entry("internal_status", source_state))

        audit_data = audit_response.json()
        assume_that("есть ровно одна запись аудита", audit_data, has_length(equal_to(1)))
        self.verification.assert_that("аудит соответствует ожидаемому", audit_data[0], has_entries(success=False, source_state=source_state, target_state=target_state))

    def fail_unexpected_transition(self, transition_response, task_response, task_walle_response, audit_response, initial_state, source_state, target_state, is_walle_deleted):
        """
        Проверка того, что переход, из состояния, которое не соответствует актуальному не может быть совершён
        """
        self.check_response_code(transition_response, 409)
        self.check_response_code(task_response, 200)
        self.check_response_code(task_walle_response, 404 if is_walle_deleted else 200)
        self.check_response_code(audit_response, 200)

        self.verification.assert_that("состояние задачи не изменилось", task_response.json(), has_entry("internal_status", initial_state))

        audit_data = audit_response.json()
        assume_that("есть ровно одна запись аудита", audit_data, has_length(equal_to(1)))
        self.verification.assert_that("аудит соответствует ожидаемому", audit_data[0], has_entries(success=False, source_state=source_state, target_state=target_state))

    def fail_invalid_choice(self, transition_response, task_response, task_walle_response, audit_response, initial_state, is_walle_deleted):
        """
        Проверка обработки состояния, которое удалено из FSM
        """
        self.check_response_code(transition_response, 400)
        self.check_response_code(task_response, 200)
        self.check_response_code(task_walle_response, 404 if is_walle_deleted else 200)
        self.check_response_code(audit_response, 200)

        self.verification.assert_that("состояние задачи не изменилось", task_response.json(), has_entry("internal_status", initial_state))
        self.verification.assert_that("записей аудита нет", audit_response.json(), empty())

    def positive_audit(self, audit_response):
        self.check_response_code(audit_response, 204)

    def negative_audit(self, audit_response):
        self.check_response_code(audit_response, 400)

    def has_no_audit(self, audit_response):
        self.check_response_code(audit_response, 200)
        self.verification.assert_that("записи аудита отсутствуют", audit_response.json(), empty())

    def has_audit(self, audit_response):
        self.check_response_code(audit_response, 200)
        self.verification.assert_that("есть ровно одна запись аудита", audit_response.json(), has_length(equal_to(1)))

    def audit_contains(self, audit_response, expected_audit):
        self.check_response_code(audit_response, 200)
        self.verification.assert_that("аудит содержит ожидаемую запись", audit_response.json(), has_item(has_entries(**expected_audit)))
