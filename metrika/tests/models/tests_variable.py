import metrika.admin.python.bishop.frontend.tests.helper as tests_helper

import metrika.admin.python.bishop.frontend.bishop.models as bp_models
import metrika.admin.python.bishop.frontend.bishop.constants as bp_constants
import metrika.admin.python.bishop.frontend.bishop.exceptions as bp_exceptions


class TestCreate(tests_helper.BishopTestCase):
    @property
    def environment(self):
        return bp_models.Environment.objects.get(name='root.not_used')

    def _create_variable(self, name, value, _type, **kwargs):
        return bp_models.Variable.create(
            name,
            self.environment,
            user=self._request.user,
            _type=_type,
            value=value,
            **kwargs
        )

    def test_string(self):
        value = 'value'
        var = self._create_variable(
            'awesome',
            value,
            'string',
        )
        self.assertEqual(
            var.value,
            value,
        )

    def test_integer(self):
        value = 666
        var = self._create_variable(
            'awesome',
            value,
            'integer',
        )
        self.assertEqual(
            var.type,
            'integer',
        )
        self.assertEqual(
            var.value,
            value,
        )

    def test_json_dict(self):
        value = {"hello": "world"}
        var = self._create_variable(
            'awesome',
            value,
            'json',
        )
        self.assertEqual(
            var.type,
            'json',
        )
        self.assertEqual(
            var.value,
            value,
        )

    def test_json_list(self):
        value = ["hello", "world"]
        var = self._create_variable(
            'awesome',
            value,
            'json',
        )
        self.assertEqual(
            var.type,
            'json',
        )
        self.assertEqual(
            var.value,
            value,
        )

    def test_json_only_dict_and_list(self):
        for value in ('string', 12345, True, False):
            with self.assertRaises(bp_exceptions.BishopModelError):
                self._create_variable(
                    'awesome',
                    value,
                    'json'
                )

    def test_boolean(self):
        value = False
        var = self._create_variable(
            'awesome',
            value,
            'boolean',
        )
        self.assertIs(
            var.type,
            'boolean',
        )
        self.assertIs(
            var.value,
            value,
        )

    def test_missing_user_parameter(self):
        with self.assertRaises(ValueError):
            bp_models.Variable.create(
                'awesome',
                self.environment,
                'hello',
                'string',
            )

    def test_link_environment(self):
        link_environment = bp_models.Environment.objects.get(
            name='root.programs.httpd.testing'
        )
        link = bp_models.Variable.objects.get(
            name='listen_port',
            environment=link_environment,
        )

        var = self._create_variable(
            'awesome',
            None,
            None,
            link=link,
            link_environment=link_environment,
        )
        self.assertTrue(var.is_link)
        self.assertEqual(
            var.value,
            link.value,
        )
        self.assertEqual(
            var.link,
            link,
        )
        self.assertEqual(
            var.link_environment,
            link_environment,
        )


class TestUpdate(tests_helper.BishopTestCase):
    def test_normal(self):
        var = bp_models.Variable.objects.get(
            name='integer_var',
            environment__name='root.not_used',
        )
        desired_type = 'string'
        desired_value = 'hello'

        var.update(desired_type, desired_value)
        var.refresh_from_db()

        self.assertEqual(
            var.type,
            desired_type,
        )
        self.assertEqual(
            var.value,
            desired_value,
        )

    def test_link(self):
        var = bp_models.Variable.objects.get(
            name='integer_chain',
            environment__name='root.variables',
        )
        linked_by = bp_models.Snapshot(init_list=['variable']).get_variable_linked_by(var)
        self.assertEqual(
            len(linked_by),
            1,
        )
        linked_by_recurse = bp_models.Snapshot(init_list=['variable']).get_variable_linked_by_recurse(var)
        self.assertEqual(
            len(linked_by_recurse),
            4,
        )
        for linked_by_var in linked_by_recurse:
            self.assertEqual(
                var.type,
                linked_by_var.type,
            )
            self.assertEqual(
                var.value,
                linked_by_var.value,
            )

        desired_type = 'string'
        desired_value = 'hello'
        var.update(desired_type, desired_value)
        var.refresh_from_db()

        linked_by_recurse = bp_models.Snapshot(init_list=['variable']).get_variable_linked_by_recurse(var)
        self.assertEqual(
            len(linked_by_recurse),
            4,
        )
        for linked_by_var in linked_by_recurse:
            self.assertEqual(
                var.type,
                linked_by_var.type,
            )
            self.assertEqual(
                var.value,
                linked_by_var.value,
            )


class TestUpdateTarget(tests_helper.BishopTestCase):
    def test_normal(self):
        var = bp_models.Variable.objects.get(name='integer_chain_1', environment__name='root.chain1')
        target = bp_models.Variable.objects.get(name='string_var', environment__name='root.variables')

        self.assertNotEqual(var.type, target.type)
        self.assertNotEqual(var.value, target.value)

        linked_by_recurse = bp_models.Snapshot(init_list=['variable']).get_variable_linked_by_recurse(var)
        self.assertEqual(len(linked_by_recurse), 3)

        for linked_by_var in linked_by_recurse:
            self.assertEqual(var.type, linked_by_var.type)
            self.assertEqual(var.value, linked_by_var.value)

        var.update_target(target)
        var.refresh_from_db()

        self.assertEqual(var.type, target.type)
        self.assertEqual(var.value, target.value)

        linked_by_recurse = bp_models.Snapshot(init_list=['variable']).get_variable_linked_by_recurse(var)
        self.assertEqual(len(linked_by_recurse), 3)

        for linked_by_var in linked_by_recurse:
            self.assertEqual(var.type, linked_by_var.type)
            self.assertEqual(var.value, linked_by_var.value)

    def test_not_link(self):
        var = bp_models.Variable.objects.get(name='integer_var', environment__name='root.not_used')
        with self.assertRaises(ValueError):
            var.update_target(None)


class TestClone(tests_helper.BishopTestCase):
    @property
    def environment(self):
        return bp_models.Environment.objects.get(name='root.not_used')

    def test_normal(self):
        var = bp_models.Variable.objects.get(
            name='string_var',
            environment=self.environment,
        )
        to_env = bp_models.Environment.objects.get(name='root.not_used_with_children')
        var.clone(to_env)
        bp_models.Variable.objects.get(
            name='string_var',
            environment=to_env,
        )


class TestConvertToLink(tests_helper.BishopTestCase):
    @property
    def links_env(self):
        return bp_models.Environment.objects.get(name='root.links')

    @property
    def variables_env(self):
        return bp_models.Environment.objects.get(name='root.variables')

    def test_is_link(self):
        link = bp_models.Variable.objects.get(
            name='string_var',
            environment=self.variables_env,
        )
        for _type in bp_constants.VARIABLE_TYPES:
            name = '{}_var_link'.format(_type)
            var = bp_models.Variable.objects.get(
                name=name,
                environment=self.links_env,
            )
            with self.assertRaises(ValueError):
                var.convert_to_link(link)

    def test_normal(self):
        for _type in bp_constants.VARIABLE_TYPES:
            name = '{}_var'.format(_type)
            var = bp_models.Variable.objects.get(
                name=name,
                environment=self.links_env,
            )
            link = bp_models.Variable.objects.get(
                name=name,
                environment=self.variables_env,
            )
            self.assertFalse(var.is_link)
            prev_value = var.value

            var.convert_to_link(link)
            var.refresh_from_db()

            self.assertTrue(var.is_link)
            self.assertNotEqual(
                var.value,
                prev_value,
            )
            self.assertEqual(
                var.value,
                link.value,
            )
            self.assertEqual(
                var.type,
                link.type,
            )

    def test_linked_by(self):
        var = bp_models.Variable.objects.get(
            name='integer_chain',
            environment__name='root.variables',
        )
        link = bp_models.Variable.objects.get(
            name='zk_group',
            environment__name='root.defaults',
        )
        self.assertFalse(var.is_link)
        prev_value = var.value

        var.convert_to_link(link)
        var.refresh_from_db()

        self.assertNotEqual(
            var.value,
            prev_value,
        )
        linked_by_recurse = bp_models.Snapshot(init_list=['variable']).get_variable_linked_by_recurse(var)
        self.assertEqual(
            len(linked_by_recurse),
            4,
        )
        for linked_by_var in linked_by_recurse:
            self.assertEqual(
                var.type,
                linked_by_var.type,
            )
            self.assertEqual(
                var.value,
                linked_by_var.value,
            )


class TestConvertToNormal(tests_helper.BishopTestCase):
    @property
    def links_env(self):
        return bp_models.Environment.objects.get(name='root.links')

    @property
    def variables_env(self):
        return bp_models.Environment.objects.get(name='root.variables')

    def test_not_link(self):
        for _type in bp_constants.VARIABLE_TYPES:
            name = '{}_var'.format(_type)
            var = bp_models.Variable.objects.get(
                name=name,
                environment=self.variables_env,
            )
            with self.assertRaises(ValueError):
                var.convert_to_normal()

    def test_normal(self):
        self.assertEqual(
            len(self.variables_env.linked_by),
            2,
        )
        for _type in bp_constants.VARIABLE_TYPES:
            name = '{}_var_link'.format(_type)
            var = bp_models.Variable.objects.get(
                name=name,
                environment=self.links_env,
            )
            link = var.link
            self.assertTrue(var.is_link)

            var.convert_to_normal()
            var.refresh_from_db()

            self.assertFalse(var.is_link)
            self.assertIs(
                var.link,
                None,
            )
            self.assertIs(
                var.link_environment,
                None,
            )
            self.assertEqual(
                var.value,
                link.value,
            )
            self.assertEqual(
                var.type,
                link.type,
            )
        self.assertEqual(
            len(self.variables_env.linked_by),
            1,
        )
