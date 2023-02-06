import metrika.admin.python.bishop.frontend.bishop.models as bp_models

import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas
import metrika.admin.python.bishop.frontend.tests.helper as tests_helper
import metrika.admin.python.bishop.frontend.tests.api.schemas.activation_request as ar_schema

from parameterized import parameterized


class TestGet(tests_helper.BishopApiTestCase):
    def test_list(self):
        activation_requests_count = bp_models.ActivationRequest.objects.count()
        response = self.client.get('/api/v3/activation_requests')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(
            ar_schema.ActivationRequestListSchema(data).validate(),
        )

        self.assertTrue(data['result'])
        self.assertEqual(len(data['data']), activation_requests_count)
        self.assertEqual(len(data['errors']), 0)
        self.assertEqual(len(data['messages']), 0)
        self.assertEqual(data['data'], sorted(data['data'], key=lambda x: x['id'], reverse=True))

    @parameterized.expand([
        ('by_status', {'status': 'opened'}, {43, 44, 47}),
        ('by_id', {'id': '46,47,48'}, {46, 47, 48}),
        ('by_id_single', {'id': '46'}, {46}),
        ('by_program', {'program': 'yaml_program'}, {25, 26, 34, 35, 45, 46, 47, 48}),
        ('by_environment', {'environment': 'root.programs.yaml_program.testing'}, {25, 34, 45, 47}),
        ('by_program_and_status', {'status': 'deployed', 'program': 'unused_program'}, {33}),
        ('by_environment_and_status', {'status': 'opened', 'environment': 'root.programs.yaml_program.testing'}, {47}),
        ('by_program_and_environment', {'program': 'yaml_program', 'environment': 'root.programs.yaml_program.production'}, {26, 35, 46, 48})
    ])
    def test_filtered_list(self, _, query, ids):
        response = self.client.get('/api/v3/activation_requests', query)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(
            ar_schema.ActivationRequestListSchema(data).validate(),
        )

        self.assertTrue(data['result'])
        self.assertEqual(len(data['data']), len(ids))
        self.assertEqual(len(data['errors']), 0)
        self.assertEqual(len(data['messages']), 0)

        uniq_ids = set(x['id'] for x in data['data'])
        self.assertEqual(uniq_ids, ids)

    def test_filtered_missed(self):
        response = self.client.get('/api/v3/activation_requests?id=99999')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(
            tests_api_schemas.ListSchema(data).validate(),
        )

        self.assertTrue(data['result'])
        self.assertEqual(len(data['data']), 0)
        self.assertEqual(len(data['errors']), 0)
        self.assertEqual(len(data['messages']), 0)

    def test_normal(self):
        activation_request = bp_models.ActivationRequest.objects.get(pk=34)
        response = self.client.get('/api/v3/activation_requests/34')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(
            ar_schema.ActivationRequestSchema(data).validate()
        )
        self.assertTrue(data['result'])
        self.assertEqual(data['data']['program'], activation_request.config.program.name)
        self.assertEqual(data['data']['environment'], activation_request.config.environment.name)

    def test_missing(self):
        response = self.client.get('/api/v3/activation_requests/100500')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate(),
        )


class TestDeploy(tests_helper.BishopApiTestCase):
    def test_deploy(self):
        data = self.client.get('/api/v3/activation_requests?status=opened').json()

        self.assertTrue(len(data['data']) > 0)

        ar = data['data'][0]['id']

        response = self.client.post('/api/v3/activation_requests/%d' % ar)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(
            ar_schema.ActivationRequestDeploySchema(data).validate(),
        )

        self.assertTrue(data['result'])
        self.assertEqual(len(data['data']), 0)
        self.assertEqual(len(data['errors']), 0)
        self.assertEqual(len(data['messages']), 1)

        data = self.client.get('/api/v3/activation_requests/%d' % ar).json()
        self.assertEqual(data['data']['status'], "deployed")

    def test_deploy_deployed(self):
        data = self.client.get('/api/v3/activation_requests?status=deployed').json()

        self.assertTrue(len(data['data']) > 0)

        ar = data['data'][0]['id']

        response = self.client.post('/api/v3/activation_requests/%d' % ar)
        self.assertEqual(response.status_code, 400)
        data = response.json()

        self.assertTrue(
            ar_schema.ActivationRequestDeploySchema(data).validate(),
        )

        self.assertFalse(data['result'])
        self.assertEqual(len(data['data']), 0)
        self.assertEqual(len(data['errors']), 1)
        self.assertEqual(len(data['messages']), 0)

        data = self.client.get('/api/v3/activation_requests/%d' % ar).json()
        self.assertEqual(data['data']['status'], "deployed")

    def test_deploy_no_pk(self):
        response = self.client.post('/api/v3/activation_requests')
        self.assertEqual(response.status_code, 405)
        data = response.json()

        self.assertTrue(
            ar_schema.ActivationRequestDeploySchema(data).validate(),
        )

        self.assertFalse(data['result'])
        self.assertEqual(len(data['data']), 0)
        self.assertEqual(len(data['errors']), 1)
        self.assertEqual(len(data['messages']), 0)
