# -*- coding: utf-8 -*-
import json
from copy import deepcopy
from urllib import urlencode
from django.test import TestCase
from django.test.client import Client as RequestClient

from passport_grants_configurator.apps.core.models import (
    Environment,
    Client,
    Consumer,
    Issue,
    Namespace,
)

TEST_CLIENT_NAME = 'Test Client Name'
TEST_CLIENT_ID = 3

TEST_CONSUMER_ID = 1
TEST_ENVIRONMENT_ID = 1
TEST_NAMESPACE_ID = 1


class ClientViewTestCase(TestCase):
    fixtures = ['default.json']
    url = '/grants/client/'
    maxDiff = None

    def setUp(self):
        self.request_client = RequestClient()
        self.data = {
            'name': TEST_CLIENT_NAME,
            'client_id': TEST_CLIENT_ID,
            'environment': TEST_ENVIRONMENT_ID,
            'namespace': TEST_NAMESPACE_ID,
        }

    def base_response(self):
        return {
            'client_pk': TEST_CLIENT_ID,
            'success': True,
        }

    def make_post_request(self, data=None):
        data = data or self.data
        return self.request_client.post(self.url, data)

    def assert_response(self, resp, expected_resp=None):
        expected_resp = expected_resp or self.base_response()
        self.assertItemsEqual(json.loads(resp.content), expected_resp)

    def make_delete_request(self, data):
        return self.request_client.delete(
            self.url,
            data=urlencode(data),
            content_type='application/x-www-form-urlencoded',
        )

    def test_add_ok(self):
        response = self.make_post_request()
        self.assert_response(response)

    def test_add_already_exists_without_consumer_editable(self):
        data = deepcopy(self.data)
        data.update(
            environment=Environment.objects.get(pk=TEST_ENVIRONMENT_ID),
            namespace=Namespace.objects.get(pk=TEST_NAMESPACE_ID),
        )
        client = Client.objects.create(**data)
        response = self.make_post_request()
        expected_response = {
            'success': False,
            'client_id': client.client_id,
            'name': client.name,
            'client_pk': client.id,
            'client_editable': True,
        }
        self.assert_response(resp=response, expected_resp=expected_response)

    def test_add_already_exists_without_consumer_not_editable(self):
        data = deepcopy(self.data)
        data.update(
            environment=Environment.objects.get(pk=TEST_ENVIRONMENT_ID),
            namespace=Namespace.objects.get(pk=TEST_NAMESPACE_ID),
        )
        client = Client.objects.create(**data)
        Issue.objects.get(pk=1).clients.add(client)
        response = self.make_post_request()
        expected_response = {
            'success': False,
            'client_id': client.client_id,
            'name': client.name,
            'client_pk': client.id,
            'client_editable': False,
        }
        self.assert_response(resp=response, expected_resp=expected_response)

    def test_add_already_exists_with_consumer_error(self):
        consumer = Consumer.objects.get(pk=TEST_CONSUMER_ID)
        data = deepcopy(self.data)
        data.update(
            environment=Environment.objects.get(pk=TEST_ENVIRONMENT_ID),
            consumer=consumer,
            namespace=Namespace.objects.get(pk=TEST_NAMESPACE_ID),
        )
        client = Client.objects.create(**data)
        response = self.make_post_request()
        expected_response = {
            'success': False,
            'errors': {
                '__all__': [
                    u'ClientID: %s уже привязан к потребителю %s' % (client.client_id, consumer.name),
                    u'Client с таким Client id,Namespace и Environment уже существует.',
                ],
            },
        }
        self.assert_response(resp=response, expected_resp=expected_response)

    def test_delete_ok(self):
        data = deepcopy(self.data)
        data.update(
            environment=Environment.objects.get(pk=TEST_ENVIRONMENT_ID),
            namespace=Namespace.objects.get(pk=TEST_NAMESPACE_ID),
        )
        client = Client.objects.create(**data)
        client_pk = client.id
        resp = self.make_delete_request(dict(client_pk=client_pk))
        self.assert_response(resp=resp, expected_resp=dict(success=True))
        with self.assertRaises(Client.DoesNotExist):
            Client.objects.get(id=client_pk)

    def test_delete_non_exist_ok(self):
        resp = self.make_delete_request(dict(client_pk=2))
        self.assert_response(resp, expected_resp=dict(success=True))
