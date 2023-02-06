import pytest

from sandbox.projects.yabs.qa.pipeline.stage import (
    stage,
    StageRequirementsUnsatisfied,
    StageMissingResults,
    DuplicatedResultFields,
)

from .mock import MockTask


class TestStage(object):
    def test_kwargs(self):
        class Task(MockTask):
            @stage(provides='item')
            def method(self, additional_argument=None):
                return additional_argument

        task = Task()
        task.method(additional_argument='test')
        assert task.Context.item == 'test'

    def test_kwargs_default(self):
        class Task(MockTask):
            @stage(provides='item')
            def method(self, additional_argument='argument_value'):
                return additional_argument

        task = Task()
        task.method()
        assert task.Context.item == 'argument_value'

    @pytest.mark.parametrize('return_value', (
        'my_item',
        ('my_item', ),
        {'item': 'my_item'},
    ))
    def test_return_single_provided_item(self, return_value):
        class Task(MockTask):
            @stage(provides='item', result_is_dict=isinstance(return_value, dict))
            def method(self):
                return return_value

        task = Task()
        task.method()
        assert task.Context.item == 'my_item'

    def test_return_single_provided_dict(self):
        class Task(MockTask):
            @stage(provides='item', result_is_dict=False)
            def method(self):
                return {'inner_item': 'my_inner_item_value'}

        task = Task()
        task.method()
        assert task.Context.item == {'inner_item': 'my_inner_item_value'}

    @pytest.mark.parametrize('return_value', (
        {'first_item': 'my_first_item', 'second_item': 'my_second_item'},
        ('my_first_item', 'my_second_item'),
    ))
    def test_return_multiple_provided_items(self, return_value):
        class Task(MockTask):
            @stage(provides=('first_item', 'second_item'), result_is_dict=isinstance(return_value, dict))
            def method(self):
                return return_value

        task = Task()
        task.method()
        assert task.Context.first_item == 'my_first_item'
        assert task.Context.second_item == 'my_second_item'

    def test_already_done(self):
        class Task(MockTask):
            @stage(provides=('item'))
            def method(self):
                return 'second_item_value'

        task = Task()
        setattr(task.Context, 'item', 'first_item_value')
        result = task.method()
        assert result == 'first_item_value'
        assert task.Context.item == 'first_item_value'

    def test_unsatisfied_requirements(self):
        class Task(MockTask):
            @stage(provides=())
            def method(self, some_variable):
                pass

        task = Task()
        with pytest.raises(StageRequirementsUnsatisfied):
            task.method()

    @pytest.mark.parametrize('provided_item', (
        0,
        0.,
        None,
        True,
        False,
        {},
        set(),
        [],
    ))
    def test_non_string_result_declaration(self, provided_item):
        with pytest.raises(ValueError):
            class Task(MockTask):
                @stage(provides=(provided_item, ))
                def method(self):
                    pass

    def test_duplicated_result_declaration(self):
        with pytest.raises(DuplicatedResultFields):
            class Task(MockTask):
                @stage(provides=('item', 'item'))
                def method(self):
                    pass

    @pytest.mark.parametrize('return_value', (
        {'first_item': 'my_first_item'},
        ('my_first_item', ),
        'my_first_item',
    ))
    def test_missing_results(self, return_value):
        class Task(MockTask):
            @stage(provides=('first_item', 'second_item'), result_is_dict=isinstance(return_value, dict))
            def method(self):
                return return_value

        task = Task()
        with pytest.raises(StageMissingResults):
            task.method()

    def test_failed_stage(self):
        class Task(MockTask):
            @stage(provides=('smth', ))
            def failing_stage(self):
                raise Exception('fail')

        task = Task()
        try:
            task.failing_stage()
        except Exception:
            pass
        assert task.Context._failed_stage == 'failing_stage'
