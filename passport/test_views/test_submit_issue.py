# -*- coding: utf-8 -*-

import datetime
import json

from django.contrib.auth.models import User
from django.contrib.comments import Comment
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.client import RequestFactory

from passport_grants_configurator.apps.core.models import (
    Action,
    Consumer,
    Email,
    Environment,
    Issue,
    Macros,
    Namespace,
    Network,
)
from passport_grants_configurator.apps.core.test.utils import MockRequests
from passport_grants_configurator.apps.core.views import issue_submit

TEST_COMMENT = 'test comment'


class SubmitIssueCase(TestCase):
    fixtures = ['default.json']

    url = '/grants/issue/submit/'

    def get_query_params(self, **kwargs):
        params = {
            'consumer_name': 'some_consumer',
            'environments': [1],
            'namespace': 1,
            'comment': TEST_COMMENT,
        }
        params.update(kwargs)
        return params

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(id=3)

        self.mock_requests = MockRequests()
        self.mock_requests.start()
        self.mock_requests.response.text = '0.0.0.0\tyes\n'

    def tearDown(self):
        self.mock_requests.stop()

    def get_test_consumer_data(self, type_=Issue.TO_CREATE,
                               consumer_name=u'new_consumer_2', _id=u'',
                               consumer_id=None, consumer_name_new=u'new_name', emails=None):
        data = {
            u'type': type_,
            u'comment': TEST_COMMENT,
            u'consumer_description': u'new description',
            u'consumer_name': consumer_name,
            u'environments': [1],
            u'add_action': [
                3,
                4,
                5,
            ],
            u'del_action': [],
            u'id': _id,
            u'add_macros': [
                1,
            ],
            u'del_macros': [],
            u'namespace': 1,
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 2,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-0-network': 1,
            u'add_networks-0-environment': 1,
            u'add_networks-1-network': 2,
            u'add_networks-1-environment': 1,
        }
        if consumer_id:
            data.update(
                consumer=consumer_id,
                consumer_name_new=consumer_name_new,
            )
        if emails:
            data.update(emails=emails)
        return data

    def assert_consumer_name_invalid(self, response):
        response_data = json.loads(response.content)
        self.assertEqual(
            response_data[u'errors'],
            [u'__all__: Поле consumer_name содержит запрещенные символы']
        )
        self.assertEqual(response_data[u'success'], False)

    def test_submit_new_consumer(self):
        request = self.factory.post(self.url, self.get_test_consumer_data())
        request.user = self.user

        response = issue_submit(request)
        issue = Issue.objects.latest('id')

        self.assertEqual(json.loads(response.content), {
            u'issue_id': issue.id,
            u'success': True,
        })

        meta_add_action = (
            {u'grant__name': u'captcha', 'name': u'*'},
            {u'grant__name': u'login', u'name': u'suggest'},
            {u'grant__name': u'login', u'name': u'validate'},
        )
        add_action_set = set(Action.objects.get(**kw) for kw in meta_add_action)
        add_macros_set = set(Macros.objects.filter(name='some_macros1'))

        self.assertEqual(issue.type, Issue.TO_CREATE)
        self.assertEqual(issue.consumer, None)
        self.assertEqual(issue.consumer_name, u'new_consumer_2')
        self.assertEqual(issue.consumer_description, u'new description')
        self.assertEqual(set(issue.environments.all()), {Environment.objects.get(id=1)})
        self.assertEqual(issue.namespace, Namespace.objects.get(id=1))
        self.assertEqual(set(issue.add_action.all()), add_action_set)
        self.assertEqual(set(issue.add_macros.all()), add_macros_set)
        self.assertEqual(set(issue.add_network.all()), set(Network.objects.filter(id__in=[1, 2])))
        self.assertEqual(set(issue.del_action.all()), set())
        self.assertEqual(set(issue.del_macros.all()), set())
        self.assertEqual(set(issue.del_network.all()), set())
        self.assertEqual(issue.creator, self.user)
        self.assertEqual(issue.status, Issue.NEW)

        self.assert_comment_created(object_pk=issue.id)

    def test_submit_clone_consumer(self):
        request = self.factory.post(self.url, self.get_test_consumer_data(type_=Issue.TO_CLONE))
        request.user = self.user

        response = issue_submit(request)
        issue = Issue.objects.latest('id')

        self.assertEqual(json.loads(response.content), {
            u'issue_id': issue.id,
            u'success': True,
        })

        meta_add_action = (
            {u'grant__name': u'captcha', 'name': u'*'},
            {u'grant__name': u'login', u'name': u'suggest'},
            {u'grant__name': u'login', u'name': u'validate'},
        )
        add_action_set = set(Action.objects.get(**kw) for kw in meta_add_action)
        add_macros_set = set(Macros.objects.filter(name='some_macros1'))

        self.assertEqual(issue.type, Issue.TO_CLONE)
        self.assertEqual(issue.consumer, None)
        self.assertEqual(issue.consumer_name, u'new_consumer_2')
        self.assertEqual(issue.consumer_description, u'new description')
        self.assertEqual(set(issue.environments.all()), {Environment.objects.get(id=1)})
        self.assertEqual(issue.namespace, Namespace.objects.get(id=1))
        self.assertEqual(set(issue.add_action.all()), add_action_set)
        self.assertEqual(set(issue.add_macros.all()), add_macros_set)
        self.assertEqual(set(issue.add_network.all()), set(Network.objects.filter(id__in=[1, 2])))
        self.assertEqual(set(issue.del_action.all()), set())
        self.assertEqual(set(issue.del_macros.all()), set())
        self.assertEqual(set(issue.del_network.all()), set())
        self.assertEqual(issue.creator, self.user)
        self.assertEqual(issue.status, Issue.NEW)

        self.assert_comment_created(object_pk=issue.id)

    def test_submit_new_consumer_with_invalid_name(self):
        request = self.factory.post(self.url, self.get_test_consumer_data(consumer_name=u'new consumer'))
        request.user = self.user

        response = issue_submit(request)
        self.assert_consumer_name_invalid(response)

    def test_submit_with_emails(self):
        existing_address = 'test1@yandex-team.ru'
        request = self.factory.post(self.url, self.get_test_consumer_data(emails=[existing_address]))
        request.user = self.user

        email = Email.objects.get(address=existing_address)

        response = issue_submit(request)
        issue = Issue.objects.latest('id')

        self.assertEqual(json.loads(response.content), {
            u'issue_id': issue.id,
            u'success': True,
        })
        self.assertEquals(set(issue.emails.all()), {email})

    def test_submit_with_invalid_emails(self):
        email = 'alice@alice.com'

        request = self.factory.post(self.url, self.get_test_consumer_data(emails=[email]))
        request.user = self.user
        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(
            response_data[u'errors'],
            [u'__all__: emails: Введите валидный адрес с доменом yandex-team или логин пользователя'],
        )
        self.assertFalse(response_data[u'success'])

    def test_submit_new_consumer_existing_issue(self):
        Issue.objects.filter(id=1).update(status=Issue.DRAFT)
        request = self.factory.post(
            self.url,
            self.get_test_consumer_data(
                consumer_name='new_consumer',
                _id=1,
            ),
        )
        request.user = self.user

        response = issue_submit(request)
        self.assertEqual(json.loads(response.content), {
            u'issue_id': 1,
            u'success': True,
        })

        issue = Issue.objects.get(id=1)

        add_action_set = set(Action.objects.get(id=id_) for id_ in [3, 4, 5])
        add_macros_set = set(Macros.objects.filter(id=1))

        self.assertEqual(issue.type, Issue.TO_CREATE)
        self.assertEqual(issue.consumer, None)
        self.assertEqual(issue.consumer_name, 'new_consumer')
        self.assertEqual(issue.consumer_description, 'new description')
        self.assertEqual(set(issue.environments.all()), set(Environment.objects.filter(id=1)))
        self.assertEqual(issue.namespace, Namespace.objects.get(id=1))
        self.assertEqual(set(issue.add_action.all()), add_action_set)
        self.assertEqual(set(issue.add_macros.all()), add_macros_set)
        self.assertEqual(set(issue.add_network.all()), set(Network.objects.filter(id__in=[1, 2])))
        self.assertEqual(set(issue.del_action.all()), set())
        self.assertEqual(set(issue.del_macros.all()), set())
        self.assertEqual(set(issue.del_network.all()), set())
        self.assertEqual(issue.creator, self.user)
        self.assertEqual(issue.status, Issue.NEW)

    def test_submit_new_consumer_existing_issue_invalid_name(self):
        Issue.objects.filter(id=1).update(status=Issue.DRAFT)
        request = self.factory.post(
            self.url,
            self.get_test_consumer_data(
                consumer_name='new consumer',
                _id=1,
            ),
        )
        request.user = self.user
        response = issue_submit(request)
        self.assert_consumer_name_invalid(response)

    def test_submit_existing_consumer(self):
        data = {
            u'type': Issue.TO_MODIFY,
            'comment': TEST_COMMENT,
            u'consumer_description': u'new description',
            u'consumer': 1,
            u'environments': [1],
            u'add_action': [
                3,
                4,
                5,
            ],
            u'del_action': [
                1,
                2,
            ],
            u'id': '',
            u'add_macros': [
                1,
            ],
            u'del_macros': [
                2,
            ],
            u'namespace': 1,
            u'del_networks-TOTAL_FORMS': 1,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 1,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-0-network': 1,
            u'add_networks-0-environment': 1,
            u'del_networks-0-network': 3,
            u'del_networks-0-environment': 1,
        }

        request = self.factory.post(self.url, data)
        request.user = self.user

        response = issue_submit(request)
        issue = Issue.objects.latest('id')

        self.assertEqual(json.loads(response.content), {
            u'issue_id': issue.id,
            u'success': True,
        })

        meta_add_action = (
            {u'grant__name': u'captcha', u'name': u'*'},
            {u'grant__name': u'login', u'name': u'suggest'},
            {u'grant__name': u'login', u'name': u'validate'},
        )
        meta_del_action = (
            {u'grant__name': u'password', u'name': u'is_changing_required'},
            {u'grant__name': u'password', u'name': u'validate'},
        )
        add_action_set = set(Action.objects.get(**kw) for kw in meta_add_action)
        add_macros_set = set(Macros.objects.filter(name=u'some_macros1'))
        del_action_set = set(Action.objects.get(**kw) for kw in meta_del_action)
        del_macros_set = set(Macros.objects.filter(name=u'some_macros2'))

        self.assertEqual(issue.type, Issue.TO_MODIFY)
        self.assertEqual(issue.consumer, Consumer.objects.get(name=u'some_consumer'))
        self.assertEqual(issue.consumer_name, u'')
        self.assertEqual(issue.consumer_description, u'new description')
        self.assertEqual(set(issue.environments.all()), {Environment.objects.get(id=1)})
        self.assertEqual(issue.namespace, Namespace.objects.get(id=1))
        self.assertEqual(set(issue.add_action.all()), add_action_set)
        self.assertEqual(set(issue.add_macros.all()), add_macros_set)
        self.assertEqual(set(issue.add_network.all()), {Network.objects.get(id=1)})
        self.assertEqual(set(issue.del_action.all()), del_action_set)
        self.assertEqual(set(issue.del_macros.all()), del_macros_set)
        self.assertEqual(set(issue.del_network.all()), {Network.objects.get(id=3)})
        self.assertEqual(issue.creator, self.user)
        self.assertEqual(issue.status, Issue.NEW)

    def test_submit_existing_consumer_with_temporal_grants(self):
        data = {
            u'type': Issue.TO_SET_EXPIRATION,
            'comment': TEST_COMMENT,
            u'consumer_description': u'new description',
            u'consumer': 1,
            u'environments': [1],
            u'expiration': u'20.10.2016',
            u'add_action': [
                3,
                4,
                5,
            ],
            u'del_action': [
                1,
                2,
            ],
            u'id': '',
            u'add_macros': [
                1,
            ],
            u'del_macros': [
                2,
            ],
            u'namespace': 1,
            u'del_networks-TOTAL_FORMS': 1,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 1,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-0-network': 1,
            u'add_networks-0-environment': 1,
            u'del_networks-0-network': 3,
            u'del_networks-0-environment': 1,
        }

        request = self.factory.post(self.url, data)
        request.user = self.user

        response = issue_submit(request)
        issue = Issue.objects.latest('id')

        self.assertEqual(json.loads(response.content), {
            u'issue_id': issue.id,
            u'success': True,
        })

        meta_add_action = (
            {u'grant__name': u'captcha', u'name': u'*'},
            {u'grant__name': u'login', u'name': u'suggest'},
            {u'grant__name': u'login', u'name': u'validate'},
        )
        meta_del_action = (
            {u'grant__name': u'password', u'name': u'is_changing_required'},
            {u'grant__name': u'password', u'name': u'validate'},
        )
        add_action_set = set(Action.objects.get(**kw) for kw in meta_add_action)
        add_macros_set = set(Macros.objects.filter(name=u'some_macros1'))
        del_action_set = set(Action.objects.get(**kw) for kw in meta_del_action)
        del_macros_set = set(Macros.objects.filter(name=u'some_macros2'))

        self.assertEqual(issue.type, Issue.TO_SET_EXPIRATION)
        self.assertEqual(issue.consumer, Consumer.objects.get(name=u'some_consumer'))
        self.assertEqual(issue.consumer_name, u'')
        self.assertEqual(issue.consumer_description, u'new description')
        self.assertEqual(set(issue.environments.all()), {Environment.objects.get(id=1)})
        self.assertEqual(issue.namespace, Namespace.objects.get(id=1))
        self.assertEqual(set(issue.add_action.all()), add_action_set)
        self.assertEqual(set(issue.add_macros.all()), add_macros_set)
        self.assertEqual(set(issue.add_network.all()), {Network.objects.get(id=1)})
        self.assertEqual(set(issue.del_action.all()), del_action_set)
        self.assertEqual(set(issue.del_macros.all()), del_macros_set)
        self.assertEqual(set(issue.del_network.all()), {Network.objects.get(id=3)})
        self.assertEqual(issue.creator, self.user)
        self.assertEqual(issue.status, Issue.NEW)
        self.assertEqual(issue.expiration, datetime.date(2016, 10, 20))

    def test_submit_existing_consumer_existing_issue(self):
        Issue.objects.filter(id=1).update(status=Issue.DRAFT)
        data = {
            u'type': Issue.TO_MODIFY,
            'comment': TEST_COMMENT,
            u'consumer_description': u'new description',
            u'consumer': 1,
            u'environments': [1],
            u'add_action': [
                3,
                4,
                5,
            ],
            u'del_action': [
                1,
                2,
            ],
            u'id': 1,
            u'add_macros': [
                1,
            ],
            u'del_macros': [
                2,
            ],
            u'namespace': 1,
            u'del_networks-TOTAL_FORMS': 1,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 1,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-0-network': 1,
            u'add_networks-0-environment': 1,
            u'del_networks-0-network': 3,
            u'del_networks-0-environment': 1,
        }

        request = self.factory.post(self.url, data)
        request.user = self.user

        response = issue_submit(request)
        self.assertEqual(json.loads(response.content), {
            u'issue_id': 1,
            u'success': True,
        })

        issue = Issue.objects.get(id=1)

        add_action_set = set(Action.objects.get(id=id_) for id_ in [3, 4, 5])
        add_macros_set = set(Macros.objects.filter(id=1))
        del_action_set = set(Action.objects.get(id=id_) for id_ in [1, 2])
        del_macros_set = set(Macros.objects.filter(id=2))

        self.assertEqual(issue.type, issue.TO_MODIFY)
        self.assertEqual(issue.consumer, Consumer.objects.get(name=u'some_consumer'))
        self.assertEqual(issue.consumer_name, u'')
        self.assertEqual(issue.consumer_description, u'new description')
        self.assertEqual(set(issue.environments.all()), {Environment.objects.get(id=1)})
        self.assertEqual(issue.namespace, Namespace.objects.get(id=1))
        self.assertEqual(set(issue.add_action.all()), add_action_set)
        self.assertEqual(set(issue.add_macros.all()), add_macros_set)
        self.assertEqual(set(issue.add_network.all()), set(Network.objects.filter(id=1)))
        self.assertEqual(set(issue.del_action.all()), del_action_set)
        self.assertEqual(set(issue.del_macros.all()), del_macros_set)
        self.assertEqual(set(issue.del_network.all()), set(Network.objects.filter(id=3)))
        self.assertEqual(issue.creator, self.user)
        self.assertEqual(issue.status, Issue.NEW)

    def test_submit_renaming_existing_consumer(self):
        data = {
            u'type': Issue.TO_MODIFY,
            'comment': TEST_COMMENT,
            u'consumer_description': u'new description',
            u'consumer': 1,
            u'consumer_name_new': u'new_name',
            u'environments': [1],
            u'add_action': [
                3,
                4,
                5,
            ],
            u'del_action': [
                1,
                2,
            ],
            u'id': '',
            u'add_macros': [
                1,
            ],
            u'del_macros': [
                2,
            ],
            u'namespace': 1,
            u'del_networks-TOTAL_FORMS': 1,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 1,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-0-network': 2,
            u'add_networks-0-environment': 1,
            u'del_networks-0-network': 3,
            u'del_networks-0-environment': 1,
        }

        request = self.factory.post(self.url, data)
        request.user = self.user

        response = issue_submit(request)
        issue = Issue.objects.latest('id')

        self.assertEqual(json.loads(response.content), {
            u'issue_id': issue.id,
            u'success': True,
        })

        add_action_set = set(Action.objects.filter(id__in=[3, 4, 5]))
        add_macros_set = set(Macros.objects.filter(id=1))
        del_action_set = set(Action.objects.filter(id__in=[1, 2]))
        del_macros_set = set(Macros.objects.filter(id=2))

        self.assertEqual(issue.type, Issue.TO_MODIFY)
        self.assertEqual(issue.consumer, Consumer.objects.get(name=u'some_consumer'))
        self.assertEqual(issue.consumer_name_new, u'new_name')
        self.assertEqual(issue.consumer_description, u'new description')
        self.assertEqual(set(issue.environments.all()), set(Environment.objects.filter(id=1)))
        self.assertEqual(issue.namespace, Namespace.objects.get(id=1))
        self.assertEqual(set(issue.add_action.all()), add_action_set)
        self.assertEqual(set(issue.add_macros.all()), add_macros_set)
        self.assertEqual(set(issue.add_network.all()), {Network.objects.get(id=2)})
        self.assertEqual(set(issue.del_action.all()), del_action_set)
        self.assertEqual(set(issue.del_macros.all()), del_macros_set)
        self.assertEqual(set(issue.del_network.all()), {Network.objects.get(id=3)})
        self.assertEqual(issue.creator, self.user)
        self.assertEqual(issue.status, Issue.NEW)

    def test_submit_renaming_existing_consumer_invalid_name(self):
        data = self.get_test_consumer_data(
            type_=Issue.TO_MODIFY,
            consumer_id=1,
            consumer_name_new='new name',
        )
        request = self.factory.post(self.url, data)
        request.user = self.user

        response = issue_submit(request)
        self.assert_consumer_name_invalid(response)

    def test_submit_consumer_without_grants(self):
        data = {
            u'type': Issue.TO_CREATE,
            'comment': TEST_COMMENT,
            u'consumer_name': u'new_consumer_2',
            u'consumer_description': u'new description',
            u'environments': [1],
            u'namespace': 1,
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        }

        request = self.factory.post(self.url, data)
        request.user = self.user

        response = issue_submit(request)
        issue = Issue.objects.latest('id')

        self.assertEqual(json.loads(response.content), {
            u'issue_id': issue.id,
            u'success': True,
        })

        self.assertEqual(issue.type, Issue.TO_CREATE)
        self.assertEqual(issue.consumer, None)
        self.assertEqual(issue.consumer_name, u'new_consumer_2')
        self.assertEqual(issue.consumer_description, u'new description')
        self.assertEqual(set(issue.environments.all()), {Environment.objects.get(id=1)})
        self.assertEqual(issue.namespace, Namespace.objects.get(id=1))
        self.assertEqual(set(issue.add_action.all()), set())
        self.assertEqual(set(issue.add_macros.all()), set())
        self.assertEqual(set(issue.add_network.all()), set())
        self.assertEqual(set(issue.del_action.all()), set())
        self.assertEqual(set(issue.del_macros.all()), set())
        self.assertEqual(set(issue.del_network.all()), set())
        self.assertEqual(issue.creator, self.user)
        self.assertEqual(issue.status, Issue.NEW)

    def test_submit_rename_consumer(self):
        data = {
            u'type': Issue.TO_MODIFY,
            'comment': TEST_COMMENT,
            u'consumer': 1,
            u'consumer_name_new': u'renamed_consumer',
            u'environments': [1],
            u'namespace': 1,
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        }

        request = self.factory.post(self.url, data)
        request.user = self.user

        response = issue_submit(request)
        issue = Issue.objects.latest('id')

        self.assertEqual(json.loads(response.content), {
            u'issue_id': issue.id,
            u'success': True,
        })

        self.assertEqual(issue.type, Issue.TO_MODIFY)
        self.assertEqual(issue.consumer, Consumer.objects.get(name='some_consumer'))
        self.assertEqual(issue.consumer_name_new, u'renamed_consumer')
        self.assertEqual(issue.consumer_description, u'')
        self.assertEqual(set(issue.environments.all()), set(Environment.objects.filter(id=1)))
        self.assertEqual(issue.namespace, Namespace.objects.get(id=1))
        self.assertEqual(set(issue.add_action.all()), set())
        self.assertEqual(set(issue.add_macros.all()), set())
        self.assertEqual(set(issue.add_network.all()), set())
        self.assertEqual(set(issue.del_action.all()), set())
        self.assertEqual(set(issue.del_macros.all()), set())
        self.assertEqual(set(issue.del_network.all()), set())
        self.assertEqual(issue.creator, self.user)
        self.assertEqual(issue.status, Issue.NEW)

    def test_no_consumer_name(self):
        request = self.factory.post(self.url, {
            u'type': Issue.TO_CREATE,
            'comment': TEST_COMMENT,
            u'consumer_name': '',
            u'environments': [1],
            u'namespace': 1,
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })
        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'errors'], [u'__all__: Не передано обязательное поле consumer_name'])
        self.assertEqual(response_data[u'success'], False)

    def test_no_namespace(self):
        request = self.factory.post(self.url, {
            u'type': Issue.TO_CREATE,
            'comment': TEST_COMMENT,
            u'consumer_name': 'consumer',
            u'environments': [1],
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })
        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'errors'], [u'namespace: Обязательное поле.'])
        self.assertEqual(response_data[u'success'], False)

    def test_no_environment(self):
        request = self.factory.post(self.url, {
            u'type': Issue.TO_CREATE,
            'comment': TEST_COMMENT,
            u'consumer_name': u'consumer',
            u'namespace': 1,
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })
        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'errors'], [u'environments: Обязательное поле.'])
        self.assertEqual(response_data[u'success'], False)

    def test_add_nonexistent_grants(self):
        request = self.factory.post(self.url, {
            u'type': Issue.TO_CREATE,
            'comment': TEST_COMMENT,
            u'consumer_name': u'consumer',
            u'namespace': 1,
            u'environments': [1],
            u'add_action': [100500],
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })

        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'errors'], [u'add_action: Выберите корректный вариант. 100500 нет среди допустимых значений.'])
        self.assertEqual(response_data[u'success'], False)

    def test_remove_nonexistent_grants(self):
        request = self.factory.post(self.url, {
            u'type': Issue.TO_MODIFY,
            'comment': TEST_COMMENT,
            u'consumer': 1,
            u'namespace': 1,
            u'environments': [1],
            u'del_action': [
                100500,
            ],
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })

        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'errors'], [
            u'del_action: Выберите корректный вариант. 100500 нет среди допустимых значений.',
        ])
        self.assertEqual(response_data[u'success'], False)

    def test_add_nonexistent_macroses(self):
        request = self.factory.post(self.url, {
            u'type': Issue.TO_CREATE,
            'comment': TEST_COMMENT,
            u'consumer_name': u'consumer',
            u'namespace': 1,
            u'environments': [1],
            u'add_macros': [
                100500,
            ],
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })

        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'errors'], [
            u'add_macros: Выберите корректный вариант. 100500 нет среди допустимых значений.',
        ])
        self.assertEqual(response_data[u'success'], False)

    def test_remove_nonexistent_macroses(self):
        request = self.factory.post(self.url, {
            u'type': Issue.TO_MODIFY,
            'comment': TEST_COMMENT,
            u'consumer': 1,
            u'namespace': 1,
            u'environments': [1],
            u'del_macros': [
                100500,
            ],
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })

        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'errors'], [
            u'del_macros: Выберите корректный вариант. 100500 нет среди допустимых значений.',
        ])
        self.assertEqual(response_data[u'success'], False)

    def test_issue_without_any_data_changes(self):
        request = self.factory.post(self.url, {
            u'type': Issue.TO_MODIFY,
            'comment': TEST_COMMENT,
            u'consumer': 1,
            u'namespace': 1,
            u'environments': [1],
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })
        request.user = self.user

        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'success'], False)

    def test_attempt_to_change_nonexistent_issue(self):
        request = self.factory.post(self.url, {
            u'type': Issue.TO_CREATE,
            'comment': TEST_COMMENT,
            u'consumer_name': u'consumer',
            u'namespace': 1,
            u'environments': [1],
            u'id': 100500,
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })
        request.user = self.user

        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'errors'], [
            u'id: Выберите корректный вариант. Вашего варианта нет среди допустимых значений.',
        ])
        self.assertEqual(response_data[u'success'], False)

    def test_attempt_to_rename_nonexistent_consumer(self):
        request = self.factory.post(self.url, {
            u'type': Issue.TO_MODIFY,
            'comment': TEST_COMMENT,
            u'consumer': 100500,
            u'consumer_name_new': u'new_name',
            u'namespace': 1,
            u'environments': [1],
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })
        request.user = self.user

        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'errors'], [
            u'consumer: Выберите корректный вариант. Вашего варианта нет среди допустимых значений.',
            u'__all__: Не передано обязательное поле consumer',  # параграфы
        ])
        self.assertEqual(response_data[u'success'], False)

    def test_uneditable_issue(self):
        Issue.objects.filter(id=1).update(status=Issue.REJECTED)

        request = self.factory.post(self.url, {
            'comment': TEST_COMMENT,
            u'consumer_name': u'consumer',
            u'namespace': 1,
            u'environments': [1],
            u'id': 1,
            u'type': u'C',
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })
        request.user = self.user

        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'errors'], [
            u'id: Выберите корректный вариант. Вашего варианта нет среди допустимых значений.',
        ])
        self.assertEqual(response_data[u'success'], False)

    def test_attempt_to_rename_consumer_to_existing(self):
        Consumer.objects.create(name=u'existing_consumer', namespace_id=1)

        request = self.factory.post(self.url, {
            u'type': Issue.TO_MODIFY,
            'comment': TEST_COMMENT,
            u'consumer': 1,
            u'consumer_name_new': u'existing_consumer',
            u'namespace': 1,
            u'environments': [1],
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })
        request.user = self.user

        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'errors'], [u'__all__: Потребитель с именем "existing_consumer" уже существует'])
        self.assertEqual(response_data[u'success'], False)

    def test_adding_ungranted_network(self):
        self.mock_requests.response.text = 'someperson1,someperson2\n'

        data = {
            u'type': Issue.TO_CREATE,
            'comment': TEST_COMMENT,
            u'consumer_description': u'new description',
            u'consumer_name': u'new_consumer_2',
            u'environments': [1],
            u'add_action': [],
            u'del_action': [],
            u'id': '',
            u'add_macros': [],
            u'del_macros': [],
            u'namespace': 1,
            u'add_networks-0-network': 5,
            u'add_networks-0-environment': 5,
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 1,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        }
        request = self.factory.post(self.url, data)
        request.user = User()
        response = issue_submit(request)

        response_data = json.loads(response.content)
        self.assertEqual(
            response_data[u'errors'],
            [u'Нет прав на хост grantushka.yandex-team.ru']
        )
        self.assertEqual(response_data[u'success'], False)

    def test_attempt_to_edit_other_persons_issue(self):
        Issue.objects.filter(id=1).update(status=Issue.DRAFT)

        data = {
            u'type': Issue.TO_CREATE,
            'comment': TEST_COMMENT,
            u'consumer_description': u'new description',
            u'consumer_name': u'new_consumer_2',
            u'environments': [1],
            u'add_action': [1],
            u'del_action': [],
            u'id': 1,
            u'add_macros': [],
            u'del_macros': [],
            u'namespace': 1,
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        }
        request = self.factory.post(self.url, data)
        request.user = User.objects.create()
        response = issue_submit(request)

        response_data = json.loads(response.content)
        self.assertEqual(
            response_data[u'errors'],
            [u'У Вас нет необходимых прав на изменение этой заявки']
        )
        self.assertEqual(response_data[u'success'], False)

    def test_create_issue_having_grants_namespace_other_than_consumers(self):
        Issue.objects.filter(id=1).update(status=Issue.DRAFT)
        data = {
            u'type': Issue.TO_CREATE,
            'comment': TEST_COMMENT,
            u'consumer_description': u'new description',
            u'consumer_name': u'new_consumer',
            u'environments': [1],
            u'add_action': [
                3,
                4,
                8,
            ],
            u'del_action': {},
            u'id': 1,
            u'add_macros': [
                3,
            ],
            u'del_macros': [],
            u'namespace': 1,
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        }

        request = self.factory.post(self.url, data)
        request.user = self.user

        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(
            response_data[u'errors'],
            [
                u'add_action: Выберите корректный вариант. 8 нет среди допустимых значений.',
                u'add_macros: Выберите корректный вариант. 3 нет среди допустимых значений.',
            ]
        )
        self.assertEqual(response_data[u'success'], False)

    def test_submit_old_conductor_macro(self):
        data = {
            u'type': Issue.TO_CREATE,
            'comment': TEST_COMMENT,
            u'consumer_description': u'new description',
            u'consumer_name': u'new_consumer_2',
            u'environments': [1],
            u'add_action': [3],
            u'del_action': [],
            u'id': '',
            u'add_macros': [],
            u'del_macros': [],
            u'namespace': 1,
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 1,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-0-network': 8,
            u'add_networks-0-environment': 1,
        }

        request = self.factory.post(self.url, data)
        request.user = self.user

        response = issue_submit(request)
        response_data = json.loads(response.content)
        self.assertEqual(
            response_data[u'errors'],
            [u'network: Old conductor macro used _C_PASSPORT_GRANTUSHKA_STABLE_'],
        )
        self.assertEqual(response_data[u'success'], False)

    def assert_comment_created(self, object_pk, model='issue', app='core', text=TEST_COMMENT):
        content_type_id = ContentType.objects.get(model=model, app_label=app).id
        comment = Comment.objects.filter(
            content_type_id=content_type_id,
            object_pk=object_pk
        ).latest('submit_date')

        self.assertEqual(
            comment.comment,
            text,
        )

    def test_submit_historydb_issue_with_client(self):
        data = {
            u'type': Issue.TO_CREATE,
            u'comment': TEST_COMMENT,
            u'consumer_description': u'historydb with client',
            u'consumer_name': u'HWC',
            u'environments': [2],
            u'add_action': [27],
            u'del_action': [],
            u'id': u'',
            u'add_macros': [],
            u'del_macros': [],
            u'namespace': 11,
            u'clients': [5],
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        }

        request = self.factory.post(self.url, data)
        request.user = self.user

        response = issue_submit(request)
        issue = Issue.objects.latest('id')

        self.assertEqual(json.loads(response.content), {
            u'issue_id': issue.id,
            u'success': True,
        })

    def test_delete_bound_clients_from_issue(self):
        request = self.factory.post(self.url, {
            u'type': Issue.TO_MODIFY,
            'comment': TEST_COMMENT,
            u'consumer': 11,
            u'namespace': 1,
            u'environments': [1],
            u'del_networks-TOTAL_FORMS': 0,
            u'del_networks-INITIAL_FORMS': 0,
            u'del_networks-MAX_NUM_FORMS': 1000,
            u'add_networks-TOTAL_FORMS': 0,
            u'add_networks-INITIAL_FORMS': 0,
            u'add_networks-MAX_NUM_FORMS': 1000,
        })
        request.user = self.user

        response = issue_submit(request)
        issue = Issue.objects.latest('id')
        response_data = json.loads(response.content)
        self.assertEqual(response_data[u'success'], True)
        self.assertEqual(response_data[u'issue_id'], issue.id)

    def test_can_edit_namespace(self):
        admin_namespaces = ['passport']

        with self.settings(
            PASSPORT_TEAM_ADMIN=[self.user.username],
            NAMESPACES_FOR_ADMINS=admin_namespaces,
        ):
            request = self.factory.post(self.url, self.get_test_consumer_data())
            request.user = self.user

            response = issue_submit(request)
            response_data = json.loads(response.content)
            issue = Issue.objects.latest('id')
            self.assertEqual(response_data, {
                u'issue_id': issue.id,
                u'success': True,
            })

        with self.settings(PASSPORT_TEAM_ADMIN=['admin'], NAMESPACES_FOR_ADMINS=admin_namespaces):
            request = self.factory.post(self.url, self.get_test_consumer_data(consumer_name='new-consumer2'))
            request.user = self.user

            response = issue_submit(request)
            response_data = json.loads(response.content)
            self.assertEqual(response_data[u'errors'],
                             [u'У Вас нет необходимых прав на изменение этой заявки'])
            self.assertEqual(response_data[u'success'], False)
