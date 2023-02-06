import mock
import pytest

import dmp_suite.datetime_utils as dtu
from dmp_suite.maintenance import ecook
from dmp_suite.maintenance.ecook import cmd, hooks
from dmp_suite.maintenance.ecook.paths import by_table
from test_dmp_suite.maintenance.ecook.utils import (
    WITH_DEFAULT_SETTINGS,
    assert_system_exit,
    patch_parser,
    path_to_module_name_mock
)
from test_dmp_suite.maintenance.ecook.table import FooTable, DayFooTable


class TestContextHook(object):
    def test_context_without_hook(self):
        context_ = dict()

        def once_copy(definition, context):
            definition.copy(by_table(FooTable))
            assert context_ == context

        _recipe = ecook.Recipe(once_copy.__name__, once_copy, hooks=[])

        with pytest.raises(TypeError):
            _recipe.build(context_)

    def test_decorator_context_without_hook(self):
        context_ = dict()

        @ecook.recipe(hooks=[])
        def once_copy(definition, context):
            definition.copy(by_table(FooTable))
            assert context_ == context

        with pytest.raises(TypeError):
            once_copy.build(context_)

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_context_forwarding(self, m1):
        context_ = dict()

        def once_copy(definition, context):
            definition.copy(by_table(FooTable))
            assert context_ == context

        _recipe = ecook.Recipe(
            once_copy.__name__, once_copy, hooks=(hooks.context_hook,)
        )
        result = _recipe.build(context_)
        expected = [ecook.Command(
            ecook.RecipeDefinition.COPY,
            '//source/bar/group/foo/foo',
            '//dummy/bar/group/foo/foo'
        )]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_decorator_context_forwarding(self, m1):
        context_ = dict()

        @ecook.recipe(hooks=(hooks.context_hook,))
        def once_copy(definition, context):
            definition.copy(by_table(FooTable))
            assert context_ == context

        result = once_copy.build(context_)
        expected = [ecook.Command(
            ecook.RecipeDefinition.COPY,
            '//source/bar/group/foo/foo',
            '//dummy/bar/group/foo/foo'
        )]
        assert expected == result


@mock.patch('dmp_suite.maintenance.ecook.cmd.path_to_module_name',
            path_to_module_name_mock)
class TestPeriodHook(object):

    def test_without_hook(self):
        def once_copy(definition, period):
            definition.copy(by_table(FooTable))

        _recipe = ecook.Recipe(once_copy.__name__, once_copy, hooks=[])

        with pytest.raises(TypeError):
            _recipe.build()

    def test_decorator_context_without_hook(self):
        @ecook.recipe(hooks=[])
        def once_copy(definition, period):
            definition.copy(by_table(FooTable))

        with pytest.raises(TypeError):
            once_copy.build()

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_period_forwarding(self, m1):
        start_date = '2019-04-02'
        end_date = '2019-04-06'
        context_ = type('', (), {})()
        context_.period = dtu.Period(start_date, end_date)

        def once_copy(definition, period):
            definition.copy(by_table(FooTable))
            assert dtu.period(start_date, end_date) == period

        _recipe = ecook.Recipe(
            once_copy.__name__, once_copy, hooks=(hooks.period_hook,)
        )
        result = _recipe.build(context_)
        expected = [ecook.Command(
            ecook.RecipeDefinition.COPY,
            '//source/bar/group/foo/foo',
            '//dummy/bar/group/foo/foo'
        )]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_default_period_rewrite(self, m1):
        start_date = '2019-04-02'
        end_date = '2019-04-03'
        context_ = type('', (), {})()
        context_.period = dtu.Period(start_date, end_date)

        @ecook.recipe(hooks=(hooks.period_hook,))
        def once_copy(definition, period=dtu.period('1998-01-21',
                                                    '1998-01-22')):
            definition.copy(by_table(DayFooTable, period))
            assert dtu.period(start_date, end_date) == period

        result = once_copy.build(context_)
        expected = [
            ecook.Command(
                ecook.RecipeDefinition.COPY,
                '//source/bar/day_foo/2019-04-02',
                '//dummy/bar/day_foo/2019-04-02'
            ),
            ecook.Command(
                ecook.RecipeDefinition.COPY,
                '//source/bar/day_foo/2019-04-03',
                '//dummy/bar/day_foo/2019-04-03'
            ),
        ]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_cmd_args_period_required_raise(self, extract_recipe_mock):
        @ecook.recipe(hooks=(hooks.period_hook,))
        def dummy_recipe(_, period):
            pass

        extract_recipe_mock.return_value = dummy_recipe

        with assert_system_exit():
            cmd.parse_args(['foo/bar.py'])

        with assert_system_exit():
            cmd.parse_args(['foo/bar.py', '--period', '1998-01-21'])

        with assert_system_exit():
            cmd.parse_args(['foo/bar.py', '--period'])

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_cmd_args_period_invalid(self, extract_recipe_mock):
        @ecook.recipe(hooks=(hooks.period_hook,))
        def dummy_recipe(_, period):
            pass

        extract_recipe_mock.return_value = dummy_recipe

        with assert_system_exit():
            cmd.parse_args([
                'foo/bar.py', '--period', '1998-01-22', '1998-01-21'
            ])

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_cmd_args_period_required(self, extract_recipe_mock):
        @ecook.recipe(hooks=(hooks.period_hook,))
        def dummy_recipe(_, period):
            pass

        extract_recipe_mock.return_value = dummy_recipe

        recipe, args = cmd.parse_args([
            'foo/bar.py', '--period', '1998-01-21', '1998-01-22'
        ])
        assert args.period == dtu.period('1998-01-21', '1998-01-22')

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_cmd_args_period_default(self, extract_recipe_mock):
        @ecook.recipe(hooks=(hooks.period_hook,))
        def dummy_recipe(_, period=dtu.period('1998-01-21', '1998-01-22')):
            pass

        extract_recipe_mock.return_value = dummy_recipe

        recipe, args = cmd.parse_args(['foo/bar.py'])
        assert args.period == dtu.period('1998-01-21', '1998-01-22')

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_cmd_args_period_default_rewrite(self, extract_recipe_mock):
        @ecook.recipe(hooks=(hooks.period_hook,))
        def dummy_recipe(_, period=dtu.period('1998-01-21', '1998-01-22')):
            pass

        extract_recipe_mock.return_value = dummy_recipe

        recipe, args = cmd.parse_args([
            'foo/bar.py', '--period', '2008-12-30', '2008-12-31'
        ])
        assert args.period == dtu.period('2008-12-30', '2008-12-31')


class TestDefaultHooks(object):
    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_context_period_forwarding(self, m1):
        start_date = '2019-04-02'
        end_date = '2019-04-06'
        context_ = type('', (), {})()
        context_.period = dtu.Period(start_date, end_date)

        def once_copy(definition, period, context):
            definition.copy(by_table(FooTable))
            assert dtu.period(start_date, end_date) == period
            assert context_ == context

        _recipe = ecook.Recipe(once_copy.__name__, once_copy)
        result = _recipe.build(context_)
        expected = [ecook.Command(
            ecook.RecipeDefinition.COPY,
            '//source/bar/group/foo/foo',
            '//dummy/bar/group/foo/foo'
        )]
        assert expected == result

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_period_context_forwarding(self, m1):
        start_date = '2019-04-02'
        end_date = '2019-04-06'
        context_ = type('', (), {})()
        context_.period = dtu.Period(start_date, end_date)

        def once_copy(definition, context, period):
            definition.copy(by_table(FooTable))
            assert dtu.period(start_date, end_date) == period
            assert context_ == context

        _recipe = ecook.Recipe(once_copy.__name__, once_copy)
        result = _recipe.build(context_)
        expected = [ecook.Command(
            ecook.RecipeDefinition.COPY,
            '//source/bar/group/foo/foo',
            '//dummy/bar/group/foo/foo'
        )]
        assert expected == result
