import yaml

import unittest.mock

import lxml.etree

import django.db
import django.core.exceptions as dce

import metrika.admin.python.bishop.frontend.tests.helper as tests_helper
import metrika.admin.python.bishop.frontend.bishop.models as bp_models
import metrika.admin.python.bishop.frontend.bishop.helpers as bp_helpers
import metrika.admin.python.bishop.frontend.bishop.exceptions as bp_exceptions


class TestCreate(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models.Config, 'audit', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(bp_models.Config, 'validate', new=unittest.mock.Mock().method())
    def test_normal(self):
        program = bp_models.Program.objects.get(name='xml_program')
        environment = bp_models.Environment.objects.get(
            name='root.programs.xml_program.production',
        )
        template = bp_models.Template.objects.get(name='template.xml')
        state = bp_models.ConfigState.objects.get(
            program=program,
            environment=environment,
        )
        config, ar = bp_models.Config.create(
            request=self._request,
            response=self._response,
            program=program,
            environment=environment,
            template=template,
            state=state,
            variables={},
            text=template.text,
            use_vault=False,
            use_hosts=False,
            use_yc_clusters=False,
            use_networks=False,
            vaults=[],
            yc_clusters_ids=[],
        )

        self.assertTrue(
            isinstance(config, bp_models.Config)
        )
        self.assertTrue(
            isinstance(ar, bp_models.ActivationRequest)
        )
        self.assertEqual(
            1,
            config.lines,
        )
        self.assertEqual(
            18,
            config.size,
        )

        bp_models.Config.audit.assert_called()
        bp_models.Config.validate.assert_called()


class TestValidate(tests_helper.BishopTestCase):
    def _get_config(self, fmt):
        return bp_models.Config.objects.get(
            program__name='{}_program'.format(fmt),
            environment__name='root.programs.{}_program.production'.format(fmt),
            active=True,
        )

    def test_plaintext(self):
        config = self._get_config('xml')
        config.text = '<invalid></xml'
        config.template.format = 'plaintext'
        config.format = 'plaintext'
        config.validate()

    def test_valid_xml(self):
        self.assertTrue(
            self._get_config('xml').validate()
        )

    def test_invalid_xml(self):
        config = self._get_config('xml')
        config.text = '<invalid></xml'
        with self.assertRaises(bp_exceptions.ConfigValidationError):
            config.validate()

    def test_valid_json(self):
        self.assertTrue(
            self._get_config('json').validate()
        )

    def test_invalid_json(self):
        config = self._get_config('json')
        config.text = '{"invalid: json"}'
        with self.assertRaises(bp_exceptions.ConfigValidationError):
            config.validate()

    def test_valid_yaml(self):
        self.assertTrue(
            self._get_config('yaml').validate()
        )

    def test_invalid_yaml(self):
        config = self._get_config('yaml')
        config.text = 'ivald\n\n\asdfyaml\nadsf'
        with self.assertRaises(bp_exceptions.ConfigValidationError):
            config.validate()

    @unittest.mock.patch.object(bp_helpers, 'json_loads', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(yaml, 'load', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(lxml.etree, 'fromstring', new=unittest.mock.Mock().method())
    def test_plaintext_format(self):
        config = self._get_config('plaintext')
        self.assertEqual(config.template.format, 'plaintext')
        self.assertEqual(config.format, config.template.format)
        self.assertTrue(
            config.validate()
        )
        bp_helpers.json_loads.assert_not_called()
        yaml.load.assert_not_called()
        lxml.etree.fromstring.assert_not_called()

    @unittest.mock.patch.object(bp_helpers, 'json_loads', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(yaml, 'load', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(lxml.etree, 'fromstring', new=unittest.mock.Mock().method())
    def test_xml_format(self):
        config = self._get_config('xml')
        self.assertEqual(config.template.format, 'xml')
        self.assertEqual(config.format, config.template.format)
        self.assertTrue(
            config.validate()
        )
        bp_helpers.json_loads.assert_not_called()
        yaml.load.assert_not_called()
        lxml.etree.fromstring.assert_called()

    @unittest.mock.patch.object(bp_helpers, 'json_loads', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(yaml, 'load', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(lxml.etree, 'fromstring', new=unittest.mock.Mock().method())
    def test_json_format(self):
        config = self._get_config('json')
        self.assertEqual(config.template.format, 'json')
        self.assertEqual(config.format, config.template.format)
        self.assertTrue(
            config.validate()
        )
        bp_helpers.json_loads.assert_called()
        yaml.load.assert_not_called()
        lxml.etree.fromstring.assert_not_called()

    @unittest.mock.patch.object(bp_helpers, 'json_loads', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(yaml, 'load', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(lxml.etree, 'fromstring', new=unittest.mock.Mock().method())
    def test_yaml_format(self):
        config = self._get_config('yaml')
        self.assertEqual(config.template.format, 'yaml')
        self.assertEqual(config.format, config.template.format)
        self.assertTrue(
            config.validate()
        )
        bp_helpers.json_loads.assert_not_called()
        yaml.load.assert_called()
        lxml.etree.fromstring.assert_not_called()


class TestDelete(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models.Config, 'audit', new=unittest.mock.Mock().method())
    def test_normal(self):
        config = bp_models.Config.objects.get(
            program__name='unused_program'
        )
        pk = config.pk
        config.delete(
            self._request,
            self._response,
        )
        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Config.objects.get(pk=pk)
        bp_models.Config.audit.assert_called()

    def test_delete_failed_if_active_ar_exist(self):
        config = bp_models.Config.objects.filter(
            program__name='yaml_program',
            environment__name='root.programs.yaml_program.testing',
        ).latest()
        self.assertTrue(
            config.get_active_ar(),
        )
        pk = config.pk
        response = config.delete(
            self._request,
            self._response,
        )
        self.assertFalse(
            response.result,
        )
        bp_models.Config.objects.get(pk=pk)


class TestCommon(tests_helper.BishopTestCase):
    def test_versions(self):
        self._update_template(
            'template.txt',
            text='upd!',
        )
        self._update_template(
            'template.txt',
            text='u',
        )
        config = bp_models.Config.objects.latest()
        versions = config.versions
        self.assertEqual(len(versions), 3)
        for item in versions:
            self.assertTrue(
                isinstance(item, bp_models.Config)
            )

    def test_vault(self):
        config = bp_models.Config.objects.filter(template__name='template.txt').latest()
        self.assertFalse(config.use_vault)

        self._update_template(
            'template.txt',
            text='{{ vault["sec-01ckx62bkvpee201ks4d4a1g09"] }}',
        )

        config = bp_models.Config.objects.filter(template__name='template.txt').latest()
        self.assertTrue(config.use_vault)
        self.assertEqual(
            config.vaults,
            ['sec-01ckx62bkvpee201ks4d4a1g09'],
        )


class TestActivate(tests_helper.BishopTestCase):
    program_name = 'plaintext_program'
    environment_name = 'root.programs.plaintext_program.production'
    template_name = 'template.txt'

    def _get_latest_config(self):
        return bp_models.Config.objects.filter(
            program__name=self.program_name,
            environment__name=self.environment_name,
        ).order_by('-pk')[0]

    def _activate(self, config):
        return config.activate(
            self._request,
            self._response,
        )

    @unittest.mock.patch.object(bp_models.Config, 'deactivate', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(django.db.transaction, 'atomic', new=unittest.mock.Mock().method())
    def test_active(self):
        config = self._get_latest_config()
        self.assertTrue(config.active)
        result = config.activate(
            self._request,
            self._response,
        )
        self.assertTrue(result)
        config.deactivate.assert_not_called()
        django.db.transaction.atomic.assert_not_called()

    def test_normal(self):
        config = self._get_latest_config()
        self.assertTrue(config.active)

        self._update_template(self.template_name)

        latest_config = self._get_latest_config()

        self.assertIs(latest_config.active, False)
        self.assertIs(latest_config.was_active, False)

        for attr in ('version', 'active', 'text'):
            self.assertNotEqual(
                getattr(latest_config, attr),
                getattr(config, attr),
            )

        self.assertTrue(
            self._activate(latest_config)
        )

        config.refresh_from_db()
        self.assertIs(config.was_active, True)
        self.assertIs(config.active, False)
