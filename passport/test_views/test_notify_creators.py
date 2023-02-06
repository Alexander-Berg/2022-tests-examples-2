# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core import mail
from django.test import TestCase, RequestFactory

from passport_grants_configurator.apps.core.mail import get_project_title
from passport_grants_configurator.apps.core.models import Issue
from passport_grants_configurator.apps.core.test.utils import MockRequests
from passport_grants_configurator.apps.core.views import notify_creators


class NotifyCreatorsCase(TestCase):
    fixtures = ['default.json']
    maxDiff = None

    url = '/grants/notify/'

    def setUp(self):
        self.factory = RequestFactory()
        self.requests = MockRequests()
        self.requests.start()

    def tearDown(self):
        self.requests.stop()

    def setup_bitbucket_last_commits_info(
        self,
        last_unixtime=1490994000000,  # 2017-04-01 00:00:00
        previous_unixtime=1488315600000,  # 2017-03-01 00:00:00
    ):
        commits_info = {
            'values': [
                {
                    'committerTimestamp': last_unixtime,
                    'message': 'passport-grants-robo has exported new grants'
                },
                {
                    'committerTimestamp': previous_unixtime,
                    'message': 'passport-grants-robo has exported new grants',
                },
            ],
        }
        self.requests.response.text = json.dumps(commits_info)

    def make_request(self, data):
        request = self.factory.post(self.url, json.dumps(data), content_type='application/json')
        return notify_creators(request)

    def assert_ok_response(self, response, status_code=200):
        self.assertEqual(response.status_code, status_code)
        response_content = json.loads(response.content)
        self.assertTrue(response_content['success'])

    def assert_error_response(self, response, errors=None, status_code=200):
        self.assertEqual(response.status_code, status_code)
        response_content = json.loads(response.content)
        self.assertFalse(response_content['success'])
        if errors:
            self.assertEqual(sorted(response_content['errors']), sorted(errors))

    def assert_mail_sent(self, message_num, project, recipients, message_data):
        self.assertEquals(len(mail.outbox), message_num)
        subjects = [mail.outbox[i].subject for i in range(message_num)]
        actual_recipients = sum([mail.outbox[i].to for i in range(message_num)], [])
        messages = [mail.outbox[i].body for i in range(message_num)]
        self.assertEqual(
            set(subjects),
            {
                '%s Пакет c нужными вам грантами для %s в проде' % (
                    get_project_title(),
                    project,
                ),
            },
        )
        self.assertEqual(sorted(actual_recipients), sorted(recipients))
        self.assertEqual(sorted(messages), sorted(message_data))

    def assert_mail_not_sent(self):
        self.assertFalse(len(mail.outbox))

    def get_body(self, issues):
        issues_data = []
        for issue in issues:
            consumer = u'Потребитель: {}'.format(issue.get_consumer_name())
            issue_link = u'Ссылка: https://grantushka.passportdev-python.yandex-team.ru/grants/issue/{}/'.format(issue.pk)
            issues_data.append('\n'.join([consumer, issue_link]))

        return u'Ваши заявки:\n{}'.format('\n---\n'.join(issues_data))

    def test_ok(self):
        self.setup_bitbucket_last_commits_info()
        data = {
            'task': 'TASK',
            'task_id': 1,
            'ticket_id': 2,
            'branch': 'stable',
            'raw_branch': 'hotfix',
            'project': 'project_name',
            'old_status': 'installing',
            'new_status': 'done',
            'modifier': 'modifier_login',
            'modifier_id': 1,
            'author': 'author_login',
            'comment': 'comment',
            'ticket_subscribers': ['login1', 'login2'],
            'ticket_mailcc': 'mail1@yandex-team.ru,mail2@yandex-team.ru',
            'packages': [
                {
                    'package': 'yandex-blackbox-by-client-grants',
                    'version': '1.0',
                    'prev_version': '0.9',
                },
            ],
            'ticket_tasks_total': 1,
            'ticket_tasks_finished': 1,
        }
        issue1 = Issue.objects.get(pk=9)
        issue2 = Issue.objects.get(pk=10)
        response = self.make_request(data)
        self.assert_ok_response(response)
        self.assert_mail_sent(
            4,
            'blackbox_by_client',
            ['test1@yandex-team.ru', 'test@test.com', 'test-test@test.com', 'test2@yandex-team.ru'],
            [
                self.get_body([issue1]),
                self.get_body([issue1, issue2]),
                self.get_body([issue2]),
                self.get_body([issue2]),
            ],
        )

    def test_no_issues(self):
        self.setup_bitbucket_last_commits_info()
        data = {
            'branch': 'stable',
            'raw_branch': 'hotfix',
            'project': 'project_name',
            'author': 'author_login',
            'comment': 'comment',
            'packages': [
                {
                    'package': 'yandex-blackbox-grants',
                    'version': '1.0',
                    'prev_version': '0.9',
                },
            ],
            'ticket_tasks_total': 2,
            'ticket_tasks_finished': 2,
        }
        response = self.make_request(data)
        self.assert_ok_response(response)
        self.assert_mail_not_sent()

    def test_form_invalid(self):
        self.setup_bitbucket_last_commits_info()
        data = {
            'branch': 'stable',
            'raw_branch': 'hotfix',
            'project': 'project_name',
            'author': 'author_login',
            'comment': 'comment',
            'ticket_subscribers': ['login1', 'login2'],
            'ticket_mailcc': 'mail1@yandex-team.ru,mail2@yandex-team.ru',
            'ticket_tasks_total': 1,
        }
        response = self.make_request(data)
        self.assert_error_response(
            response,
            errors=['__all__: packages required', 'ticket_tasks_finished: Обязательное поле.'],
        )
        self.assert_mail_not_sent()

    def test_not_notify_admins(self):
        with self.settings(PASSPORT_TEAM_ADMIN=['test1']):
            self.setup_bitbucket_last_commits_info()
            data = {
                'branch': 'stable',
                'project': 'project_name',
                'packages': [
                    {
                        'package': 'yandex-blackbox-by-client-grants',
                        'version': '1.0',
                        'prev_version': '0.9',
                    },
                ],
                'ticket_tasks_total': 2,
                'ticket_tasks_finished': 2,
            }
            issue1 = Issue.objects.get(pk=9)
            issue2 = Issue.objects.get(pk=10)
            response = self.make_request(data)
            self.assert_ok_response(response)
            self.assert_mail_sent(
                3,
                'blackbox_by_client',
                ['test@test.com', 'test-test@test.com', 'test2@yandex-team.ru'],
                [
                    self.get_body([issue1, issue2]),
                    self.get_body([issue2]),
                    self.get_body([issue2]),
                ],
            )

    def test_task_not_finished(self):
        self.setup_bitbucket_last_commits_info()
        data = {
            'branch': 'stable',
            'packages': [
                {
                    'package': 'yandex-blackbox-by-client-grants',
                    'version': '1.0',
                    'prev_version': '0.9',
                },
            ],
            'ticket_tasks_total': 1,
            'ticket_tasks_finished': 2,
        }
        response = self.make_request(data)
        self.assert_ok_response(response, status_code=202)
        self.assert_mail_not_sent()

    def test_no_commits(self):
        self.requests.response.text = json.dumps({'values': []})
        data = {
            'branch': 'stable',
            'packages': [
                {
                    'package': 'yandex-blackbox-grants',
                    'version': '1.0',
                    'prev_version': '0.9',
                },
            ],
            'ticket_tasks_total': 2,
            'ticket_tasks_finished': 2,
        }
        response = self.make_request(data)
        self.assert_error_response(response, status_code=400)
        self.assert_mail_not_sent()
