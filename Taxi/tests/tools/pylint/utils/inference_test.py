import textwrap
import unittest.mock
import warnings

import astroid
import astroid.context
import pytest
import tools.pylint.utils.inference


def test_infer_sends_warning_on_inference_error():
    mock = unittest.mock.Mock(side_effect=astroid.InferenceError())
    code = 'code'
    node = astroid.extract_node(code)
    node.infer = mock
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        tools.pylint.utils.inference.infer(node)
        assert len(w) == 1


def test_infer_returns_none_on_inference_error():
    mock = unittest.mock.Mock(side_effect=astroid.InferenceError())
    code = 'code'
    node = astroid.extract_node(code)
    node.infer = mock
    with warnings.catch_warnings(record=True):
        warnings.simplefilter('always')
        actual = tools.pylint.utils.inference.infer(node)
    assert actual is None


def test_infer_returns_node_if_it_is_a_value():
    code = '42'
    const_node = astroid.extract_node(code)
    actual = tools.pylint.utils.inference.infer(const_node)
    assert const_node == actual


def test_infer_returns_actual_inference_result():
    code = """
    const = 42 #@
    const #@
    """
    code = textwrap.dedent(code)
    const, name = astroid.extract_node(code)

    # Тайпгард
    assert isinstance(const, astroid.Assign)
    assert isinstance(name, astroid.Name)
    assert isinstance(const.value, astroid.Const)

    expected = const.value
    actual = tools.pylint.utils.inference.infer(name)
    assert expected == actual


def test_infer_returns_actual_inference_result_if_types_are_set():
    code = """
    const = 42 #@
    const #@
    """
    code = textwrap.dedent(code)
    const, name = astroid.extract_node(code)

    # Тайпгард
    assert isinstance(const, astroid.Assign)
    assert isinstance(name, astroid.Name)
    assert isinstance(const.value, astroid.Const)

    expected = const.value
    actual = tools.pylint.utils.inference.infer(name, types=(astroid.Const,))
    assert expected == actual


def test_infer_returns_none_if_types_are_not_suitable():
    code = """
    const = 42 #@
    const #@
    """
    code = textwrap.dedent(code)
    const, name = astroid.extract_node(code)

    # Тайпгард
    assert isinstance(const, astroid.Assign)
    assert isinstance(name, astroid.Name)
    assert isinstance(const.value, astroid.Const)

    actual = tools.pylint.utils.inference.infer(name, types=(astroid.Call,))
    assert actual is None


def test_infer_classdef_returns_classdef_if_called_on_it():
    code = """
    class Foo:
        pass
    """
    code = textwrap.dedent(code)
    classdef = astroid.extract_node(code)
    expected = classdef
    actual = tools.pylint.utils.inference.infer_classdef(classdef)
    assert expected == actual


def test_returns_none_for_constant():
    code = '42'
    node = astroid.extract_node(code)
    actual = tools.pylint.utils.inference.infer_classdef(node)
    assert actual is None


def test_infer_classdef_returns_classdef_by_name():
    code = """
    class Foo: #@
        pass

    alias = Foo
    alias #@
    """
    code = textwrap.dedent(code)
    classdef, name = astroid.extract_node(code)
    module = name.root()
    context = astroid.context.bind_context_to_node(None, module)
    actual = tools.pylint.utils.inference.infer_classdef(name, context)
    expected = classdef
    assert expected == actual


def test_resolve_call_returns_call_by_name():
    code = """
    def f(): #@
        pass

    call = f() #@
    alias = call
    alias #@
    """
    code = textwrap.dedent(code)
    func, assign, name = astroid.extract_node(code)
    actual = tools.pylint.utils.inference.resolve_name(name)
    expected = assign.value.func
    assert isinstance(actual, astroid.Call)
    assert actual.func == expected


def test_get_call_kwarg_returns_none_if_kwarg_is_not_set():
    code = 'call(answer=42) #@'
    call = astroid.extract_node(code)
    # Тайпгард
    assert isinstance(call, astroid.Call)
    actual = tools.pylint.utils.inference.infer_call_kwarg(call, "arg")
    assert actual is None


def test_get_call_kwarg_returns_value():
    code = 'call(answer=42) #@'
    call = astroid.extract_node(code)
    # Тайпгард
    assert isinstance(call, astroid.Call)
    expected = 42
    kwarg = tools.pylint.utils.inference.infer_call_kwarg(call, "answer")
    # Тайпгард
    assert isinstance(kwarg, astroid.Const)
    actual = kwarg.value
    assert expected == actual


@pytest.mark.skip(
    """
Этот тест не работает, но было бы круто довести инструменты инференса
до ума, чтобы это проходило.
"""
)
def test_get_call_kwarg_returns_value_for_unpacked_kwargs():
    code = """
    kwargs = {
        'answer': 42
    }
    call(**kwargs) #@
    """
    code = textwrap.dedent(code)
    call = astroid.extract_node(code)
    module = call.root()
    context = astroid.context.bind_context_to_node(None, module)
    # Тайпгард
    assert isinstance(call, astroid.Call)
    expected = 42
    kwarg = tools.pylint.utils.inference.infer_call_kwarg(call, "answer", context)
    # Тайпгард
    assert isinstance(kwarg, astroid.Const)
    actual = kwarg.value
    assert expected == actual


def test_get_call_kwarg_returns_inferred_value():
    code = """
    answer = 42
    call(answer=answer) #@
    """
    code = textwrap.dedent(code)
    call = astroid.extract_node(code)
    module = call.root()
    context = astroid.context.bind_context_to_node(None, module)
    # Тайпгард
    assert isinstance(call, astroid.Call)
    expected = 42
    kwarg = tools.pylint.utils.inference.infer_call_kwarg(call, "answer", context)
    # Тайпгард
    assert isinstance(kwarg, astroid.Const)
    actual = kwarg.value
    assert expected == actual
