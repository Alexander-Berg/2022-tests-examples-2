import unittest.mock

from datetime import datetime

import django.core.exceptions as dce

import metrika.admin.python.bishop.frontend.tests.helper as tests_helper
import metrika.admin.python.bishop.frontend.bishop.models as bp_models
import metrika.admin.python.bishop.frontend.bishop.exceptions as bp_exceptions


class TestCreate(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models.Program, 'audit', new=unittest.mock.Mock().method())
    def test_normal(self):
        template = bp_models.Template.objects.get(name='simple.txt')
        response = bp_models.Program.create(
            request=self._request,
            response=self._response,
            name='test_program',
            template=template,
        )
        self.assertTrue(response.result)
        self.assertTrue(
            isinstance(response.data, bp_models.Program),
        )
        bp_models.Program.audit.assert_called()

    def test_duplicate(self):
        template = bp_models.Template.objects.get(name='simple.txt')
        with self.assertRaises(dce.ValidationError):
            bp_models.Program.create(
                request=self._request,
                response=self._response,
                name='plaintext_program',
                template=template,
            )


class TestUpdate(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models.Program, 'audit', new=unittest.mock.MagicMock(return_value=None))
    def test_normal(self):
        program = bp_models.Program.objects.get(
            name='plaintext_program',
        )
        template = bp_models.Template.objects.get(name='simple.txt')
        template.save()
        response = program.update(
            request=self._request,
            response=self._response,
            template=template,
        )
        program.refresh_from_db()
        self.assertEqual(program.template.id, template.id)
        self.assertTrue(response.result)
        bp_models.Program.audit.assert_called()

    @unittest.mock.patch.object(bp_models.Program, 'audit', new=unittest.mock.Mock().method())
    def test_render_error_in_target_template(self):
        program = bp_models.Program.objects.get(
            name='plaintext_program',
        )
        template = bp_models.Template.objects.get(name='simple.txt')
        template.text = "{{ hell }}"
        template.save()
        response = program.update(
            request=self._request,
            response=self._response,
            template=template,
        )
        program.refresh_from_db()
        self.assertNotEqual(program.template.id, template.id)
        self.assertFalse(response.result)


class TestDelete(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models.Program, 'audit', new=unittest.mock.Mock().method())
    def test_normal(self):
        program = bp_models.Program.objects.get(
            name='simple_program',
        )
        response = program.delete(
            request=self._request,
            response=self._response,
        )
        self.assertTrue(response.result)
        bp_models.Program.audit.assert_called()

    @unittest.mock.patch.object(bp_models.Program, 'audit', new=unittest.mock.Mock().method())
    def test_related_configs(self):
        program = bp_models.Program.objects.get(
            name='plaintext_program',
        )
        response = program.delete(
            request=self._request,
            response=self._response,
        )
        self.assertFalse(response.result)
        bp_models.Program.audit.assert_not_called()


class TestRebuildConfigs(tests_helper.BishopTestCase):
    program_name = 'plaintext_program'
    environment_name = 'root.programs.plaintext_program.production'
    template_name = 'template.txt'

    def test_normal(self):
        program = self._get_program()
        template = self._get_template()
        environment = self._get_environment()

        config = program.get_latest_config(environment)

        template.text = template.text + '\nhello'
        template.save()

        program.rebuild_configs(
            request=self._request,
            response=self._response,
        )

        latest_config = program.get_latest_config(environment)
        self.assertTrue(config.version < latest_config.version)
        self.assertFalse(latest_config.active)

        self.assertFalse(latest_config.use_hosts)
        self.assertFalse(latest_config.use_vault)
        self.assertFalse(latest_config.use_networks)

    def test_render_error(self):
        program = self._get_program()
        environment = self._get_environment()
        template = self._get_template()
        template.text = '{% lol-tag %}'
        template.save()

        config = program.get_latest_config(environment)
        self.assertFalse(config.state.broken)

        with self.assertRaises(bp_exceptions.RenderError):
            program.rebuild_configs(
                request=self._request,
                response=self._response,
            )
        config.state.refresh_from_db()
        self.assertFalse(config.state.broken)

    def test_ignore_render_error(self):
        program = self._get_program()
        environment = self._get_environment()
        template = self._get_template()
        trigger = 'ignoredl!lol'
        template.text = '{% lol-tag %}'
        template.save()

        config = program.get_latest_config(environment)
        state = config.state
        self.assertFalse(state.broken)
        self.assertFalse(state.broken_at)

        program.rebuild_configs(
            request=self._request,
            response=self._response,
            ignore_render_errors=True,
            trigger=trigger,
        )

        config.state.refresh_from_db()
        self.assertTrue(config.state.broken)
        self.assertTrue(
            isinstance(config.state.broken_at, datetime)
        )
        self.assertIn(trigger, config.state.error_text)

    def test_not_created_if_not_changed(self):
        program = self._get_program()
        environment = self._get_environment()

        config = program.get_latest_config(environment)

        program.rebuild_configs(
            request=self._request,
            response=self._response,
        )

        latest_config = program.get_latest_config(environment)

        self.assertEqual(config.pk, latest_config.pk)


class TestAttachEnvironment(tests_helper.BishopTestCase):
    def test_normal(self):
        program = bp_models.Program.objects.get(
            name='simple_program',
        )
        environment = bp_models.Environment.objects.get(
            name='root.programs.plaintext_program.production',
        )

        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Config.objects.get(program=program, environment=environment)

        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.ConfigState.objects.get(program=program, environment=environment)

        self.assertNotIn(
            environment,
            program.environments.all(),
        )
        response = program.attach_environment(
            request=self._request,
            response=self._response,
            environment=environment,
        )
        self.assertTrue(response.result)
        self.assertTrue(
            isinstance(response.data, bp_models.Program),
        )
        self.assertIn(
            environment,
            program.environments.all(),
        )

        config = bp_models.Config.objects.get(program=program, environment=environment)
        self.assertFalse(config.active)

        state = bp_models.ConfigState.objects.get(program=program, environment=environment)
        self.assertFalse(state.auto_activation)

    def test_auto_activation(self):
        program = bp_models.Program.objects.get(
            name='simple_program',
        )
        environment = bp_models.Environment.objects.get(
            name='root.programs.plaintext_program.production',
        )

        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.Config.objects.get(program=program, environment=environment)

        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.ConfigState.objects.get(program=program, environment=environment)

        self.assertNotIn(
            environment,
            program.environments.all(),
        )
        response = program.attach_environment(
            request=self._request,
            response=self._response,
            environment=environment,
            auto_activation=True,
        )
        self.assertTrue(response.result)
        self.assertTrue(
            isinstance(response.data, bp_models.Program),
        )
        self.assertIn(
            environment,
            program.environments.all(),
        )

        config = bp_models.Config.objects.get(program=program, environment=environment)
        self.assertTrue(config.active)

        state = bp_models.ConfigState.objects.get(program=program, environment=environment)
        self.assertTrue(state.auto_activation)


class TestDetachEnvironment(tests_helper.BishopTestCase):
    def test_normal(self):
        program = bp_models.Program.objects.get(
            name='plaintext_program',
        )
        environment = bp_models.Environment.objects.get(
            name='root.programs.plaintext_program.production',
        )
        self.assertTrue(
            bp_models.Config.objects.get(program=program, environment=environment, active=True),
        )
        self.assertTrue(
            bp_models.ConfigState.objects.get(program=program, environment=environment)
        )
        self.assertIn(
            environment,
            program.environments.all(),
        )

        response = program.detach_environment(
            request=self._request,
            response=self._response,
            environment=environment,
        )

        self.assertTrue(response.result)
        self.assertTrue(
            isinstance(response.data, bp_models.Program),
        )
        self.assertNotIn(
            environment,
            program.environments.all(),
        )

        with self.assertRaises(dce.ObjectDoesNotExist):
            bp_models.ConfigState.objects.get(program=program, environment=environment)
