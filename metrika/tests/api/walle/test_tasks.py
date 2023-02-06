import json
import logging
import pytest

import django.test

import metrika.admin.python.cms.frontend.cms.models as cms_models
import metrika.admin.python.cms.frontend.tests.helper as helper
import metrika.admin.python.cms.frontend.tests.api.walle.schemas.schemas as api_schemas

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("noop_queue")
class TestCreate(helper.CmsBaseTestCase, django.test.TestCase):
    valid_post_data = {
        "id": "hello",
        "type": "manual",
        "issuer": "robert",
        "action": "reboot",
        "hosts": [
            "mtdev05e.yandex.ru",
        ],
        "comment": "awesome-comment",
        "extra": {},
    }

    def test_normal(self):
        post_data = json.dumps(self.valid_post_data)
        response = self.client.post(
            '/api/v1/walle/v14/tasks',
            post_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(
            api_schemas.PostSchema(data).validate(),
        )

        # check accessible through api
        response = self.client.get(
            '/api/v1/walle/v14/tasks/hello'
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(
            api_schemas.GetSchema(data).validate(),
        )

    def test_duplicate_task_id(self):
        post_data = json.dumps(self.valid_post_data)
        response = self.client.post(
            '/api/v1/walle/v14/tasks',
            post_data,
            content_type='application/json',
        )
        response = self.client.post(
            '/api/v1/walle/v14/tasks',
            post_data,
            content_type='application/json',
        )
        logger.debug(response.content)
        self.assertEqual(response.status_code, 500)

        data = response.json()

        self.assertTrue(
            api_schemas.ErrorSchema(data).validate(),
        )

    def test_post_is_not_allowed_if_task_id_is_specified(self):
        post_data = json.dumps(self.valid_post_data)
        response = self.client.post(
            '/api/v1/walle/v14/tasks/task_id_is_given',
            post_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 405)

        data = response.json()

        self.assertTrue(
            api_schemas.ErrorSchema(data).validate(),
        )


class TestGet(helper.CmsBaseTestCase, django.test.TestCase):
    def test_normal(self):
        response = self.client.get(
            '/api/v1/walle/v14/tasks/production-1'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(
            api_schemas.GetSchema(data).validate(),
        )

    def test_missing(self):
        response = self.client.get(
            '/api/v1/walle/v14/tasks/production-25'
        )
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertTrue(
            api_schemas.ErrorSchema(data).validate(),
        )

    def test_list_schema(self):
        response = self.client.get(
            '/api/v1/walle/v14/tasks'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(
            api_schemas.GetListSchema(data).validate(),
        )

    def test_list_data(self):
        data = self.client.get(
            '/api/v1/walle/v14/tasks'
        ).json()

        # there is no deleted tasks (marked with walle_deleted) in list results
        self.assertEqual(
            3,
            len(data['result']),
        )
        self.assertEqual(
            0,
            len(
                list(
                    filter(lambda task: task['id'] == 'production-4', data['result'])
                )
            )
        )
        source_task = cms_models.Task.objects_for_frontend.get(walle_id='production-1')
        api_task = list(
            filter(lambda task: task['id'] == 'production-1', data['result'])
        )[0]
        self.assertEqual(
            source_task.walle_action,
            api_task['action'],
        )
        self.assertEqual(
            source_task.walle_status,
            api_task['status'],
        )

    def test_empty_list(self):
        cms_models.Task.objects_for_frontend.all().delete()
        response = self.client.get(
            '/api/v1/walle/v14/tasks'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(
            api_schemas.GetListSchema(data).validate(),
        )

        self.assertEqual(
            0,
            len(data['result']),
        )


class TestDelete(helper.CmsBaseTestCase, django.test.TransactionTestCase):
    def test_normal(self):
        response = self.client.delete(
            '/api/v1/walle/v14/tasks/production-1'
        )
        self.assertEqual(response.status_code, 204)

        # task is not really deleted from db, but marked as deleted for walle
        task = cms_models.Task.objects_for_frontend.get(walle_id='production-1')
        for audit in task.auditlog_set.all():
            logger.debug(audit)
        self.assertTrue(
            task.walle_deleted,
        )

        # should return 404 if task is marked as deleted for walle
        response = self.client.delete(
            '/api/v1/walle/v14/tasks/production-1'
        )
        self.assertEqual(response.status_code, 404)

    def test_missing(self):
        response = self.client.delete(
            '/api/v1/walle/v14/tasks/production-35'
        )
        self.assertEqual(response.status_code, 404)


class TestUpdate(helper.CmsBaseTestCase, django.test.TestCase):
    '''
    Test PUT method is not supported
    '''
    def test_normal(self):
        # existing task
        response = self.client.put(
            '/api/v1/walle/v14/tasks/production-1'
        )
        self.assertEqual(response.status_code, 405)

        # tasks list
        response = self.client.put(
            '/api/v1/walle/v14/tasks'
        )
        self.assertEqual(response.status_code, 405)

        # missing task
        response = self.client.put(
            '/api/v1/walle/v14/tasks/production-35'
        )
        self.assertEqual(response.status_code, 405)
