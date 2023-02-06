import json
import copy

import django.core.exceptions as dce

import metrika.admin.python.bishop.frontend.bishop.models as bp_models

import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas
import metrika.admin.python.bishop.frontend.tests.helper as tests_helper
import metrika.admin.python.bishop.frontend.tests.api.schemas.template as template_schema


class TestCreate(tests_helper.BishopApiTestCase):
    valid_post_data = {
        'name': 'prosto_template.txt',
        'text': 'awesome {% include "template.txt" %}',
        'format': 'plaintext',
    }

    def test_normal(self):
        post_data = json.dumps(self.valid_post_data)
        response = self.client.post(
            '/api/v3/templates',
            post_data,
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )
        self.assertTrue(
            template_schema.TemplateSchema(data).validate()
        )
        count = bp_models.Template.objects.filter(
            name=self.valid_post_data['name']
        ).count()
        self.assertEqual(count, 1)

    def test_duplicate(self):
        post_data = json.dumps(self.valid_post_data)
        response = self.client.post(
            '/api/v3/templates',
            post_data,
            content_type='application/json',
        )
        response = self.client.post(
            '/api/v3/templates',
            post_data,
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )
        count = bp_models.Template.objects.filter(
            name=self.valid_post_data['name']
        ).count()
        self.assertEqual(count, 1)

    def test_invalid_jinja(self):
        post_data = copy.deepcopy(self.valid_post_data)
        post_data['text'] = '{{ inclide jinja %}'
        post_data = json.dumps(post_data)
        response = self.client.post(
            '/api/v3/templates',
            post_data,
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )
        count = bp_models.Template.objects.filter(
            name=self.valid_post_data['name']
        ).count()
        self.assertEqual(count, 0)

    def test_missing_include(self):
        post_data = copy.deepcopy(self.valid_post_data)
        post_data['text'] = '{% include "missing_template.txt" %}'
        post_data = json.dumps(post_data)
        response = self.client.post(
            '/api/v3/templates',
            post_data,
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )
        count = bp_models.Template.objects.filter(
            name=self.valid_post_data['name']
        ).count()
        self.assertEqual(count, 0)

    def test_missing_parameter_name(self):
        post_data = copy.deepcopy(self.valid_post_data)
        del post_data['name']
        post_data = json.dumps(post_data)
        response = self.client.post(
            '/api/v3/templates',
            post_data,
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )

    def test_missing_parameter_text(self):
        post_data = copy.deepcopy(self.valid_post_data)
        del post_data['text']
        post_data = json.dumps(post_data)
        response = self.client.post(
            '/api/v3/templates',
            post_data,
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )
        count = bp_models.Template.objects.filter(
            name=self.valid_post_data['name']
        ).count()
        self.assertEqual(count, 0)

    def test_missing_parameter_format(self):
        post_data = copy.deepcopy(self.valid_post_data)
        del post_data['format']
        post_data = json.dumps(post_data)
        response = self.client.post(
            '/api/v3/templates',
            post_data,
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )
        count = bp_models.Template.objects.filter(
            name=self.valid_post_data['name']
        ).count()
        self.assertEqual(count, 0)

    def test_wrong_name_format(self):
        post_data = json.dumps({
            'name': 'plaintext.txt',
            'format': 'xml',
            'text': 'required',
        })
        response = self.client.post(
            '/api/v3/templates',
            post_data,
            content_type="application/json",
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )
        count = bp_models.Template.objects.filter(
            name=self.valid_post_data['name']
        ).count()
        self.assertEqual(count, 0)


class TestGet(tests_helper.BishopApiTestCase):
    def test_list(self):
        templates_total = bp_models.Template.objects.all().count()
        response = self.client.get('/api/v3/templates')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(
            template_schema.TemplateListSchema(data).validate(),
        )
        self.assertTrue(data['result'])
        self.assertEqual(len(data['data']), templates_total)
        self.assertEqual(len(data['errors']), 0)
        self.assertEqual(len(data['messages']), 0)

    def test_normal(self):
        template = bp_models.Template.objects.get(name='httpd.xml')
        response = self.client.get('/api/v3/templates/httpd.xml')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(
            template_schema.TemplateSchema(data).validate()
        )
        self.assertTrue(data['result'])
        self.assertEqual(data['data']['text'], template.text)

    def test_missing(self):
        response = self.client.get('/api/v3/templates/httpd.xmls')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )


class TestUpdate(tests_helper.BishopApiTestCase):
    valid_put_data = {
        'text': 'awesome',
        'format': 'xml',
    }

    def test_normal(self):
        template = bp_models.Template.objects.get(name='unused.txt')
        text = template.text
        format = template.format
        text_to_update = self.valid_put_data['text']
        put_data = json.dumps(self.valid_put_data)
        response = self.client.put(
            '/api/v3/templates/unused.txt',
            put_data,
            content_type="application/json",
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )
        template = bp_models.Template.objects.get(name='unused.txt')
        self.assertNotEqual(text, template.text)
        self.assertNotEqual(format, template.format)
        self.assertEqual(text_to_update, template.text)

    def test_match_without_ext(self):
        template = bp_models.Template.objects.get(name='match')
        put_data = json.dumps({
            'text': template.text,
            'format': 'json',
            'match_extension': True,
        })
        response = self.client.put(
            '/api/v3/templates/match',
            put_data,
            content_type="application/json",
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )

        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Template.objects.get(name='match')
        template = bp_models.Template.objects.get(name='match.json')
        self.assertEqual(template.format, 'json')

    def test_match_with_ext(self):
        template = bp_models.Template.objects.get(name='match.xml')
        put_data = json.dumps({
            'text': template.text,
            'format': 'json',
            'match_extension': True,
        })
        response = self.client.put(
            '/api/v3/templates/match.xml',
            put_data,
            content_type="application/json",
        )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )

        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Template.objects.get(name='match.xml')
        template = bp_models.Template.objects.get(name='match.json')
        self.assertEqual(template.format, 'json')

    def test_dont_match_with_ext(self):
        template = bp_models.Template.objects.get(name='matchmatch.yaml')
        put_data = json.dumps({
            'text': template.text,
            'format': 'json',
            'match_extension': False,
        })
        response = self.client.put(
            '/api/v3/templates/matchmatch.yaml',
            put_data,
            content_type="application/json",
        )

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(data).validate()
        )

        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Template.objects.get(name='matchmatch.json')
        template = bp_models.Template.objects.get(name='matchmatch.yaml')
        self.assertEqual(template.format, 'json')

    def test_match_with_ext_exists(self):
        template = bp_models.Template.objects.get(name='matchmatch.xml')
        put_data = json.dumps({
            'text': template.text,
            'format': 'yaml',
            'match_extension': True,
        })
        response = self.client.put(
            '/api/v3/templates/matchmatch.xml',
            put_data,
            content_type="application/json",
        )

        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )

        template = bp_models.Template.objects.get(name='matchmatch.xml')
        self.assertEqual(template.format, 'xml')

    def test_missing_text_parameter(self):
        put_data = copy.deepcopy(self.valid_put_data)
        del put_data['text']
        response = self.client.put(
            '/api/v3/templates/unused.txt',
            put_data,
            content_type="application/json",
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )

    def test_missing_format_parameter(self):
        put_data = copy.deepcopy(self.valid_put_data)
        del put_data['format']
        response = self.client.put(
            '/api/v3/templates/unused.txt',
            put_data,
            content_type="application/json",
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(data).validate()
        )

    def test_missing_template(self):
        response = self.client.put('/api/v3/templates/httpd.xmls')

        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()['result'])
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    def test_wrong_format(self):
        put_data = json.dumps({
            'format': 'wrong format',
            'text': 'required',
        })
        response = self.client.put(
            '/api/v3/templates/unused.txt',
            put_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )
        template = bp_models.Template.objects.get(name='unused.txt')
        self.assertEqual(template.format, 'plaintext')

    def test_match_included(self):
        template = bp_models.Template.objects.get(name='logger.xml')
        put_data = json.dumps({
            'text': template.text,
            'format': 'yaml',
            'match_extension': True,
        })
        response = self.client.put(
            '/api/v3/templates/logger.xml',
            put_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )
        template = bp_models.Template.objects.get(name='logger.xml')
        self.assertEqual(template.format, 'xml')

    def test_invalid_jinja(self):
        put_data = json.dumps({
            'text': '{{ invalid jinja %%',
        })
        response = self.client.put(
            '/api/v3/templates/unused.txt',
            put_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    def test_invalid_xml(self):
        put_data = json.dumps({
            'text': '<invalid><xml>',
            'format': 'xml',
        })
        response = self.client.put(
            '/api/v3/templates/template.xml',
            put_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    def test_invalid_json(self):
        put_data = json.dumps({
            'text': '{"hello "vasya"}',
            'format': 'json',
        })
        response = self.client.put(
            '/api/v3/templates/template.json',
            put_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    def test_invalid_yaml(self):
        put_data = json.dumps({
            'text': 'this is invalid yaml:\n    akkaka\n\nd\nd',
            'format': 'yaml',
        })
        response = self.client.put(
            '/api/v3/templates/template.yaml',
            put_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    def test_ignore_render_errors(self):
        # missing variable should be ok in this case
        put_data = json.dumps({
            'text': '{{ missing_variable }}',
            'format': 'yaml',
            'ignore_render_errors': True,
        })
        response = self.client.put(
            '/api/v3/templates/template.yaml',
            put_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(response.json()).validate()
        )


class TestDelete(tests_helper.BishopApiTestCase):
    def test_normal(self):
        response = self.client.delete('/api/v3/templates/unused.txt')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            tests_api_schemas.SuccessMessageSchema(response.json()).validate()
        )
        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Template.objects.get(name='unused.txt')

    def test_missing(self):
        response = self.client.delete('/api/v3/templates/httpd.xmls')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )

    def test_included_by_other_templates(self):
        response = self.client.delete('/api/v3/templates/logger.xml')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )
        bp_models.Template.objects.get(name='logger.xml')

    def test_used_by_program(self):
        response = self.client.delete('/api/v3/templates/httpd.xml')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            tests_api_schemas.ErrorSchema(response.json()).validate()
        )
        bp_models.Template.objects.get(name='httpd.xml')
