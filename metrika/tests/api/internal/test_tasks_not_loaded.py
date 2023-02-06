import pytest
import django.test
import logging
import pprint
import datetime

import metrika.admin.python.cms.lib.fsm.states as fsm_states
import metrika.admin.python.cms.frontend.cms.models as cms_models

pytestmark = pytest.mark.django_db(transaction=True)

logger = logging.getLogger(__name__)


class TestGet(django.test.TestCase):
    def test_get(self):
        # предусловия
        for state in fsm_states.States.all:
            logger.info(f"Createing task in internal_status={state}")
            cms_models.Task.objects_for_frontend.create(
                internal_status=state,
                walle_hosts=["{}.localdomain".format(state)],
                walle_id="walle-id-{}".format(datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f"))
            )

        # действия
        response = self.client.get("/api/v1/internal/tasks/not_loaded")

        # проверки
        self.assertEqual(response.status_code, 200)
        task_list = response.json()
        logger.info("Task list: {}".format(pprint.pformat(task_list)))
        self.assertEqual(len(task_list), len(fsm_states.States.not_loaded))
