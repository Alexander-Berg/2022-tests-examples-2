import json
import copy

import django.core.exceptions as dce

import metrika.admin.python.bishop.frontend.tests.helper as tests_helper
import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas
import metrika.admin.python.bishop.frontend.tests.api.schemas.program as program_schema

import metrika.admin.python.bishop.frontend.bishop.models as bp_models


class TestCreate(tests_helper.BishopApiTestCase):
    valid_post_data = {
        'name': 'prosto_program',
        'template': 'unused.txt',
    }

    def test_normal(self):
        post_data = json.dumps(self.valid_post_data)
        response = self.client.post(
            '/api/v3/programs',
            post_data,
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )
        self.assertTrue(
            program_schema.ProgramSchema(data).validate()
        )
        count = bp_models.Program.objects.filter(
            name=self.valid_post_data['name'],
        ).count()
        self.assertEqual(count, 1)

    def test_duplicate(self):
        post_data = json.dumps(self.valid_post_data)
        response = self.client.post(
            '/api/v3/programs',
            post_data,
            content_type='application/json',
        )
        response = self.client.post(
            '/api/v3/programs',
            post_data,
            content_type='application/json',
        )
        data = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )
        count = bp_models.Program.objects.filter(
            name=self.valid_post_data['name'],
        ).count()
        self.assertEqual(count, 1)

    def test_missing_template(self):
        post_data = copy.deepcopy(self.valid_post_data)
        post_data['template'] = 'template_does_not_exist.xml'
        post_data = json.dumps(post_data)
        response = self.client.post(
            '/api/v3/programs',
            post_data,
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate(),
        )
        count = bp_models.Program.objects.filter(
            name=self.valid_post_data['name'],
        ).count()
        self.assertEqual(count, 0)

    def test_missing_parameter_name(self):
        post_data = copy.deepcopy(self.valid_post_data)
        del post_data['name']
        post_data = json.dumps(post_data)
        response = self.client.post(
            '/api/v3/programs',
            post_data,
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate(),
        )

    def test_missing_parameter_template(self):
        post_data = copy.deepcopy(self.valid_post_data)
        del post_data['template']
        post_data = json.dumps(post_data)
        response = self.client.post(
            '/api/v3/programs',
            post_data,
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate(),
        )


class TestGet(tests_helper.BishopApiTestCase):
    def test_list(self):
        programs_count = bp_models.Program.objects.count()
        response = self.client.get('/api/v3/programs')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(
            program_schema.ProgramListSchema(data).validate(),
        )

        self.assertTrue(data['result'])
        self.assertEqual(len(data['data']), programs_count)
        self.assertEqual(len(data['errors']), 0)
        self.assertEqual(len(data['messages']), 0)

    def test_normal(self):
        program = bp_models.Program.objects.get(name='httpd')
        response = self.client.get('/api/v3/programs/httpd')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(
            program_schema.ProgramSchema(data).validate()
        )
        self.assertTrue(data['result'])
        self.assertEqual(data['data']['name'], program.name)

    def test_missing(self):
        response = self.client.get('/api/v3/programs/httpdx')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate(),
        )


class TestUpdate(tests_helper.BishopApiTestCase):
    valid_put_data = {
        'template': 'unused.txt',
    }

    def test_normal(self):
        program = bp_models.Program.objects.get(name='json_program')
        self.assertNotEqual(
            program.template.name,
            self.valid_put_data['template'],
        )
        put_data = json.dumps(self.valid_put_data)
        response = self.client.put(
            '/api/v3/programs/json_program',
            put_data,
            content_type='application/json',
        )
        program = bp_models.Program.objects.get(name='json_program')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )
        self.assertEqual(
            data['data']['template']['name'],
            self.valid_put_data['template'],
        )
        self.assertEqual(
            program.template.name,
            self.valid_put_data['template'],
        )

    def test_missing_template_paramter(self):
        put_data = copy.deepcopy(self.valid_put_data)
        del put_data['template']
        put_data = json.dumps(put_data)

        response = self.client.put(
            '/api/v3/programs/json_program',
            put_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    def test_missing_template(self):
        put_data = copy.deepcopy(self.valid_put_data)
        put_data['template'] = 'does_not_exist.xml'
        put_data = json.dumps(put_data)

        response = self.client.put(
            '/api/v3/programs/json_program',
            put_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    def test_template_used_in_includes(self):
        put_data = copy.deepcopy(self.valid_put_data)
        put_data['template'] = 'logger.xml'
        put_data = json.dumps(put_data)

        response = self.client.put(
            '/api/v3/programs/json_program',
            put_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    def test_missing_variables_in_attached_environments(self):
        template = bp_models.Template.objects.get(name='template.txt')
        template.text = '{{ variable_is_missing }}'
        template.save()
        put_data = json.dumps({
            'template': 'template.txt',
        })
        response = self.client.put(
            '/api/v3/programs/httpd',
            put_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )


class TestDelete(tests_helper.BishopApiTestCase):
    def test_normal(self):
        response = self.client.delete('/api/v3/programs/simple_program')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(response.json()).validate()
        )
        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Program.objects.get(name='simple_program')

    def test_missing(self):
        response = self.client.delete('/api/v3/programs/plaintext_programzz')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate(),
        )

    def test_has_configs(self):
        response = self.client.delete('/api/v3/programs/httpd')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )


class TestAttachEnvironment(tests_helper.BishopApiTestCase):
    def test_normal(self):
        response = self.client.post('/api/v3/programs/simple_program/environments/root.not_used', content_type='application/json',)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(response.json()).validate()
        )

    def test_with_auto_activation(self):
        program, env = 'simple_program', 'root.not_used_with_children.not_used'
        response = self.client.post(f'/api/v3/programs/{program}/environments/{env}', data={'auto_activation': True}, content_type='application/json',)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(response.json()).validate()
        )

        response = self.client.get('/api/v3/activation_requests', {
            'program': program,
            'environment': env,
            'status': 'deployed'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.data), 1)


class TestDetachEnvironment(tests_helper.BishopApiTestCase):
    def test_normal(self):
        response = self.client.delete('/api/v3/programs/apid/environments/root.programs.apid.production')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(response.json()).validate()
        )
