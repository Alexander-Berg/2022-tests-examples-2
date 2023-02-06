import unittest.mock

import django.core.exceptions as dce

import metrika.admin.python.bishop.frontend.tests.helper as tests_helper

import metrika.admin.python.bishop.frontend.bishop.lock as bp_lock
import metrika.admin.python.bishop.frontend.bishop.models as bp_models
import metrika.admin.python.bishop.frontend.bishop.exceptions as bp_exceptions


class TestCreate(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_normal(self):
        parent = bp_models.Environment.objects.get(
            name='root.programs',
        )
        response = bp_models.Environment.create(
            request=self._request,
            response=self._response,
            name='envik',
            parent=parent,
        )
        self.assertTrue(response.result)
        self.assertTrue(
            isinstance(response.data, bp_models.Environment),
        )
        bp_models.Environment.audit.assert_called()
        environment = response.data

        self.assertEqual(
            environment.name,
            'root.programs.envik',
        )

        self.assertEqual(
            environment.parent.name,
            parent.name,
        )
        parent.refresh_from_db()
        self.assertTrue(
            parent.has_children
        )

        self.assertTrue(
            bp_models.Environment.objects.get(name='root.programs.envik')
        )

    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_has_children_updated(self):
        parent = bp_models.Environment.objects.get(
            name='root.not_used',
        )
        self.assertFalse(
            parent.has_children
        )
        response = bp_models.Environment.create(
            request=self._request,
            response=self._response,
            name='envik',
            parent=parent,
        )
        self.assertTrue(response.result)
        self.assertTrue(
            isinstance(response.data, bp_models.Environment),
        )
        parent.refresh_from_db()
        self.assertTrue(
            parent.has_children
        )

    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_duplicate(self):
        with self.assertRaises(dce.ValidationError):
            parent = bp_models.Environment.objects.get(
                name='root',
            )
            bp_models.Environment.create(
                request=self._request,
                response=self._response,
                name='programs',
                parent=parent,
            )
        bp_models.Environment.audit.assert_not_called()


class TestDelete(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_normal(self):
        environment = bp_models.Environment.objects.get(
            name='root.not_used_with_children.not_used',
        )
        parent = environment.parent
        self.assertTrue(
            parent.has_children
        )

        response = environment.delete(
            request=self._request,
            response=self._response,
        )
        self.assertTrue(response.result)

        parent.refresh_from_db()
        self.assertFalse(
            parent.has_children
        )

        bp_models.Environment.audit.assert_called()

    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_root(self):
        name = 'root'
        environment = bp_models.Environment.objects.get(name=name)
        response = environment.delete(
            request=self._request,
            response=self._response,
        )
        self.assertFalse(response.result)
        bp_models.Environment.audit.assert_not_called()
        self.assertTrue(
            bp_models.Environment.objects.get(name=name)
        )

    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_has_children(self):
        name = 'root.not_used_with_children'
        environment = bp_models.Environment.objects.get(name=name)
        response = environment.delete(
            request=self._request,
            response=self._response,
        )
        self.assertFalse(response.result)
        bp_models.Environment.audit.assert_not_called()
        self.assertTrue(
            bp_models.Environment.objects.get(name=name)
        )

    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_attached_to_program(self):
        name = 'root.programs.apid.production'
        environment = bp_models.Environment.objects.get(name=name)
        response = environment.delete(
            request=self._request,
            response=self._response,
        )
        self.assertFalse(response.result)
        bp_models.Environment.audit.assert_not_called()
        self.assertTrue(
            bp_models.Environment.objects.get(name=name)
        )

    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_has_related_configs(self):
        name = 'root.detached'
        environment = bp_models.Environment.objects.get(name=name)
        response = environment.delete(
            request=self._request,
            response=self._response,
        )
        self.assertFalse(response.result)
        bp_models.Environment.audit.assert_not_called()
        self.assertTrue(
            bp_models.Environment.objects.get(name=name)
        )


class TestRelations(tests_helper.BishopTestCase):
    def test_get_affected_configs_pairs(self):
        environment = bp_models.Environment.objects.get(
            name='root.programs.httpd',
        )
        expected = [
            ('httpd', 'root.programs.httpd.production'),
            ('httpd', 'root.programs.httpd.testing'),
            ('writerd', 'root.programs.writerd.production'),
            ('writerd', 'root.programs.writerd.testing'),
        ]

        result = sorted([
            (pair[0].name, pair[1].name) for pair in environment.get_affected_configs_pairs()
        ])

        self.assertEqual(
            expected,
            result,
        )

        environment = bp_models.Environment.objects.get(
            name='root.defaults.production',
        )

        expected = [
            ('apid', 'root.programs.apid.production'),
            ('httpd', 'root.programs.httpd.production'),
            ('parserd', 'root.programs.parserd.production'),
            ('writerd', 'root.programs.writerd.production'),
            ('writerd', 'root.programs.writerd.testing'),
            ('yaml_program', 'root.programs.yaml_program.production'),
        ]

        result = sorted([
            (pair[0].name, pair[1].name) for pair in environment.get_affected_configs_pairs()
        ])

        self.assertEqual(
            expected,
            result,
        )

        environment = bp_models.Environment.objects.get(
            name='root.not_used',
        )
        self.assertEqual(
            [],
            environment.get_affected_configs_pairs(),
        )


class TestConvertVariableToLink(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models, 'rebuild_affected_configs', new=unittest.mock.Mock().method())
    def test_value_not_changed(self):
        environment = bp_models.Environment.objects.get(name='root.links')
        var = bp_models.Variable.objects.get(
            name='integer_1111',
            environment=environment,
        )
        link = bp_models.Variable.objects.get(
            name='integer_1111',
            environment__name='root.variables',
        )
        response = environment.convert_variable_to_link(
            var,
            link,
            request=self._request,
            response=self._response,
        )
        self.assertTrue(response.result)
        bp_models.rebuild_affected_configs.assert_not_called()

    @unittest.mock.patch.object(bp_models, 'rebuild_affected_configs', new=unittest.mock.Mock().method())
    def test_value_changed(self):
        environment = bp_models.Environment.objects.get(name='root.links')
        var = bp_models.Variable.objects.get(
            name='integer_1111',
            environment=environment,
        )
        link = bp_models.Variable.objects.get(
            name='integer_2222',
            environment__name='root.variables',
        )
        response = environment.convert_variable_to_link(
            var,
            link,
            request=self._request,
            response=self._response,
        )
        self.assertTrue(response.result)
        bp_models.rebuild_affected_configs.assert_called()

    @unittest.mock.patch.object(bp_models, 'rebuild_affected_configs', new=unittest.mock.Mock().method())
    def test_error_on_self(self):
        environment = bp_models.Environment.objects.get(name='root.links')
        var = bp_models.Variable.objects.get(
            name='integer_1111',
            environment=environment,
        )
        response = environment.convert_variable_to_link(
            var,
            var,
            request=self._request,
            response=self._response,
        )
        self.assertFalse(response.result)
        bp_models.rebuild_affected_configs.assert_not_called()


class TestUpdateLinkedVariableTarget(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models, 'rebuild_affected_configs', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_normal(self):
        var = bp_models.Variable.objects.get(name='integer_chain_1', environment__name='root.chain1')
        target = bp_models.Variable.objects.get(name='string_var', environment__name='root.variables')

        environment = var.environment

        response = environment.update_linked_variable_target(
            var,
            target,
            response=self._response,
            request=self._request,
        )
        self.assertTrue(response.result)
        bp_models.Environment.audit.assert_called()
        bp_models.rebuild_affected_configs.assert_called()

    @unittest.mock.patch.object(bp_models, 'rebuild_affected_configs', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_value_not_changed(self):
        var = bp_models.Variable.objects.get(name='integer_chain_2', environment__name='root.chain2')
        target = bp_models.Variable.objects.get(name='integer_chain', environment__name='root.variables')

        environment = var.environment

        response = environment.update_linked_variable_target(
            var,
            target,
            response=self._response,
            request=self._request,
        )
        self.assertTrue(response.result)
        bp_models.Environment.audit.assert_called()
        bp_models.rebuild_affected_configs.assert_not_called()

    @unittest.mock.patch.object(bp_models, 'rebuild_affected_configs', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_error_on_self(self):
        var = bp_models.Variable.objects.get(name='integer_chain_2', environment__name='root.chain2')

        environment = var.environment

        response = environment.update_linked_variable_target(
            var,
            var,
            response=self._response,
            request=self._request,
        )
        self.assertFalse(response.result)
        bp_models.Environment.audit.assert_not_called()
        bp_models.rebuild_affected_configs.assert_not_called()


class TestAddLinkedVariable(tests_helper.BishopTestCase):
    def _create_link(self,
                     rebuild_configs=None,
                     environment=None,
                     ):
        kwargs = {}

        if rebuild_configs is not None:
            kwargs['rebuild_configs'] = rebuild_configs

        if environment is None:
            environment = bp_models.Environment.objects.get(
                name='root.programs.httpd.production',
            )

        link = bp_models.Variable.objects.get(
            name='string_var',
            environment__name='root.not_used',
        )

        response = environment.add_linked_variable(
            'link_to_string_var',
            link,
            request=self._request,
            response=self._response,
            **kwargs
        )
        return response, environment

    @unittest.mock.patch.object(bp_models, 'rebuild_affected_configs', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_normal(self):
        response, environment = self._create_link()

        self.assertTrue(response.result)
        variable = response.data
        self.assertTrue(
            isinstance(variable, bp_models.Variable),
        )
        self.assertIn(
            variable,
            environment.variables,
        )

        bp_models.Environment.audit.assert_called()
        bp_models.rebuild_affected_configs.assert_called()

    @unittest.mock.patch.object(bp_lock.ObjectLock, '__enter__', new=unittest.mock.Mock().method())
    def test_lock_taken(self):
        environment = bp_models.Environment.objects.get(
            name='root.programs.httpd.production',
        )
        response, environment = self._create_link(
            environment=environment,
        )
        bp_lock.ObjectLock.__enter__.assert_called()

    @unittest.mock.patch.object(bp_models, 'rebuild_affected_configs', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_no_rebuild_configs(self):
        response, environment = self._create_link(
            rebuild_configs=False,
        )

        self.assertTrue(response.result)
        self.assertTrue(
            isinstance(response.data, bp_models.Variable),
        )
        bp_models.Environment.audit.assert_called()
        bp_models.rebuild_affected_configs.assert_not_called()

    def test_duplicate_name(self):
        with self.assertRaises(bp_exceptions.BishopModelError):
            self._create_link()
            self._create_link()


class TestClone(tests_helper.BishopTestCase):
    def test_normal(self):
        environment = bp_models.Environment.objects.get(
            name='root.programs.httpd.production',
        )
        parent = bp_models.Environment.objects.get(
            name='root.defaults',
        )
        response = environment.clone(
            response=self._response,
            request=self._request,
            name='cloned',
            parent=parent,
        )
        self.assertTrue(
            response.result,
        )
        clone = response.data

        self.assertTrue(
            isinstance(clone, bp_models.Environment),
        )
        self.assertEqual(
            set([(v.name, v.value, v.type, v.is_link) for v in clone.variables]),
            set([(v.name, v.value, v.type, v.is_link) for v in environment.variables]),
        )


class TestDeleteVariable(tests_helper.BishopTestCase):
    @unittest.mock.patch.object(bp_models, 'rebuild_affected_configs', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_normal(self):
        environment = bp_models.Environment.objects.get(
            name='root.not_used',
        )
        variable = bp_models.Variable.objects.get(
            name='boolean_var',
            environment=environment,
        )
        response = environment.delete_variable(
            variable,
            request=self._request,
            response=self._response,
        )
        self.assertTrue(
            response.result,
        )
        self.assertFalse(
            bp_models.ConfigState.objects.filter(broken=True),
        )

    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_linked_by(self):
        environment = bp_models.Environment.objects.get(
            name='root.programs.httpd.production',
        )
        variable = bp_models.Variable.objects.get(
            name='not_used_in_httpd',
            environment=environment,
        )
        response = environment.delete_variable(
            variable,
            request=self._request,
            response=self._response,
        )
        self.assertFalse(
            response.result,
        )
        bp_models.Environment.audit.assert_not_called()


class TestAddVariable(tests_helper.BishopTestCase):
    def _create_variable(self,
                         rebuild_configs=None,
                         environment=None,
                         ):
        kwargs = {}

        if rebuild_configs is not None:
            kwargs['rebuild_configs'] = rebuild_configs

        if environment is None:
            environment = bp_models.Environment.objects.get(
                name='root.programs.httpd',
            )

        response = environment.add_variable(
            'string',
            'somevar',
            'somevalue',
            request=self._request,
            response=self._response,
            **kwargs
        )
        return response, environment

    @unittest.mock.patch.object(bp_models, 'rebuild_affected_configs', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_normal(self):
        response, environment = self._create_variable()

        self.assertTrue(
            response.result,
        )
        variable = response.data
        self.assertTrue(
            isinstance(variable, bp_models.Variable),
        )
        self.assertIn(
            variable,
            environment.variables,
        )

        bp_models.Environment.audit.assert_called()
        bp_models.rebuild_affected_configs.assert_called()

    @unittest.mock.patch.object(bp_lock.ObjectLock, '__enter__', new=unittest.mock.Mock().method())
    def test_lock_taken(self):
        environment = bp_models.Environment.objects.get(
            name='root.programs.httpd',
        )
        response, environment = self._create_variable(
            environment=environment,
        )
        bp_lock.ObjectLock.__enter__.assert_called()

    @unittest.mock.patch.object(bp_models, 'rebuild_affected_configs', new=unittest.mock.Mock().method())
    @unittest.mock.patch.object(bp_models.Environment, 'audit', new=unittest.mock.Mock().method())
    def test_no_rebuild_configs(self):
        response, environment = self._create_variable(
            rebuild_configs=False,
        )

        self.assertTrue(
            response.result,
        )
        self.assertTrue(
            isinstance(response.data, bp_models.Variable),
        )
        bp_models.Environment.audit.assert_called()
        bp_models.rebuild_affected_configs.assert_not_called()

    def test_duplicate_name(self):
        with self.assertRaises(bp_exceptions.BishopModelError):
            self._create_variable()
            self._create_variable()
