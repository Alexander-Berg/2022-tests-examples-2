import mock
import pytest
import unittest

import dmp_suite.datetime_utils as dtu
from dmp_suite.maintenance import ecook
from dmp_suite.maintenance.ecook.paths import by_table, yt_paths, by_gp_table
from test_dmp_suite.maintenance.ecook.table import (
    FooTable, DayFooTable, GPMonthPartitionTable,
    GPListPartitionTable, GPListAndMonthPartitionTable, GPHeapTable,
    HnhmEntityTable,
    HnhmEntityTablePartition
)
from test_dmp_suite.maintenance.ecook.utils import (
    patch_parser, WITH_DEFAULT_SETTINGS, simplify_hnhm_attr_meta
)
from dmp_suite.greenplum.meta import GPMeta


class RecipeDecoratorTest(unittest.TestCase):
    def test_without_name(self):
        @ecook.recipe
        def foo(_):
            pass

        assert isinstance(foo, ecook.Recipe)
        assert foo.name == 'foo'

    def test_with_name(self):
        @ecook.recipe(name='default')
        def foo(_):
            pass

        assert isinstance(foo, ecook.Recipe)
        assert foo.name == 'default'

    def test_no_args_call(self):
        @ecook.recipe()
        def foo(_):
            pass

        assert isinstance(foo, ecook.Recipe)
        assert foo.name == 'foo'


class RecipeClsTest(unittest.TestCase):
    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_once_copy(self, m1):
        def once_copy(definition):
            definition.copy(by_table(FooTable))

        _recipe = ecook.Recipe(once_copy.__name__, once_copy)
        result = _recipe.build()
        expected = [ecook.Command(
            ecook.RecipeDefinition.COPY,
            '//source/bar/group/foo/foo',
            '//dummy/bar/group/foo/foo'
        )]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_once_link_period(self, m1):
        def once_link(definition):
            definition.link(by_table(
                DayFooTable,
                dtu.period('2019-04-01', '2019-04-02')
            ))

        _recipe = ecook.Recipe(once_link.__name__, once_link)
        result = _recipe.build()
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.LINK,
                '//source/bar/day_foo/2019-04-01',
                '//dummy/bar/day_foo/2019-04-01'
            ),
            ecook.Command(
                ecook.RecipeDefinition.LINK,
                '//source/bar/day_foo/2019-04-02',
                '//dummy/bar/day_foo/2019-04-02'
            ),
        ]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_once_restore_heap(self, m1):
        gp_object = GPHeapTable

        def once_restore(definition):
            definition.gp.restore(by_gp_table(gp_object, period=dtu.period('2019-04-01', '2019-04-02')))

        _recipe = ecook.Recipe(once_restore.__name__, once_restore)
        result = _recipe.build()
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.RESTORE,
                {
                    'meta': gp_object,
                    'name': GPMeta(gp_object, prefix_manager=lambda x: '').table_full_name,
                    'partition': None,
                    'subpartition': None,
                    'schema_name_prefix': GPMeta(gp_object).prefix
                },
                GPMeta(gp_object).table_full_name
            ),
        ]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_once_restore_period(self, m1):
        gp_object = GPMonthPartitionTable

        def once_restore(definition):
            definition.gp.restore(by_gp_table(gp_object, period=dtu.period('2019-04-01', '2019-04-02')))

        _recipe = ecook.Recipe(once_restore.__name__, once_restore)
        result = _recipe.build()
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.RESTORE,
                {
                    'meta': gp_object,
                    'name': GPMeta(gp_object, prefix_manager=lambda x: '').table_full_name,
                    'partition': {
                        'start_dttm': '2019-04-01 00:00:00',
                        'end_dttm': '2019-04-02 00:00:00'
                    },
                    'subpartition': None,
                    'schema_name_prefix': GPMeta(gp_object).prefix
                },
                GPMeta(gp_object).table_full_name
            ),
        ]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_once_restore_without_period(self, m1):
        gp_object = GPMonthPartitionTable

        def once_restore(definition):
            definition.gp.restore(by_gp_table(gp_object))

        _recipe = ecook.Recipe(once_restore.__name__, once_restore)
        with pytest.raises(ValueError):
            _recipe.build()

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_once_restore_list(self, m1):
        gp_object = GPListPartitionTable

        def once_restore(definition):
            definition.gp.restore(by_gp_table(gp_object, partition=['daily']))

        _recipe = ecook.Recipe(once_restore.__name__, once_restore)
        result = _recipe.build()
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.RESTORE,
                {
                    'meta': gp_object,
                    'name': GPMeta(gp_object, prefix_manager=lambda x: '').table_full_name,
                    'partition': {
                        'list': ['daily']
                    },
                    'subpartition': None,
                    'schema_name_prefix': GPMeta(gp_object).prefix
                },
                GPMeta(gp_object).table_full_name
            ),
        ]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_once_restore_preiod_and_list(self, m1):
        gp_object = GPListAndMonthPartitionTable

        def once_restore(definition):
            definition.gp.restore(by_gp_table(
                gp_object,
                partition=['weekly'],
                subpartition=dtu.period('2019-02-01', '2019-04-02')
            ))

        _recipe = ecook.Recipe(once_restore.__name__, once_restore)
        result = _recipe.build()
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.RESTORE,
                {
                    'meta': gp_object,
                    'name': GPMeta(gp_object, prefix_manager=lambda x: '').table_full_name,
                    'partition': {
                        'list': ['weekly']
                    },
                    'subpartition': {
                        'start_dttm': '2019-02-01 00:00:00',
                        'end_dttm': '2019-04-02 00:00:00'
                    },
                    'schema_name_prefix': GPMeta(gp_object).prefix
                },
                GPMeta(gp_object).table_full_name
            ),
        ]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_multy_definition(self, m1):
        gp_object = GPHeapTable

        def link_and_copy(definition):
            definition.copy(by_table(FooTable))
            definition.link(by_table(
                DayFooTable,
                dtu.period('2019-04-01', '2019-04-02')
            ))
            definition.gp.restore(by_gp_table(gp_object))

        _recipe = ecook.Recipe(link_and_copy.__name__, link_and_copy)
        result = _recipe.build()
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.LINK,
                '//source/bar/day_foo/2019-04-01',
                '//dummy/bar/day_foo/2019-04-01'
            ),
            ecook.Command(
                ecook.RecipeDefinition.LINK,
                '//source/bar/day_foo/2019-04-02',
                '//dummy/bar/day_foo/2019-04-02'
            ),
            ecook.Command(
                ecook.RecipeDefinition.COPY,
                '//source/bar/group/foo/foo',
                '//dummy/bar/group/foo/foo'
            ),
            ecook.Command(
                ecook.RecipeDefinition.RESTORE,
                {
                    'meta': gp_object,
                    'name': GPMeta(gp_object, prefix_manager=lambda x: '').table_full_name,
                    'partition': None,
                    'subpartition': None,
                    'schema_name_prefix': GPMeta(gp_object).prefix
                },
                GPMeta(gp_object).table_full_name
            ),
        ]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_conflict_restore_preiod(self, m1):
        gp_object = GPMonthPartitionTable

        def once_restore(definition):
            definition.gp.restore(by_gp_table(gp_object, period=dtu.period('2019-04-01', '2019-04-02')))
            definition.gp.restore(by_gp_table(gp_object, period=dtu.period('2020-01-01', '2020-04-02')))

        _recipe = ecook.Recipe(once_restore.__name__, once_restore)
        result = _recipe.build()
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.RESTORE,
                {
                    'meta': gp_object,
                    'name': GPMeta(gp_object, prefix_manager=lambda x: '').table_full_name,
                    'partition': {
                        'start_dttm': '2020-01-01 00:00:00',
                        'end_dttm': '2020-04-02 00:00:00'
                    },
                    'subpartition': None,
                    'schema_name_prefix': GPMeta(gp_object).prefix
                },
                GPMeta(gp_object).table_full_name
            ),
        ]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_conflict_copy_link(self, m1):
        def link_and_copy(definition):
            definition.copy(by_table(FooTable))
            definition.link(by_table(FooTable))

        _recipe = ecook.Recipe(link_and_copy.__name__, link_and_copy)
        result = _recipe.build()
        expected = [ecook.Command(
            ecook.RecipeDefinition.LINK,
            '//source/bar/group/foo/foo',
            '//dummy/bar/group/foo/foo'
        )]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_conflict_link_copy(self, m1):
        def link_and_copy(definition):
            definition.link(by_table(FooTable))
            definition.copy(by_table(FooTable))

        _recipe = ecook.Recipe(link_and_copy.__name__, link_and_copy)
        result = _recipe.build()
        expected = [ecook.Command(
            ecook.RecipeDefinition.COPY,
            '//source/bar/group/foo/foo',
            '//dummy/bar/group/foo/foo'
        )]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_restore_period_conflict(self, m1):
        gp_object = GPMonthPartitionTable

        def once_restore(definition):
            definition.gp.restore(by_gp_table(
                gp_object,
                period=dtu.period('2019-04-01', '2019-04-02'),
                partition=dtu.period('2020-01-01', '2020-03-02')
            ))

        _recipe = ecook.Recipe(once_restore.__name__, once_restore)
        result = _recipe.build()
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.RESTORE,
                {
                    'meta': gp_object,
                    'name': GPMeta(gp_object, prefix_manager=lambda x: '').table_full_name,
                    'partition': {
                        'start_dttm': '2020-01-01 00:00:00',
                        'end_dttm': '2020-03-02 00:00:00'
                    },
                    'subpartition': None,
                    'schema_name_prefix': GPMeta(gp_object).prefix
                },
                GPMeta(gp_object).table_full_name
            ),
        ]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_restore_hnhm(self, m1):
        gp_object = HnhmEntityTable
        tables = [t for t in gp_object().get_classes()]

        def once_restore(definition):
            definition.gp.restore(by_gp_table(gp_object))

        _recipe = ecook.Recipe(once_restore.__name__, once_restore)
        result = _recipe.build()
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.RESTORE,
                {
                    'meta': t,
                    'name': GPMeta(t, prefix_manager=lambda x: '').table_full_name,
                    'partition': None,
                    'subpartition': None,
                    'schema_name_prefix': GPMeta(t).prefix
                },
                GPMeta(t).table_full_name
            )
            for t in tables
        ]

        for item in [expected, result]:
            item.sort(key=lambda x: x.target)
            simplify_hnhm_attr_meta(item)

        expected_meta = expected[0].source['meta']
        result_meta = result[0].source['meta']

        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_restore_hnhm_partition(self, m1):
        gp_object = HnhmEntityTablePartition
        tables = [t for t in gp_object().get_classes()]

        def once_restore(definition):
            definition.gp.restore(
                by_gp_table(gp_object, period=dtu.period('2018-01-01', '2019-01-01'))
            )

        _recipe = ecook.Recipe(once_restore.__name__, once_restore)
        result = _recipe.build()
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.RESTORE,
                {
                    'meta': t,
                    'name': GPMeta(t, prefix_manager=lambda x: '').table_full_name,
                    'partition': {
                        'start_dttm': '2018-01-01 00:00:00',
                        'end_dttm': '2019-01-01 00:00:00'
                    },
                    'subpartition': None,
                    'schema_name_prefix': GPMeta(t).prefix
                },
                GPMeta(t).table_full_name
            )
            for t in tables
        ]

        for item in [expected, result]:
            item.sort(key=lambda x: x.target)
            simplify_hnhm_attr_meta(item)

        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_period_conflict(self, m1):
        def link_and_copy(definition):
            definition.link(by_table(
                DayFooTable,
                dtu.period('2019-04-01', '2019-04-02')
            ))
            definition.copy(by_table(
                DayFooTable,
                dtu.period('2019-04-02', '2019-04-02')
            ))

        _recipe = ecook.Recipe(link_and_copy.__name__, link_and_copy)
        result = _recipe.build()
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.LINK,
                '//source/bar/day_foo/2019-04-01',
                '//dummy/bar/day_foo/2019-04-01'
            ),
            ecook.Command(
                ecook.RecipeDefinition.COPY,
                '//source/bar/day_foo/2019-04-02',
                '//dummy/bar/day_foo/2019-04-02'
            ),
        ]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_conflict_folder_table(self, m1):
        def link_and_copy(definition):
            definition.copy(by_table(
                DayFooTable,
                dtu.period('2019-04-02', '2019-04-02')
            ))
            definition.copy(yt_paths('bar', prefix_key='test'))

        _recipe = ecook.Recipe(link_and_copy.__name__, link_and_copy)
        result = _recipe.build()
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.COPY,
                '//source/bar',
                '//dummy/bar'
            ),
            ecook.Command(
                ecook.RecipeDefinition.COPY,
                '//source/bar/day_foo/2019-04-02',
                '//dummy/bar/day_foo/2019-04-02'
            ),
        ]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_context_forwarding(self, m1):
        context_ = dict()

        def once_copy(definition, context):
            definition.copy(by_table(FooTable))
            assert context_ == context

        _recipe = ecook.Recipe(once_copy.__name__, once_copy)
        result = _recipe.build(context_)
        expected = [ecook.Command(
            ecook.RecipeDefinition.COPY,
            '//source/bar/group/foo/foo',
            '//dummy/bar/group/foo/foo'
        )]
        assert expected == result


class ExtractRecipeTest(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(ExtractRecipeTest, self).__init__(methodName)

        def foo(): pass

        self.foo = foo
        self.foo_recipe = ecook.Recipe('foo', foo)
        self.default_recipe = ecook.Recipe('default', foo)

    @mock.patch('dmp_suite.maintenance.ecook.extract_recipes')
    def test_empty_recipes(self, extract_recipes_mock):
        extract_recipes_mock.return_value = []
        with pytest.raises(ValueError):
            ecook.extract_recipe('foo_module', 'default')

    @mock.patch('dmp_suite.maintenance.ecook.extract_recipes')
    def test_named_non_exit_recipe(self, extract_recipes_mock):
        extract_recipes_mock.return_value = [self.foo_recipe]
        with pytest.raises(ValueError):
            ecook.extract_recipe('foo_module', 'default')

    @mock.patch('dmp_suite.maintenance.ecook.extract_recipes')
    def test_multiple_same_named_recipes(self, extract_recipes_mock):
        extract_recipes_mock.return_value = [
            self.default_recipe,
            ecook.Recipe('default', self.foo),
        ]
        with pytest.raises(ValueError):
            ecook.extract_recipe('foo_module', 'default')

    @mock.patch('dmp_suite.maintenance.ecook.extract_recipes')
    def test_named_single_recipe(self, extract_recipes_mock):
        extract_recipes_mock.return_value = [self.default_recipe]
        result = ecook.extract_recipe('foo_module', 'default')
        assert result is self.default_recipe

    @mock.patch('dmp_suite.maintenance.ecook.extract_recipes')
    def test_noname_single_recipe(self, extract_recipes_mock):
        extract_recipes_mock.return_value = [self.foo_recipe]
        result = ecook.extract_recipe('foo_module', None)
        assert result is self.foo_recipe

    @mock.patch('dmp_suite.maintenance.ecook.extract_recipes')
    def test_noname_recipes_with_default(self, extract_recipes_mock):
        extract_recipes_mock.return_value = [
            self.default_recipe, self.foo_recipe
        ]
        result = ecook.extract_recipe('foo_module', None)
        assert result is self.default_recipe

        # change recipes order
        extract_recipes_mock.return_value = [
            self.foo_recipe, self.default_recipe
        ]
        result = ecook.extract_recipe('foo_module', None)
        assert result is self.default_recipe

    @mock.patch('dmp_suite.maintenance.ecook.extract_recipes')
    def test_noname_recipes_without_default(self, extract_recipes_mock):
        extract_recipes_mock.return_value = [
            ecook.Recipe('test', self.foo), self.foo_recipe
        ]

        with pytest.raises(Exception):
            ecook.extract_recipe('foo_module', None)

    @mock.patch('dmp_suite.maintenance.ecook.extract_recipes')
    def test_named_multiple_recipes(self, extract_recipes_mock):
        extract_recipes_mock.return_value = [
            self.default_recipe, self.foo_recipe
        ]
        result = ecook.extract_recipe('foo_module', 'foo')
        assert result is self.foo_recipe

        # change recipes order
        extract_recipes_mock.return_value = [
            self.foo_recipe, self.default_recipe
        ]
        result = ecook.extract_recipe('foo_module', 'foo')
        assert result is self.foo_recipe


def test_extract_recipes():
    result = ecook.extract_recipes('test_dmp_suite.maintenance.ecook.recipes')
    assert 3 == len(result)


def yt_exists_mock(path_dict):
    def yt_exists(path):
        return path_dict[path]

    return yt_exists


def yt_get_attr_mock(path_dict):
    def yt_get_attr(path, attr):
        return path_dict.get(path, {}).get(attr)

    return yt_get_attr


class ExecuteRecipeTest(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def fixture_capsys(self, capsys):
        self.capsys = capsys

    def test_dry_run(self):
        recipe_ = mock.MagicMock()
        recipe_.build.return_value = [
            ecook.Command(ecook.RecipeDefinition.LINK,
                          '//source/link_table',
                          '//target/link_table'),
            ecook.Command(ecook.RecipeDefinition.COPY,
                          '//source/not_exist',
                          '//target/not_exist'),
            ecook.Command(ecook.RecipeDefinition.LINK,
                          '//source/not_exist2',
                          '//target/not_exist2'),
            ecook.Command(ecook.RecipeDefinition.COPY,
                          '//source/copy_table',
                          '//target/copy_table'),
            ecook.Command(ecook.RecipeDefinition.COPY,
                          '//source/copy_by_merge_table',
                          '//target/copy_by_merge_table'),
        ]
        context = type('', (), {})()
        context.dry_run = True
        context.target_ttl_days = 1
        with mock.patch('dmp_suite.maintenance.ecook.yt_operation') as yt_mock, \
                mock.patch('dmp_suite.maintenance.ecook.get_yt_client') as get_yt_client_mock, \
                mock.patch('dmp_suite.maintenance.ecook._get_used_target_prefixes',
                           return_value=['//target']) as get_used_target_prefixes_mock, \
                mock.patch('dmp_suite.maintenance.ecook.cluster_utils') as cluster_utils_mock:
            yt_mock.yt_path_exists = yt_exists_mock({
                '//source': True, '//target': False,
                '//source/link_table': True, '//target/link_table': False,
                '//source/copy_table': True, '//target/copy_table': False,
                '//source/not_exist': False, '//target/not_exist': False,
                '//source/not_exist2': True, '//target/not_exist2': True,
                '//source/copy_by_merge_table': True,
                '//target/copy_by_merge_table': False
            })
            yt_client_mock = mock.MagicMock()
            get_yt_client_mock.return_value = yt_client_mock
            yt_client_mock.get_attribute = yt_get_attr_mock({
                '//source/copy_by_merge_table': dict(dynamic=True)
            })
            ecook.execute_recipe(recipe_, context)
            out, _ = self.capsys.readouterr()

            assert 'Create target prefix directory //target. ' \
                   'Expired days: 1' in out

            assert (
                    'Skip: COPY source=//source/not_exist target=//target/not_exist'
                    ' cause: source does not exist' in out
            )
            assert (
                    'Skip: LINK source=//source/not_exist2'
                    ' target=//target/not_exist2'
                    ' cause: target already exists' in out
            )
            assert (
                    'LINK source=//source/link_table target=//target/link_table'
                    in out
            )
            assert (
                    'COPY source=//source/copy_table target=//target/copy_table'
                    in out
            )
            assert (
                    'COPY source=//source/copy_by_merge_table target=//target/copy_by_merge_table'
                    in out
            )
            yt_mock.create_link.assert_not_called()
            yt_mock.copy_yt_node.assert_not_called()
            cluster_utils_mock.get_job.assert_not_called()
            yt_mock.make_dir.assert_not_called()
            yt_mock.set_yt_attr.assert_not_called()

    def test_execution(self):
        recipe_ = mock.MagicMock()
        recipe_.build.return_value = [
            ecook.Command(ecook.RecipeDefinition.LINK,
                          '//source/link_table',
                          '//target/link_table'),
            ecook.Command(ecook.RecipeDefinition.COPY,
                          '//source/not_exist',
                          '//target/not_exist'),
            ecook.Command(ecook.RecipeDefinition.COPY,
                          '//source/copy_table',
                          '//target/copy_table'),
            ecook.Command(ecook.RecipeDefinition.COPY,
                          '//source/copy_by_merge_table',
                          '//target/copy_by_merge_table'),
        ]
        with mock.patch('dmp_suite.maintenance.ecook.yt_operation') as yt_mock, \
                mock.patch('dmp_suite.maintenance.ecook.get_yt_client') as get_yt_client_mock, \
                mock.patch('dmp_suite.yt.operation.get_yt_client') as get_yt_client_mock2, \
                mock.patch('dmp_suite.maintenance.ecook._get_used_target_prefixes',
                           return_value=['//target']) as get_used_target_prefixes_mock, \
                mock.patch('dmp_suite.maintenance.ecook.cluster_utils') as cluster_utils_mock:
            yt_mock.yt_path_exists = yt_exists_mock({
                '//source': True,
                '//target': False,
                '//source/link_table': True,
                '//target/link_table': False,
                '//source/copy_table': True,
                '//target/copy_table': False,
                '//source/not_exist': False,
                '//target/not_exist': False,
                '//source/copy_by_merge_table': True,
                '//target/copy_by_merge_table': False
            })
            yt_client_mock = mock.MagicMock()
            get_yt_client_mock.return_value = yt_client_mock
            get_yt_client_mock2.return_value = yt_client_mock
            yt_client_mock.get_attribute = yt_get_attr_mock({
                '//source/copy_by_merge_table': dict(dynamic=True)
            })
            job_mock = mock.MagicMock()
            cluster_utils_mock.get_job.return_value = job_mock
            table_stream_mock = mock.MagicMock()
            job_mock.table.return_value = table_stream_mock
            ecook.execute_recipe(recipe_, None)
            yt_mock.create_link.assert_called_with(
                link_path='//target/link_table',
                table_path='//source/link_table'
            )
            yt_mock.copy_yt_node.assert_called_with(
                source_path='//source/copy_table',
                target_path='//target/copy_table',
                force=True,
                recursive=True,
            )
            self.assertTrue(get_used_target_prefixes_mock.called)
            job_mock.table.assert_called_with('//source/copy_by_merge_table')
            table_stream_mock.put.assert_called_with('//target/copy_by_merge_table')
            cluster_utils_mock.run_with_transaction.assert_called_with(job_mock)
            yt_mock.make_dir.assert_called_with('//target')
            yt_mock.set_yt_attr.assert_not_called()
