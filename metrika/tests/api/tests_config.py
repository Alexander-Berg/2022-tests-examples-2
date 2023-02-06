import urllib.parse

import django.core.exceptions as dce

import metrika.admin.python.bishop.frontend.bishop.models as bp_models

import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas
import metrika.admin.python.bishop.frontend.tests.helper as tests_helper
import metrika.admin.python.bishop.frontend.tests.api.schemas.config as config_schema

from parameterized import parameterized


PARAMS_FOR_PARAMETERIZED = [
    (
        {
            'program': 'apid',
        },
        {19, 20}
    ),
    (
        {
            'environment': 'root.vault_test',
        },
        {36, 37, 38}
    ),
    (
        {
            'program': 'vault_test',
            'environment': 'root.vault_test',
        },
        {36}
    ),
    (
        {
            'hexdigest': '0bbae001ec2ede954119edbd1bdea757',
            'program': 'vault_test',
        },
        {36}
    ),
    (
        {
            'use_vault': 'true',
            'program': 'vault_test',
        },
        {36}
    ),
]


class TestGet(tests_helper.BishopApiTestCase):
    def test_list_no_required_params(self):
        response = self.client.get('/api/v3/configs')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate(),
        )

    @parameterized.expand(PARAMS_FOR_PARAMETERIZED)
    def test_list(self, query, ids):
        response = self.client.get('/api/v3/configs', query)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(
            config_schema.ConfigListSchema(data).validate(),
        )

        self.assertTrue(data['result'])
        self.assertEqual(len(data['data']), len(ids))
        self.assertEqual(len(data['errors']), 0)
        self.assertEqual(len(data['messages']), 0)

        uniq_ids = set(x['id'] for x in data['data'])
        self.assertEqual(uniq_ids, ids)

    def test_list_is_empty(self):
        response = self.client.get('/api/r3/configs?program=this_program_does_not_exist')
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate(),
        )

    def test_normal(self):
        config_id = 36
        config = bp_models.Config.objects\
            .select_related('program')\
            .select_related('environment')\
            .select_related('template')\
            .get(pk=config_id)

        self.assertTrue(
            bp_models.Config.objects.filter(pk=config_id).exists(),
        )

        response = self.client.get(f'/api/v3/configs/{config_id}')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(
            config_schema.ConfigSchema(data).validate()
        )
        self.assertTrue(data['result'])

        self.assertEqual(data['data']['program'], config.program.name)
        self.assertEqual(data['data']['environment'], config.environment.name)
        self.assertEqual(data['data']['template'], config.template.name)

        for name in ['id', 'hexdigest', 'active', 'use_vault', 'use_hosts', 'use_networks']:
            self.assertEqual(data['data'][name], getattr(config, name))

    def test_with_text(self):
        config_id = 36
        bp_models.Config.objects\
            .select_related('program')\
            .select_related('environment')\
            .select_related('template')\
            .get(pk=config_id)

        self.assertTrue(
            bp_models.Config.objects.filter(pk=config_id).exists(),
        )

        response = self.client.get(f'/api/v3/configs/{config_id}?with_text=True')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(
            config_schema.ConfigWithTextSchema(data).validate()
        )
        self.assertTrue(data['result'])
        self.assertTrue(data['data'].get('text', False))

    def test_missing(self):
        config_id = 100500
        response = self.client.get(f'/api/v3/configs/{config_id}')

        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Config.objects.get(pk=config_id)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate(),
        )


class TestDelete(tests_helper.BishopApiTestCase):
    def test_normal(self):
        config_id = 36

        self.assertTrue(
            bp_models.Config.objects.filter(pk=config_id).exists(),
        )

        response = self.client.delete(f'/api/v3/configs/{config_id}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(response.json()).validate()
        )
        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Config.objects.get(pk=config_id)

    def test_missing(self):
        config_id = 100500

        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Config.objects.get(pk=config_id)

        response = self.client.delete(f'/api/v3/configs/{config_id}')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    @parameterized.expand(PARAMS_FOR_PARAMETERIZED)
    def test_list(self, query, ids):
        params = urllib.parse.urlencode(query)

        url = f'/api/v3/configs?{params}'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(response.json()).validate()
        )

        self.assertTrue(data['result'])
        self.assertEqual(len(data['data']), 0)
        self.assertEqual(len(data['errors']), 0)
        self.assertEqual(len(data['messages']), len(ids))

        for pk in ids:
            with self.assertRaises(dce.ObjectDoesNotExist):
                bp_models.Config.objects.get(pk=pk)

    def test_list_no_required_params(self):
        response = self.client.delete('/api/v3/configs')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate(),
        )
