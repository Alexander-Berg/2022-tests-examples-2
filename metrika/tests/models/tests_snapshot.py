import itertools

import metrika.admin.python.bishop.frontend.tests.helper as tests_helper
import metrika.admin.python.bishop.frontend.bishop.models as bp_models
import metrika.admin.python.bishop.frontend.bishop.helpers as bp_helpers


class LazySnapshot:
    def __init__(self):
        self._snapshot = None

    def get_snapshot(self):
        if self._snapshot is None:
            self._snapshot = bp_models.Snapshot()
        return self._snapshot


lazy_snapshot = LazySnapshot()


class TestSnapshot(tests_helper.BishopTestCase):
    @property
    def snapshot(self):
        return lazy_snapshot.get_snapshot()

    def test_get_program_template(self):
        program = bp_models.Program.objects.get(name='json_program')
        self.assertEqual(
            program.template.id,
            self.snapshot.get_program_template(program).id,
        )

    def test_get_config_by_hexdigest(self):
        program = bp_models.Program.objects.get(name='yaml_program')
        environment = bp_models.Environment.objects.get(name='root.programs.yaml_program.production')
        hexdigest = '8f44efcb726e74f2e1e4504d38be0092'
        config = self.snapshot.get_config_by_hexdigest(
            program,
            environment,
            hexdigest,
        )
        self.assertEqual(
            hexdigest,
            config.hexdigest,
        )
        self.assertEqual(
            program.id,
            config.program.id,
        )
        self.assertEqual(
            environment.id,
            config.environment.id,
        )

    def test_get_latest_config(self):
        latest_config_version = 35
        program = bp_models.Program.objects.get(name='yaml_program')
        environment = bp_models.Environment.objects.get(name='root.programs.yaml_program.production')
        config = self.snapshot.get_latest_config(
            program,
            environment,
        )
        self.assertTrue(
            config.version,
            latest_config_version,
        )
        self.assertEqual(
            program.id,
            config.program.id,
        )
        self.assertEqual(
            environment.id,
            config.environment.id,
        )

    def test_get_active_config(self):
        program = bp_models.Program.objects.get(name='yaml_program')
        environment = bp_models.Environment.objects.get(name='root.programs.yaml_program.production')
        config = self.snapshot.get_active_config(
            program,
            environment,
        )
        self.assertTrue(config.active)
        self.assertEqual(
            program.id,
            config.program.id,
        )
        self.assertEqual(
            environment.id,
            config.environment.id,
        )

    def test_get_config_state(self):
        program = bp_models.Program.objects.get(name='yaml_program')
        environment = bp_models.Environment.objects.get(name='root.programs.yaml_program.production')
        state = self.snapshot.get_config_state(
            program,
            environment,
        )
        self.assertEqual(
            program.id,
            state.program.id,
        )
        self.assertEqual(
            environment.id,
            state.environment.id,
        )

    def test_get_environment_variables(self):
        environment = bp_models.Environment.objects.get(name='root.programs.writerd.production')
        expected_variables = sorted([f'{v.id}/{v.name}' for v in environment.variables])
        variables = sorted([f'{v.id}/{v.name}' for v in self.snapshot.get_environment_variables(environment)])

        self.assertEqual(
            expected_variables,
            variables,
        )

    def test_get_environment_children(self):
        environment = bp_models.Environment.objects.get(name='root.programs.plaintext_program')
        expected_children = sorted([f'{e.id}/{e.name}' for e in environment.children])
        children = sorted([f'{e.id}/{e.name}' for e in self.snapshot.get_environment_children(environment)])
        self.assertEqual(
            expected_children,
            children,
        )

        environment = bp_models.Environment.objects.get(name='root.programs.plaintext_program.production')
        self.assertEqual(
            self.snapshot.get_environment_children(environment),
            [],
        )

    def test_get_environment_linked_by(self):
        environment = bp_models.Environment.objects.get(name='root.defaults.testing')
        expected_names = sorted([e.name for e in environment.linked_by])
        names = sorted([e.name for e in self.snapshot.get_environment_linked_by(environment)])
        self.assertEqual(
            expected_names,
            names,
        )

        environment = bp_models.Environment.objects.get(name='root.programs.plaintext_program.production')
        self.assertEqual(
            self.snapshot.get_environment_linked_by(environment),
            [],
        )

    def test_build_environment_variables(self):
        def get_list_of_vars(data):
            return sorted([f'{key}/{value}' for key, value in data.items()])

        environment = bp_models.Environment.objects.get(name='root.programs.writerd.production')
        expected_dict = {
            'storage_port': 8123,
            'storage_group': 'mtlog',
            'zk_env': 'production',
            'zk_group': 'common',
            'not_used_in_httpd': 'some_value',
            'var_used_not_in_all_tempalates': 'super',
        }
        expected_variables = get_list_of_vars(expected_dict)

        helper_dict = bp_helpers.build_environment_variables(environment, {})
        helper_variables = get_list_of_vars(helper_dict)

        snapshot_dict = self.snapshot.build_environment_variables(environment)
        snapshot_variables = get_list_of_vars(snapshot_dict)

        self.assertEqual(
            expected_variables,
            helper_variables,
        )

        self.assertEqual(
            expected_variables,
            snapshot_variables,
        )

    def test_get_template_included_in(self):
        template = bp_models.Template.objects.get(name='zookeeper-servers.xml')
        expected_names = sorted([t.name for t in template.included_in])
        names = sorted([t.name for t in self.snapshot.get_template_included_in(template)])

        self.assertEqual(
            expected_names,
            names,
        )

    def test_get_template_includes(self):
        tpl = bp_models.Template.objects.get(name='parserd.xml')
        expected_includes = sorted([
            'logger.xml',
            'input_queue.xml',
            'output_queue.xml',
        ])

        includes = sorted([template.name for template in self.snapshot.get_template_includes(tpl)])

        self.assertEqual(
            expected_includes,
            includes,
        )

    def test_get_template_includes_recurse(self):
        tpl = bp_models.Template.objects.get(name='parserd.xml')
        expected_includes = sorted([
            'logger.xml',
            'input_queue.xml',
            'zookeeper-servers.xml',
            'output_queue.xml',
        ])

        includes = sorted([template.name for template in self.snapshot.get_template_includes_recurse(tpl)])

        self.assertEqual(
            expected_includes,
            includes,
        )

    def test_get_template_variables_recurse(self):
        template = bp_models.Template.objects.get(name='recursive_vars_check_root.txt')
        expected_variables = sorted([
            'root_var',
            'level1_var',
            'level2_var',
            'level3_var',
        ])

        models_variables = sorted(itertools.chain.from_iterable(
            [item['variables'] for item in template.variables_with_includes]
        ))

        snapshot_variables = sorted(self.snapshot.get_template_variables_recurse(template))

        self.assertEqual(
            expected_variables,
            models_variables,
        )

        self.assertEqual(
            expected_variables,
            snapshot_variables,
        )

    def test_get_configs_pairs_affected_by_environment(self):
        root = bp_models.Environment.objects.get(name='root')
        expected_pairs = []

        for environment in bp_models.Environment.objects.prefetch_related('program_set').all():
            for program in environment.programs:
                expected_pairs.append(
                    (program.name, environment.name),
                )

        expected_pairs = sorted(expected_pairs)
        pairs = sorted([
            (pair[0].name, pair[1].name) for pair in self.snapshot.get_configs_pairs_affected_by_environment(root)
        ])
        self.assertEqual(
            expected_pairs,
            pairs,
        )

    def test_get_configs_pairs_affected_by_template(self):
        template = bp_models.Template.objects.get(name='writerd.xml')
        self.assertEqual(
            template.get_affected_configs_pairs(),
            self.snapshot.get_configs_pairs_affected_by_template(template)
        )

    def test_get_variable_linked_by(self):
        variable = bp_models.Variable.objects.get(
            name='link_source',
            environment__name='root.link_to_link.l1',
        )
        expected_names = [
            'link_2',
        ]
        names = [v.name for v in self.snapshot.get_variable_linked_by(variable)]
        self.assertEqual(
            expected_names,
            names,
        )

    def test_get_variable_linked_by_recurse(self):
        variable = bp_models.Variable.objects.get(
            name='link_source',
            environment__name='root.link_to_link.l1',
        )
        expected_names = [
            'link_2',
            'link_3',
            'link_4',
        ]
        names = sorted([v.name for v in self.snapshot.get_variable_linked_by_recurse(variable)])
        self.assertEqual(
            expected_names,
            names,
        )

    def test_get_linked_by_variable_names(self):
        variable = bp_models.Variable.objects.get(
            name='link_source',
            environment__name='root.link_to_link.l1',
        )
        expected_names = [
            'link_2',
            'link_3',
            'link_4',
            'link_source',
        ]
        names = sorted(self.snapshot.get_linked_by_variable_names(variable))
        self.assertEqual(
            expected_names,
            names,
        )

    def test_get_configs_pairs_affected_by_variable(self):
        variable = bp_models.Variable.objects.get(
            name='var_used_not_in_all_tempalates',
            environment__name='root.programs',
        )
        expected_variable_pairs = [
            ('plaintext_program', 'root.programs.plaintext_program.production'),
            ('plaintext_program', 'root.programs.plaintext_program.testing')
        ]

        environment = bp_models.Environment.objects.get(name='root.programs')

        environment_pairs = sorted([
            (pair[0].name, pair[1].name) for pair in self.snapshot.get_configs_pairs_affected_by_environment(environment)
        ])
        variable_pairs = sorted([
            (pair[0].name, pair[1].name) for pair in self.snapshot.get_configs_pairs_affected_by_variable(variable)
        ])

        self.assertNotEqual(
            environment_pairs,
            variable_pairs,
        )
        self.assertEqual(
            expected_variable_pairs,
            variable_pairs,
        )
