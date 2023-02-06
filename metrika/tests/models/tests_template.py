import unittest.mock

import django.core.exceptions as dce

import metrika.admin.python.bishop.frontend.tests.helper as tests_helper
import metrika.admin.python.bishop.frontend.bishop.models as bp_models


class TestCreate(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models.Template, 'audit', new=unittest.mock.Mock().method())
    def test_normal(self):
        response = bp_models.Template.create(
            request=self._request,
            response=self._response,
            name='template_name.txt',
            text='hello world',
            format='plaintext',
        )
        self.assertTrue(
            response.result,
        )
        self.assertTrue(
            isinstance(response.data, bp_models.Template)
        )
        self.assertEqual(response.data.variables, [])
        bp_models.Template.audit.assert_called()

    @unittest.mock.patch.object(bp_models.Template, 'audit', new=unittest.mock.Mock().method())
    def test_duplicate(self):
        with self.assertRaises(dce.ValidationError):
            bp_models.Template.create(
                request=self._request,
                response=self._response,
                name='unused.txt',
                text='hello world',
                format='plaintext',
            )
        bp_models.Template.audit.assert_not_called()


class TestDelete(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models.Template, 'audit', new=unittest.mock.Mock().method())
    def test_normal(self):
        template = bp_models.Template.objects.get(name='unused.txt')
        response = template.delete(
            request=self._request,
            response=self._response,
        )
        self.assertTrue(response.result)

        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Template.objects.get(name='unused.txt')

        bp_models.Template.audit.assert_called()

    def test_related_program(self):
        name = 'httpd.xml'
        template = bp_models.Template.objects.get(name=name)
        response = template.delete(
            request=self._request,
            response=self._response,
        )
        self.assertFalse(response.result)
        self.assertTrue(response.errors)
        self.assertTrue(
            bp_models.Template.objects.get(name=name)
        )

    def test_used_as_include(self):
        name = 'zookeeper-servers.xml'
        template = bp_models.Template.objects.get(name=name)
        response = template.delete(
            request=self._request,
            response=self._response,
        )
        self.assertFalse(response.result)
        self.assertTrue(response.errors)
        self.assertTrue(
            bp_models.Template.objects.get(name=name)
        )


class TestRelations(tests_helper.BishopTestCase):
    def test_includes(self):
        template = bp_models.Template.objects.get(name='httpd.xml')
        self.assertIn(
            bp_models.Template.objects.get(name='logger.xml'),
            template.includes,
        )
        self.assertIn(
            bp_models.Template.objects.get(name='input_queue.xml'),
            template.includes,
        )

    def test_includes_recurse(self):
        template = bp_models.Template.objects.get(name='httpd.xml')
        self.assertIn(
            bp_models.Template.objects.get(name='zookeeper-servers.xml'),
            template.includes_recurse,
        )

    def test_included_in(self):
        template = bp_models.Template.objects.get(name='logger.xml')
        included_in_names = (
            'apid.xml',
            'httpd.xml',
            'parserd.xml',
            'writerd.xml',
        )
        included_in = template.included_in

        for name in included_in_names:
            self.assertIn(
                bp_models.Template.objects.get(name=name),
                included_in,
            )

    def test_get_affected_configs_pairs(self):
        template = bp_models.Template.objects.get(name='httpd.xml')
        program = bp_models.Program.objects.get(name='httpd')
        expected = [(program.name, environment.name) for environment in program.environments.all()]
        result = [(i[0].name, i[1].name) for i in template.get_affected_configs_pairs()]

        self.assertEqual(
            sorted(expected),
            sorted(result),
        )

        template = bp_models.Template.objects.get(name='zookeeper-servers.xml')
        programs_names = (
            'parserd',
            'writerd',
            'httpd',
        )
        expected = []
        for name in programs_names:
            program = bp_models.Program.objects.get(name=name)
            for environment in program.environments.all():
                expected.append((program.name, environment.name))

        result = [(i[0].name, i[1].name) for i in template.get_affected_configs_pairs()]
        self.assertEqual(
            sorted(expected),
            sorted(result),
        )


class TestUpdate(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models.Template, 'audit', new=unittest.mock.MagicMock(return_value=None))
    def test_normal(self):
        template = bp_models.Template.objects.get(
            name='template.xml',
        )
        response = template.update(
            request=self._request,
            response=self._response,
            text='<yandex>{{ a|default("a") }}</yandex>',
            format='xml',
        )
        template.refresh_from_db()
        self.assertTrue(response.result)
        self.assertEqual(template.text, '<yandex>{{ a|default("a") }}</yandex>')
        self.assertEqual(template.variables, ["a"])
        bp_models.Template.audit.assert_called()

    @unittest.mock.patch.object(bp_models.Template, 'audit', new=unittest.mock.Mock().method())
    def test_invalid_syntax(self):
        template = bp_models.Template.objects.get(
            name='template.txt',
        )
        text = template.text
        response = template.update(
            request=self._request,
            response=self._response,
            text='{% not jinja :%',
            format='plaintext',
        )
        template.refresh_from_db()
        self.assertFalse(response.result)
        self.assertEqual(template.text, text)
        bp_models.Template.audit.assert_not_called()

    def test_ignore_render_errors(self):
        template = bp_models.Template.objects.get(
            name='template.txt',
        )
        text = template.text
        response = template.update(
            request=self._request,
            response=self._response,
            text='{{ missed_variable }}',
            format='plaintext',
            ignore_render_errors=True,
        )
        template.refresh_from_db()
        self.assertTrue(response.result)
        self.assertNotEqual(template.text, text)
