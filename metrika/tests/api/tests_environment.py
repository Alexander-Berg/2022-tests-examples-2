import json
import copy

import django.core.exceptions as dce

import metrika.admin.python.bishop.frontend.bishop.models as bp_models

import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas
import metrika.admin.python.bishop.frontend.tests.helper as tests_helper
import metrika.admin.python.bishop.frontend.tests.api.schemas.environment as environment_schema


class TestCreate(tests_helper.BishopApiTestCase):
    valid_post_data = {
        'name': 'prosto_environment',
        'parent': 'root',
    }

    def test_normal(self):
        post_data = self.valid_post_data
        response = self.client.post(
            '/api/v3/environments',
            json.dumps(post_data),
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )
        count = bp_models.Environment.objects.filter(
            name='root.prosto_environment',
        ).count()
        self.assertEqual(count, 1)

    def test_clone(self):
        post_data = copy.deepcopy(self.valid_post_data)
        post_data['clone_from'] = 'root.programs.httpd.production'

        response = self.client.post(
            '/api/v3/environments',
            json.dumps(post_data),
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )
        count = bp_models.Environment.objects.filter(
            name='root.prosto_environment',
        ).count()
        self.assertEqual(count, 1)

        environment = bp_models.Environment.objects.get(name=post_data['clone_from'])
        clone = bp_models.Environment.objects.get(name='root.prosto_environment')

        self.assertEqual(
            set([(v.name, v.value, v.type, v.is_link) for v in clone.variables]),
            set([(v.name, v.value, v.type, v.is_link) for v in environment.variables]),
        )

    def test_duplicate(self):
        post_data = json.dumps(self.valid_post_data)
        response = self.client.post(
            '/api/v3/environments',
            post_data,
            content_type='application/json',
        )
        response = self.client.post(
            '/api/v3/environments',
            post_data,
            content_type='application/json',
        )
        data = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )
        count = bp_models.Environment.objects.filter(
            name='root.prosto_environment',
        ).count()
        self.assertEqual(count, 1)

    def test_missing_parent(self):
        post_data = copy.deepcopy(self.valid_post_data)
        post_data['clone_from'] = 'hello'
        response = self.client.post(
            '/api/v3/environments',
            json.dumps(post_data),
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )

    def test_missing_clone_from(self):
        post_data = copy.deepcopy(self.valid_post_data)
        post_data['parent'] = 'hello'
        response = self.client.post(
            '/api/v3/environments',
            json.dumps(post_data),
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )

    def test_missing_name_parameter(self):
        post_data = copy.deepcopy(self.valid_post_data)
        del post_data['name']
        response = self.client.post(
            '/api/v3/environments',
            json.dumps(post_data),
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )

    def test_missing_parent_parameter(self):
        post_data = copy.deepcopy(self.valid_post_data)
        del post_data['name']
        response = self.client.post(
            '/api/v3/environments',
            json.dumps(post_data),
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )


class TestUpdate(tests_helper.BishopApiTestCase):
    def test_normal(self):
        response = self.client.put(
            '/api/v3/environments/root.defaults',
        )
        self.assertEqual(response.status_code, 405)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )


class TestGet(tests_helper.BishopApiTestCase):
    def test_list(self):
        environments_count = bp_models.Environment.objects.count()
        response = self.client.get(
            '/api/v3/environments',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(
            tests_api_schemas.ListSchema(data).validate(),
        )

        root_count = 0
        for environment in data['data']:
            if environment['is_root']:
                root_count += 1
                self.assertTrue(
                    environment_schema.SingleEnvironmentRootSchema(environment).validate(),
                )
            else:
                self.assertTrue(
                    environment_schema.SingleEnvironmentSchema(environment).validate(),
                )

        self.assertEqual(root_count, 1)
        self.assertTrue(data['result'])
        self.assertEqual(len(data['data']), environments_count)
        self.assertEqual(len(data['errors']), 0)
        self.assertEqual(len(data['messages']), 0)

    def test_normal(self):
        environment = bp_models.Environment.objects.get(
            name='root.defaults',
        )
        response = self.client.get(
            '/api/v3/environments/root.defaults',
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(
            environment_schema.EnvironmentSchema(data).validate()
        )
        self.assertTrue(data['result'])
        self.assertEqual(
            data['data']['name'],
            environment.name,
        )

    def test_missing(self):
        response = self.client.get(
            '/api/v3/environments/root.lala.not.exist',
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate(),
        )


class TestDelete(tests_helper.BishopApiTestCase):
    def test_normal(self):
        response = self.client.delete(
            '/api/v3/environments/root.not_used',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(response.json()).validate()
        )
        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Environment.objects.get(name='root.not_used')

    def test_missing(self):
        response = self.client.delete(
            '/api/v3/environments/there.is.no.this.environment',
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    def test_has_children(self):
        response = self.client.delete(
            '/api/v3/environments/root.not_used_with_children',
        )

        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    def test_has_attaches(self):
        url = '/api/v3/environments/root.programs.httpd.production'

        # should fail because of attachment + configs + links
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

        program = bp_models.Program.objects.get(name='httpd')
        environment = bp_models.Environment.objects.get(
            name='root.programs.httpd.production',
        )

        response = program.detach_environment(
            request=self._request,
            response=self._response,
            environment=environment,
        )
        self.assertTrue(response.result)

        # should fail because of configs + links
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

        for config in bp_models.Config.objects.filter(environment=environment):
            config.delete(
                self._request,
                self._response,
            )

        # should fail because of links
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

        for var in bp_models.Variable.objects.filter(link_environment=environment):
            var.convert_to_normal()

        # should be ok
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(response.json()).validate()
        )


class TestGetVariable(tests_helper.BishopApiTestCase):
    def test_normal_string(self):
        url = (
            '/api/v3/environments/root.not_used'
            '/variables/string_var'
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            environment_schema.StringVariableSchema(response.json()).validate(),
        )

    def test_normal_integer(self):
        url = (
            '/api/v3/environments/root.not_used'
            '/variables/integer_var'
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            environment_schema.IntegerVariableSchema(response.json()).validate(),
        )

    def test_normal_boolean(self):
        url = (
            '/api/v3/environments/root.not_used'
            '/variables/boolean_var'
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            environment_schema.BooleanVariableSchema(response.json()).validate(),
        )

    def test_normal_json(self):
        url = (
            '/api/v3/environments/root.not_used'
            '/variables/json_var'
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            environment_schema.JsonVariableSchema(response.json()).validate(),
        )

    def test_missing(self):
        url = (
            '/api/v3/environments/root.programs.httpd.production'
            '/variables/listenkoko'
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate(),
        )

    def test_list(self):
        url = (
            '/api/v3/environments/root.not_used'
            '/variables'
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(
            environment_schema.VariableListSchema(data).validate(),
        )
        self.assertTrue(
            data['result'],
        )

        for _type in ['self', 'inherited']:
            for var in data['data'][_type]:
                if var['type'] == 'string':
                    schema_class = environment_schema.SingleStringVariableSchema
                elif var['type'] == 'integer':
                    schema_class = environment_schema.SingleIntegerVariableSchema
                elif var['type'] == 'boolean':
                    schema_class = environment_schema.SingleBooleanVariableSchema
                elif var['type'] == 'json':
                    schema_class = environment_schema.SingleJsonVariableSchema

                self.assertTrue(
                    schema_class(var).validate(),
                )

    def test_normal_link(self):
        url = (
            '/api/v3/environments/root.programs'
            '/variables/zk_group'
        )
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            environment_schema.StringVariableSchema(data).validate(),
        )
        self.assertEqual(data['data']['link']['name'], 'zk_group')
        self.assertEqual(data['data']['link']['environment']['name'], 'root.defaults')


class TestCreateVariable(tests_helper.BishopApiTestCase):
    types_to_values = {
        'string': 'hello',
        'boolean': True,
        'json': (
            json.dumps({'hello': 'world'}),
            json.dumps(['hello', 'world']),
            {'hello': 'world'},
            ['hello', 'world'],
        ),
        'integer': 1,
    }
    types_to_values_invalid = {
        'string': None,
        'boolean': 'not boolean',
        'json': (
            "{\"object\": \"yes}",
            'string',
            1245,
            True,
        ),
        'integer': "i'm string",
    }
    valid_post_data = {
        'name': 'somevar',
        'is_link': False,
        'environment': 'root.not_used',
    }

    def test_normal(self):
        for _type, values in self.types_to_values.items():
            if not isinstance(values, tuple):
                values = (values,)

            number = 1
            for value in values:
                post_data = copy.deepcopy(self.valid_post_data)
                post_data['type'] = _type
                post_data['value'] = value
                post_data['name'] = '{}_{}_{}'.format(
                    post_data['name'],
                    _type,
                    number,
                )
                post_data = json.dumps(post_data)
                response = self.client.post(
                    '/api/v3/environments/root.not_used/variables',
                    post_data,
                    content_type='application/json',
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(
                    tests_api_schemas.SuccessMessageSchema(response.json()).validate()
                )
                number += 1

    def test_linked(self):
        post_data = copy.deepcopy(self.valid_post_data)
        post_data['type'] = None
        post_data['value'] = None
        post_data['is_link'] = True
        post_data['link_name'] = 'storage_group'
        post_data['link_environment'] = 'root.defaults.production'
        post_data = json.dumps(post_data)
        response = self.client.post(
            '/api/v3/environments/root.not_used/variables',
            post_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_values(self):
        for _type, values in self.types_to_values_invalid.items():
            if not isinstance(values, tuple):
                values = (values,)

            number = 1
            for value in values:
                post_data = copy.deepcopy(self.valid_post_data)
                post_data['type'] = _type
                post_data['value'] = value
                post_data['name'] = '{}_{}_{}'.format(
                    post_data['name'],
                    _type,
                    number,
                )
                post_data = json.dumps(post_data)
                response = self.client.post(
                    '/api/v3/environments/root.not_used/variables',
                    post_data,
                    content_type='application/json',
                )
                self.assertEqual(response.status_code, 400)
                self.assertTrue(
                    tests_api_schemas.ErrorSchema(response.json()).validate()
                )
                number += 1


class TestDeleteVariable(tests_helper.BishopApiTestCase):
    def test_normal(self):
        response = self.client.delete(
            '/api/v3/environments/root.not_used/variables/string_var',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(response.json()).validate()
        )
        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Variable.objects.get(
                name='string_var',
                environment__name='root.not_used',
            )

    def test_missing(self):
        response = self.client.delete(
            '/api/v3/environments/root.not_used/variables/not_exist',
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    def test_used_in_templates(self):
        url = (
            '/api/v3/environments/root.programs.httpd.production'
            '/variables/listen_port'
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )


class TestVariableConvert(tests_helper.BishopApiTestCase):
    def test_link_to_link(self):
        url = (
            '/api/v3/environments/root.chain2'
            '/variables/link1/convert_to_link'
        )
        post_data = {
            'link_name': 'var1',
            'link_environment': 'root.chain2'
        }
        response = self.client.post(
            url,
            post_data,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

    def test_link_to_same_link(self):
        url = (
            '/api/v3/environments/root.chain2'
            '/variables/link1/convert_to_link'
        )
        post_data = {
            'link_name': 'integer_chain_1',
            'link_environment': 'root.chain1'
        }
        response = self.client.post(
            url,
            post_data,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)

    def test_variable_to_link(self):
        url = (
            '/api/v3/environments/root.chain2'
            '/variables/var1/convert_to_link'
        )
        post_data = {
            'link_name': 'integer_chain_2',
            'link_environment': 'root.chain2'
        }
        response = self.client.post(
            url,
            post_data,
            content_type='application/json',
        )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['is_link'], True)
        self.assertEqual(data['data']['link']['name'], 'integer_chain_2')
        self.assertEqual(data['data']['link']['environment']['name'], 'root.chain2')

    def test_variable_to_variable(self):
        url = (
            '/api/v3/environments/root.chain2'
            '/variables/var2/convert_to_normal'
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)

    def test_link_to_variable(self):
        url = (
            '/api/v3/environments/root.chain2'
            '/variables/link2/convert_to_normal'
        )
        response = self.client.post(url)

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data']['is_link'], False)
        self.assertEqual(data['data']['value'], 1)
        self.assertEqual(data['data']['type'], 'integer')
