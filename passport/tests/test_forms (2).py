# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from copy import deepcopy

from itertools import (
    chain,
    combinations,
)

from django.test import TestCase
from mock import Mock, patch

from passport_grants_configurator.apps.core.exceptions import NetworkResolveError
from passport_grants_configurator.apps.core.forms import (
    ClientForm,
    ConsumerSuggestForm,
    CreateGrantForm,
    CreateIssueForm,
    GetGrantsListForm,
    NetworkSuggestForm,
    NotifyCreatorsForm,
    ReviewIssueForm,
    SubmitIssueForm,
    ValidateNetworkForm,
)
from passport_grants_configurator.apps.core.models import (
    Client,
    Consumer,
    Email,
    Environment,
    Issue,
    Namespace,
)

TEST_COMMENT = 'test comment'

TEST_CLIENT_NAME = 'Test Client Name'
TEST_CLIENT_ID = 1

TEST_CONSUMER_ID = 1
TEST_ENVIRONMENT_ID = 1
TEST_NAMESPACE_ID = 1


def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in xrange(len(s) + 1))


class GetGrantsListFormCase(TestCase):
    fixtures = ['default.json']

    def setUp(self):
        self.consumer_1 = Consumer.objects.get(id=1)
        self.production = Environment.objects.get(id=1)
        self.passport = Namespace.objects.get(name='passport')
        self.issue_1 = Issue.objects.get(id=1)
        self.issue_1.status = Issue.DRAFT
        self.issue_1.save()

    def test_correct_issue_number(self):
        form = GetGrantsListForm({'issue': 1})
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data, {
            'consumer': None,
            'issue': self.issue_1,
            'namespace': self.passport,
        })

    def test_correct_consumer_environment(self):
        form = GetGrantsListForm({'consumer': 1, 'environment': 1})
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data, {
            'consumer': self.consumer_1,
            'issue': None,
            'namespace': self.passport,
        })

    def test_correct_namespace(self):
        form = GetGrantsListForm({'namespace': 1})
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data, {
            'consumer': None,
            'issue': None,
            'namespace': self.passport,
        })

    def test_empty_params(self):
        form = GetGrantsListForm({})
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {
            u'__all__': [u'Должно быть передано хотя бы одно из полей issue, consumer_name, namespace']
        })

    def test_consumer_environment_with_redundant_parameters(self):
        form = GetGrantsListForm({'consumer': 1, 'environment': 1, 'namespace': 1})
        self.assertEqual(form.is_valid(), False)

    def test_bad_namespace(self):
        form = GetGrantsListForm({'namespace': 100500})

        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors,
            {
                'namespace': [u'Выберите корректный вариант. Вашего варианта нет среди допустимых значений.'],
                '__all__': [u'Должно быть передано хотя бы одно из полей issue, consumer_name, namespace']
            }
        )


class CreateGrantCase(TestCase):
    fixtures = ['default.json']

    def setUp(self):
        self.data = {
            'grant_name': 'new grant',
            'grant_description': 'a new grant',
            'grant_namespace': 1,
            'name': 'new action',
            'description': 'a new action',
        }

    def test_correct_data(self):
        form = CreateGrantForm(self.data)
        self.assertEqual(form.is_valid(), True)

    def test_empty_names_and_descriptions__error(self):
        self.data.update(
            name='        ',
            description=' ',
            grant_name='\t',
        )
        form = CreateGrantForm(self.data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors,
            {
                'name': [u'Введите хотя бы один непустой символ'],
                'description': [u'Введите хотя бы один непустой символ'],
                'grant_name': [u'Введите хотя бы один непустой символ'],
            }
        )

    def test_grant_name_is_so_long(self):
        self.data['grant_name'] = 'ten chars ' * 10
        form = CreateGrantForm(self.data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors,
            {'grant_name': ['Убедитесь, что это значение содержит не более 64 символов (сейчас 100).']}
        )

    def test_adding_new_action_to_existing_grant(self):
        self.data['grant_name'] = 'password'
        form = CreateGrantForm(self.data)
        self.assertEqual(form.is_valid(), True)

    def test_no_grant_name(self):
        self.data.pop('grant_name')
        form = CreateGrantForm(self.data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {'grant_name': ['Обязательное поле.']})

    def test_no_grant_description(self):
        self.data.pop('grant_description')
        form = CreateGrantForm(self.data)
        self.assertEqual(form.is_valid(), True)

    def test_no_namespace(self):
        self.data.pop('grant_namespace')
        form = CreateGrantForm(self.data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {'grant_namespace': ['Обязательное поле.']})

    def test_nonexistent_namespace(self):
        self.data['grant_namespace'] = 100500
        form = CreateGrantForm(self.data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors,
            {'grant_namespace': ['Выберите корректный вариант. Вашего варианта нет среди допустимых значений.']},
        )

    def test_no_action_name(self):
        self.data.pop('name')
        form = CreateGrantForm(self.data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {'name': ['Обязательное поле.']})

    def test_attempt_to_create_duplicate_action(self):
        self.data.update({
            'grant_name': 'password',
            'name': 'validate',
        })
        form = CreateGrantForm(self.data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {'__all__': ['Грант "password.validate" уже существует']})

    def test_no_action_description(self):
        self.data.pop('description')
        form = CreateGrantForm(self.data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {'description': ['Обязательное поле.']})


class ValidateNetworkFormCase(TestCase):
    def test_old_conductor_macro(self):
        network_keyword = '_C_PASSPORT_'
        form = ValidateNetworkForm({'network': network_keyword})
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {'network': ['Old conductor macro used %s' % network_keyword]})

    def test_on_resolve_error(self):
        get_type_patch = patch(
            'passport_grants_configurator.apps.core.forms.NetworkResolver.get_type_and_children',
            Mock(side_effect=NetworkResolveError),
        )

        with get_type_patch:
            form = ValidateNetworkForm({'network': '127.0.0.1/24'})
            self.assertEqual(form.is_valid(), False)


class TestCreateIssueForm(TestCase):
    fixtures = ['default.json']

    def setUp(self):
        self.consumer_1 = Consumer.objects.get(id=1)
        self.production = Environment.objects.get(id=1)
        self.issue_1 = Issue.objects.get(id=1)

    def test_empty_form(self):
        create_issue_form = CreateIssueForm({})
        self.assertEqual(create_issue_form.is_valid(), True)
        self.assertEqual(create_issue_form.cleaned_data, {
            'consumer': None,
            'environment': None,
            'issue': None
        })

    def test_form_for_html_template_template_with_predefined_consumer(self):
        create_issue_form = CreateIssueForm({'consumer': 1, 'environment': 1})
        self.assertEqual(create_issue_form.is_valid(), True)
        self.assertEqual(create_issue_form.cleaned_data, {
            'consumer': self.consumer_1,
            'environment': self.production,
            'issue': None,
        })

    def test_form_for_html_template_template_with_predefined_issue_instance(self):
        create_issue_form = CreateIssueForm({'issue': 1})
        self.assertEqual(create_issue_form.is_valid(), True)
        self.assertEqual(create_issue_form.cleaned_data, {
            'consumer': None,
            'environment': None,
            'issue': self.issue_1,
        })

    def test_invalid_fields_set(self):
        invalid_sets = (
            ({'consumer': 1}, {'__all__': ['Поля consumer и environment должны передаваться вместе']}),
            ({'environment': 1}, {'__all__': ['Поля consumer и environment должны передаваться вместе']}),
            (
                {'consumer': 1, 'environment': 1, 'issue': 1},
                {'__all__': ['issue должно быть единственным переданным полем']}
            ),
            ({'consumer': 1, 'issue': 1}, {'__all__': ['issue должно быть единственным переданным полем']}),
            ({'environment': 1, 'issue': 1}, {'__all__': ['issue должно быть единственным переданным полем']}),
        )
        for arguments, errors in invalid_sets:
            create_issue_form = CreateIssueForm(arguments)
            self.assertEqual(create_issue_form.is_valid(), False)
            self.assertEqual(create_issue_form.errors, errors)


class TestSubmitIssueForm(TestCase):
    fixtures = ['default.json']

    # TODO: тест на успешную проверку формы

    def test_submit_second_issue_to_create_consumer_with_the_same_name(self):
        form = SubmitIssueForm({
            'type': 'C',
            'consumer_name': 'new_consumer',
            'namespace': 1,
            'environments': [1],
            'comment': TEST_COMMENT,
        })
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {u'__all__': ['Заявка на создание потребителя с таким именем уже существует']})

    def test_submit_issue_with_consumer_name_that_already_exists_among_consumers(self):
        for _type in [Issue.TO_CREATE, Issue.TO_CLONE]:
            form = SubmitIssueForm({
                'type': _type,
                'consumer_name': 'some_consumer',
                'namespace': 1,
                'environments': [1],
                'comment': TEST_COMMENT,
            })
            self.assertEqual(form.is_valid(), False)
            self.assertEqual(form.errors, {u'__all__': ['Потребитель с таким именем уже существует']})

    def test_issue_that_defines_name_and_new_name(self):
        form = SubmitIssueForm({
            'type': 'C',
            'consumer_name': 'new_consumer_2',
            'consumer_name_new': 'new_name',
            'namespace': 1,
            'environments': [1],
            'comment': TEST_COMMENT,
        })
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {u'__all__': ['Невозможно переименовать еще не созданного потребителя']})

    def test_attempt_to_submit_not_project_environment(self):
        environment = Environment.objects.create(name='other', type='another', priority=100)
        form = SubmitIssueForm({
            'type': 'C',
            'consumer_name': 'new_consumer_2',
            'namespace': 1,
            'environments': [1, environment.id],
            'comment': TEST_COMMENT,
        })
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {
            '__all__': ['Окружения: "other another" не входят в окружения проекта passport']
        })

    def test_attempt_to_submit_non_expiration_issue_with_expiration_date(self):
        form = SubmitIssueForm({
            'type': 'C',
            'consumer_name': 'new_consumer_2',
            'environments': [1],
            'expiration': '14.03.2014',
            'namespace': 1,
            'comment': TEST_COMMENT,
        })
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {
            '__all__': ['Поле expiration должно передаваться только для заявок на временные гранты']
        })

    def test_attempt_to_create_grant_expiration_issue_with_no_expiration_date_field(self):
        form = SubmitIssueForm({
            'type': 'E',
            'consumer': 1,
            'environments': [1],
            'namespace': 1,
            'comment': TEST_COMMENT,
        })
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {
            '__all__': ['Необходимо указать дату истечения срока действия грантов']
        })

    def test_no_comment_param__error(self):
        form = SubmitIssueForm({
            'type': 'E',
            'consumer': 1,
            'environments': [1],
            'expiration': '14.03.2014',
            'namespace': 1,
        })
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors,
            {
                'comment': [u'Обязательное поле.']
            }
        )

    def test_non_exist_clients(self):
        form = SubmitIssueForm({
            'type': 'E',
            'consumer': 1,
            'environments': [1],
            'expiration': '14.03.2014',
            'namespace': 1,
            'comment': TEST_COMMENT,
            'clients': [33],
        })
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form.errors,
            {
                'clients': [u'Выберите корректный вариант. %s нет среди допустимых значений.' % 33],
            },
        )

    def test_create_consumer_name_valid(self):
        form = SubmitIssueForm({
            'type': 'C',
            'consumer_name': "a-zA-Z0-9-_.;/'@,:()",
            'environments': [1],
            'namespace': 1,
            'comment': TEST_COMMENT,
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.data['consumer_name'], "a-zA-Z0-9-_.;/'@,:()")

    def test_create_consumer_name_invalid(self):
        form = SubmitIssueForm({
            'type': 'C',
            'consumer_name': "test spaces",
            'environments': [1],
            'namespace': 1,
            'comment': TEST_COMMENT,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                '__all__': [u'Поле consumer_name содержит запрещенные символы'],
            },
        )

    def test_create_consumer_name_empty(self):
        form = SubmitIssueForm({
            'type': 'C',
            'consumer_name': " \t",
            'environments': [1],
            'namespace': 1,
            'comment': TEST_COMMENT,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                '__all__': [u'Не передано обязательное поле consumer_name'],
            },
        )

    def test_edit_consumer_name_valid(self):
        form = SubmitIssueForm({
            'type': 'E',
            'consumer': 1,
            'consumer_name_new': "a-zA-Z0-9-_.;/'@,:()",
            'environments': [1],
            'namespace': 1,
            'comment': TEST_COMMENT,
            'expiration': '14.03.2014',
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.data['consumer_name_new'], "a-zA-Z0-9-_.;/'@,:()")

    def test_edit_consumer_name_invalid(self):
        form = SubmitIssueForm({
            'type': 'E',
            'consumer': 1,
            'consumer_name_new': "test!!test",
            'environments': [1],
            'namespace': 1,
            'comment': TEST_COMMENT,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                '__all__': [u'Поле consumer_name содержит запрещенные символы'],
            },
        )

    def test_create_consumer_with_client_required_no_client__invalid(self):
        env_testing = Environment.objects.get(pk=2)
        bb_namespace = Namespace.objects.get(name='blackbox_by_client')
        form = SubmitIssueForm({
            'type': 'C',
            'consumer_name': "BB_consumer",
            'environments': [env_testing.id],
            'namespace': bb_namespace.id,
            'comment': TEST_COMMENT,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                '__all__': ['ClientID: обязательное поле для {} всех окружений'.format(bb_namespace.name)],
            },
        )

    def test_edit_consumer_with_client_required_no_client__invalid(self):
        env_testing = Environment.objects.get(pk=2)
        env_development = Environment.objects.get(pk=3)
        bb_namespace = Namespace.objects.get(name='blackbox_by_client')
        form = SubmitIssueForm({
            'type': 'M',
            'consumer': 10,
            'consumer_name_new': "BB_consumer_new",
            'environments': [env_testing.id, env_development.id],
            'namespace': bb_namespace.id,
            'clients': [2],
            'comment': TEST_COMMENT,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                '__all__': ['ClientID: обязательное поле для {} всех окружений'.format(bb_namespace.name)],
            },
        )

    def test_create_consumer_client_not_required_no_client__valid(self):
        env_testing = Environment.objects.get(pk=2)
        passport_namespace = Namespace.objects.get(name='passport')
        form = SubmitIssueForm({
            'type': 'C',
            'consumer_name': "Pssp_consumer",
            'environments': [env_testing.id],
            'namespace': passport_namespace.id,
            'comment': TEST_COMMENT,
        })
        self.assertTrue(form.is_valid())

    def test_edit_consumer_client_not_required_no_client__valid(self):
        env_testing = Environment.objects.get(pk=2)
        env_development = Environment.objects.get(pk=3)
        passport_namespace = Namespace.objects.get(name='passport')
        form = SubmitIssueForm({
            'type': 'M',
            'consumer': 11,
            'consumer_name_new': "Pssp_consumer_new",
            'environments': [env_testing.id, env_development.id],
            'namespace': passport_namespace.id,
            'clients': [3],
            'comment': TEST_COMMENT,
        })
        self.assertTrue(form.is_valid())

    def test_create_consumer_with_client_required__valid(self):
        env_testing = Environment.objects.get(pk=2)
        bb_namespace = Namespace.objects.get(name='blackbox_by_client')
        client_with_no_consumer = Client.objects.get(pk=2)
        form = SubmitIssueForm({
            'type': 'C',
            'consumer_name': "BB_consumer",
            'environments': [env_testing.id],
            'namespace': bb_namespace.id,
            'clients': [client_with_no_consumer.id],
            'comment': TEST_COMMENT,
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['namespace'], bb_namespace)
        self.assertSequenceEqual(form.cleaned_data['clients'], [client_with_no_consumer])

    def test_edit_consumer_with_client_required__valid(self):
        env_testing = Environment.objects.get(pk=2)
        bb_namespace = Namespace.objects.get(name='blackbox_by_client')
        client_with_no_consumer = Client.objects.get(pk=2)
        form = SubmitIssueForm({
            'type': 'M',
            'consumer': 10,
            'environments': [env_testing.id],
            'namespace': bb_namespace.id,
            'clients': [client_with_no_consumer.id],
            'comment': TEST_COMMENT,
        })

        self.assertTrue(form.is_valid())
        self.assertSequenceEqual(form.cleaned_data['environments'], [env_testing])
        self.assertSequenceEqual(form.cleaned_data['clients'], [client_with_no_consumer])

    def test_client_already_used__invalid(self):
        env_production = Environment.objects.get(pk=1)
        passport_namespace = Namespace.objects.get(name='passport')
        client_with_consumer = Client.objects.get(pk=4)
        client_consumer = Consumer.objects.get(pk=11)
        form = SubmitIssueForm({
            'type': 'M',
            'consumer': 1,
            'consumer_name_new': 'Pssp_consumer_new',
            'environments': [env_production.id],
            'namespace': passport_namespace.id,
            'clients': [client_with_consumer.id],
            'comment': TEST_COMMENT,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                '__all__': ['ClientID: %s уже привязан к потребителю %s' % (
                    client_with_consumer.client_id, client_consumer.name,
                )],
            },
        )

    def test_with_valid_emails(self):
        valid_emails = ['test1', 'test1@yandex-team.ru', 'test1@yamoney.ru']
        env_testing = Environment.objects.get(pk=2)
        bb_namespace = Namespace.objects.get(name='blackbox_by_client')
        client_with_no_consumer = Client.objects.get(pk=2)
        for email in valid_emails:
            address = email
            if len(email.split('@')) < 2:
                address = '{}@yandex-team.ru'.format(email)
            expected_email = Email.objects.get(address=address)
            form = SubmitIssueForm({
                'type': 'M',
                'consumer': 10,
                'environments': [env_testing.id],
                'namespace': bb_namespace.id,
                'clients': [client_with_no_consumer.id],
                'comment': TEST_COMMENT,
                'emails': [email],
            })
            self.assertTrue(form.is_valid())
            self.assertSequenceEqual(form.cleaned_data['emails'], [expected_email])

    def test_with_empty_emails(self):
        empty_emails = ['', None]
        env_testing = Environment.objects.get(pk=2)
        bb_namespace = Namespace.objects.get(name='blackbox_by_client')
        client_with_no_consumer = Client.objects.get(pk=2)
        for email in empty_emails:
            form = SubmitIssueForm({
                'type': 'M',
                'consumer': 10,
                'environments': [env_testing.id],
                'namespace': bb_namespace.id,
                'clients': [client_with_no_consumer.id],
                'comment': TEST_COMMENT,
                'emails': [email],
            })
            self.assertTrue(form.is_valid())
            self.assertSequenceEqual(form.cleaned_data['emails'], [])

    def test_emails_domain_invalid(self):
        invalid_emails = ['alice@', 'alice@alice.com']
        env_testing = Environment.objects.get(pk=2)
        bb_namespace = Namespace.objects.get(name='blackbox_by_client')
        client_with_no_consumer = Client.objects.get(pk=2)
        for email in invalid_emails:
            form = SubmitIssueForm({
                'type': 'M',
                'consumer': 10,
                'environments': [env_testing.id],
                'namespace': bb_namespace.id,
                'clients': [client_with_no_consumer.id],
                'comment': TEST_COMMENT,
                'emails': [email],
            })

            self.assertFalse(form.is_valid())
            self.assertEqual(
                form.errors,
                {
                    '__all__': ['emails: Введите валидный адрес с доменом yandex-team или логин пользователя'],
                },
            )


class TestClientForm(TestCase):
    fixtures = ['default.json']

    def setUp(self):
        self.data = {
            'name': TEST_CLIENT_NAME,
            'client_id': TEST_CLIENT_ID,
            'environment': TEST_ENVIRONMENT_ID,
            'namespace': TEST_NAMESPACE_ID,
        }

    def test_add_client_ok(self):
        form = ClientForm(data=self.data)
        expected_cleaned_data = deepcopy(self.data)
        expected_cleaned_data.update(
            environment=Environment.objects.get(pk=self.data['environment']),
            consumer=None,
            namespace=Namespace.objects.get(pk=self.data['namespace']),
        )
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data, expected_cleaned_data)

    def test_add_duplicate_client_error(self):
        data = deepcopy(self.data)
        data.update(
            environment=Environment.objects.get(pk=self.data['environment']),
            namespace=Namespace.objects.get(pk=self.data['namespace']),
        )
        client = Client.objects.create(**data)
        form = ClientForm(data=self.data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {
            '__all__': [u'Client с таким Client id,Namespace и Environment уже существует.'],
        })
        expected_cleaned_data = deepcopy(data)
        expected_cleaned_data.update(
            existing_client=client,
            consumer=None,
        )
        self.assertEqual(form.cleaned_data, expected_cleaned_data)

    def test_similar_clients_with_different_namespaces(self):
        """
        Проверим, что можно создавать клиентов, отличающихся только namespace
        """
        data_1 = {
            'name': 'Test client',
            'client_id': 111,
            'environment': Environment.objects.get(pk=TEST_ENVIRONMENT_ID),
            'namespace': Namespace.objects.get(name='blackbox_by_client'),
        }
        data_2 = deepcopy(data_1)
        data_2.update(
            namespace=TEST_NAMESPACE_ID,
            environment=TEST_ENVIRONMENT_ID,
        )
        expected_cleaned_data = deepcopy(data_1)
        expected_cleaned_data.update(
            consumer=None,
            namespace=Namespace.objects.get(pk=TEST_NAMESPACE_ID),
        )
        Client.objects.create(**data_1)
        form = ClientForm(data=data_2)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, expected_cleaned_data)

    def test_add_client_already_with_consumer_error(self):
        consumer = Consumer.objects.get(pk=TEST_CONSUMER_ID)
        data = deepcopy(self.data)
        data.update(
            environment=Environment.objects.get(pk=self.data['environment']),
            consumer=consumer,
            namespace=Namespace.objects.get(pk=self.data['namespace']),
        )
        client = Client.objects.create(**data)
        form = ClientForm(data=self.data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {
            '__all__': [
                u'ClientID: %s уже привязан к потребителю %s' % (client.client_id, consumer.name),
                u'Client с таким Client id,Namespace и Environment уже существует.',
            ],
        })

    def test_add_client_non_exist_environment(self):
        data = deepcopy(self.data)
        data.update(
            environment=100,
        )
        form = ClientForm(data=data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {
            'environment': [u'Выберите корректный вариант. Вашего варианта нет среди допустимых значений.'],
        })

    def test_add_client_invalid_client_id(self):
        for client_id in ['text client id', 4.4]:
            data = deepcopy(self.data)
            data.update(
                client_id=client_id,
            )
            form = ClientForm(data=data)
            self.assertEqual(form.is_valid(), False)
            self.assertEqual(form.errors, {
                'client_id': [u'Введите целое число.'],
            })

    def test_add_client_invalid_client_id_min(self):
        for client_id in [0, -100]:
            data = deepcopy(self.data)
            data.update(
                client_id=client_id,
            )
            form = ClientForm(data=data)
            self.assertEqual(form.is_valid(), False)
            self.assertEqual(form.errors, {
                'client_id': [u'Убедитесь, что это значение больше либо равно 1.'],
            })

    def test_add_client_cyrillic_name_error(self):
        data = deepcopy(self.data)
        data.update(
            name=u'Ёлки-иголки',
        )
        form = ClientForm(data=data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {
            'name': [u'Русские символы недопустимы'],
        })

    def test_add_client_with_consumer_ok(self):
        data = deepcopy(self.data)
        data.update(consumer=TEST_CONSUMER_ID)
        form = ClientForm(data=data)
        expected_cleaned_form = deepcopy(self.data)
        expected_cleaned_form.update(
            consumer=Consumer.objects.get(pk=TEST_CONSUMER_ID),
            environment=Environment.objects.get(pk=self.data['environment']),
            namespace=Namespace.objects.get(pk=self.data['namespace']),
        )
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data, expected_cleaned_form)

    def test_add_client_missing_params_error(self):
        data = deepcopy(self.data)
        data.pop('client_id')
        form = ClientForm(data=data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors, {
            'client_id': [u'Обязательное поле.'],
        })


class TestReviewIssueForm(TestCase):
    fixtures = ['default.json']

    def setUp(self):
        self.data = {
            'issue': 8,
            'result': 'confirmed',
        }

    def test_issue_modify_approved(self):
        form = ReviewIssueForm(data=self.data)
        self.assertEqual(form.is_valid(), True)


class TestNetworkSuggestForm(TestCase):
    fixtures = ['default.json']

    def test_ok(self):
        form = NetworkSuggestForm(data={'keyword': 'dev'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['keyword'], 'dev')

    def test_rus(self):
        form = NetworkSuggestForm(data={'keyword': 'вум'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['keyword'], 'dev')

    def test_mixed(self):
        form = NetworkSuggestForm(data={'keyword': 'ВУv'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['keyword'], 'dev')

    def test_digits(self):
        form = NetworkSuggestForm(data={'keyword': '123'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['keyword'], '123')

    def test_invalid(self):
        form = NetworkSuggestForm(data={'keyword': '12'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {'keyword': ['Убедитесь, что это значение содержит не менее 3 символов (сейчас 2).']},
        )

    def test_empty(self):
        form = NetworkSuggestForm(data={'keyword': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {'keyword': ['Обязательное поле.']},
        )


class TestConsumerSuggestForm(TestCase):
    fixtures = ['default.json']

    def setUp(self):
        self.namespace_obj = Namespace.objects.get(id=1)

    def test_ok(self):
        data = {'keyword': '%abc_', 'namespace': 1}
        form = ConsumerSuggestForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, {'keyword': 'abc', 'namespace': self.namespace_obj})

    def test_namespace_invalid(self):
        data = {'keyword': 'abc', 'namespace': 100500}
        form = ConsumerSuggestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                'namespace': [u'Выберите корректный вариант. Вашего варианта нет среди допустимых значений.'],
            },
        )

    def test_keyword_too_long(self):
        data = {'keyword': 'abc' * 255, 'namespace': 1}
        form = ConsumerSuggestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                'keyword': [u'Убедитесь, что это значение содержит не более 250 символов (сейчас 765).'],
            },
        )

    def test_keyword_rus(self):
        data = {'keyword': 'фыр', 'namespace': 1}
        form = ConsumerSuggestForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, {'keyword': 'ash', 'namespace': self.namespace_obj})

    def test_empty(self):
        form = ConsumerSuggestForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                'keyword': ['Обязательное поле.'],
                'namespace': ['Обязательное поле.'],
            },
        )


class TestNotifyCreatorsForm(TestCase):
    maxDiff = None
    fixtures = ['default.json']

    def test_ok(self):
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
        form = NotifyCreatorsForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data,
            {
                'branch': 'stable',
                'project': 'blackbox_by_client',
                'ticket_tasks_total': 1,
                'ticket_tasks_finished': 1,
            },
        )

    def test_branch_invalid(self):
        branch = 'testing'
        data = {
            'branch': branch,
            'raw_branch': 'hotfix',
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
        form = NotifyCreatorsForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                'branch': ['Выберите корректный вариант. {} нет среди допустимых значений.'.format(branch)],
            },
        )

    def test_packages_empty(self):
        data = {
            'branch': 'stable',
            'raw_branch': 'hotfix',
            'project': 'project_name',
            'packages': [],
            'ticket_tasks_total': 1,
            'ticket_tasks_finished': 2,
        }
        form = NotifyCreatorsForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                u'__all__': [u'packages required'],
            },
        )

    def test_package_name_invalid(self):
        data = {
            'branch': 'stable',
            'raw_branch': 'hotfix',
            'project': 'project_name',
            'packages': [
                {
                    'package': 'yandex-blackbox-client-grants',
                    'version': '1.0',
                    'prev_version': '0.9',
                },
            ],
            'ticket_tasks_total': 1,
            'ticket_tasks_finished': 100,
        }
        form = NotifyCreatorsForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                '__all__': ['no project for package name: yandex-blackbox-client-grants'],
            },
        )

    def test_no_task_data(self):
        data = {
            'branch': 'stable',
            'raw_branch': 'hotfix',
            'project': 'project_name',
            'packages': [
                {
                    'package': 'yandex-blackbox-by-client-grants',
                    'version': '1.0',
                    'prev_version': '0.9',
                },
            ],
        }
        form = NotifyCreatorsForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                'ticket_tasks_total': ['Обязательное поле.'],
                'ticket_tasks_finished': ['Обязательное поле.'],
            },
        )
