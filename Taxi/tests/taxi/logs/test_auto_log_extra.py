# pylint: disable=protected-access
import asyncio
import concurrent.futures
import contextvars
import dataclasses
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from taxi.logs import auto_log_extra


@pytest.mark.parametrize(
    ['log_extra_params', 'expected_result'],
    [
        ({}, {'extdict': {}}),
        ({'foo': 'bar', 'b': 'b'}, {'extdict': {'foo': 'bar', 'b': 'b'}}),
    ],
)
def test_to_log_extra(log_extra_params, expected_result):
    assert auto_log_extra.to_log_extra(**log_extra_params) == expected_result


@pytest.mark.parametrize(
    ['context_log_extra', 'expected_result'],
    [
        (None, {'_link': 'monkeypatched_link', 'extdict': {}}),
        (
            {'_link': '123', 'extdict': {'foo': 'bar', 'b': 'b'}},
            {'_link': '123', 'extdict': {'foo': 'bar', 'b': 'b'}},
        ),
    ],
)
def test_get_log_extra(
        monkeypatch_make_link, context_log_extra, expected_result, monkeypatch,
):
    if context_log_extra is not None:
        auto_log_extra._log_extra_var.set(context_log_extra)
    else:
        monkeypatch.setattr(
            'taxi.logs.auto_log_extra._log_extra_var',
            contextvars.ContextVar('log_extra'),
        )

    assert auto_log_extra.get_log_extra() == expected_result


@pytest.mark.parametrize(['copy'], [(False,), (True,)])
def test_get_log_extra_copy(copy):
    auto_log_extra._log_extra_var.set(
        {'_link': '123', 'extdict': {'foo': 'bar'}},
    )
    other_log_extra = auto_log_extra.get_log_extra(copy=copy)
    other_log_extra['extdict']['b'] = 'b'
    if copy:
        assert 'b' not in auto_log_extra.get_log_extra()['extdict']
    else:
        assert 'b' in auto_log_extra.get_log_extra()['extdict']


@pytest.mark.parametrize(
    ['log_extra', 'expected_result'],
    [
        ({}, {'_link': 'monkeypatched_link', 'extdict': {}}),
        ({'_link': '123'}, {'_link': '123', 'extdict': {}}),
        (
            {'extdict': {'foo': 'bar'}},
            {'_link': 'monkeypatched_link', 'extdict': {'foo': 'bar'}},
        ),
        (
            {'_link': '123', 'extdict': {'foo': 'bar'}},
            {'_link': '123', 'extdict': {'foo': 'bar'}},
        ),
    ],
)
def test_set_log_extra(monkeypatch_make_link, log_extra, expected_result):
    auto_log_extra.set_log_extra(log_extra)
    assert auto_log_extra.get_log_extra() == expected_result


@pytest.mark.parametrize(
    ['log_extra', 'new_params', 'expected_result'],
    [
        ({}, {}, {'extdict': {}}),
        ({'_link': '123'}, {}, {'_link': '123', 'extdict': {}}),
        ({'extdict': {}}, {'foo': 'bar'}, {'extdict': {'foo': 'bar'}}),
        (
            {'extdict': {'bar': 'baz'}},
            {'bar': 'foo'},
            {'extdict': {'bar': 'foo'}},
        ),
        (
            {'extdict': {'foo': 'bar'}},
            {'lol': 'kek'},
            {'extdict': {'lol': 'kek', 'foo': 'bar'}},
        ),
    ],
)
def test_update_log_extra(log_extra, new_params, expected_result):
    auto_log_extra._log_extra_var.set(log_extra)
    auto_log_extra.update_log_extra(**new_params)
    assert auto_log_extra.get_log_extra() == expected_result


def test_log_scope():
    auto_log_extra._log_extra_var.set({'extdict': {}})
    with auto_log_extra.log_scope(foo='bar'):
        assert 'foo' in auto_log_extra.get_log_extra()['extdict']
    assert 'foo' not in auto_log_extra.get_log_extra()['extdict']


def test_log_scope_error():
    auto_log_extra._log_extra_var.set({'extdict': {}})
    try:
        with auto_log_extra.log_scope(foo='bar'):
            assert 'foo' in auto_log_extra.get_log_extra()['extdict']
            raise RuntimeError
    except RuntimeError:
        pass

    assert 'foo' not in auto_log_extra.get_log_extra()['extdict']


@dataclasses.dataclass
class DummyRecord:
    _link: Optional[str] = None
    extdict: Dict[str, Any] = dataclasses.field(default_factory=dict)


@pytest.mark.parametrize(
    ['record', 'context_log_extra', 'expected_record'],
    [
        (DummyRecord(), {}, DummyRecord()),
        (DummyRecord(), {'_link': '123'}, DummyRecord(_link='123')),
        (DummyRecord(_link='123'), {}, DummyRecord(_link='123')),
        (DummyRecord(_link='123'), {'_link': '456'}, DummyRecord(_link='123')),
        (
            DummyRecord(extdict={}),
            {'extdict': {'foo': 'bar'}},
            DummyRecord(extdict={'foo': 'bar'}),
        ),
        (
            DummyRecord(extdict={'foo': 'bar'}),
            {},
            DummyRecord(extdict={'foo': 'bar'}),
        ),
        (
            DummyRecord(extdict={'foo': 'bar'}),
            {'extdict': {'foo': 'bug'}},
            DummyRecord(extdict={'foo': 'bar'}),
        ),
        (
            DummyRecord(extdict={'foo': 'bar'}),
            {'extdict': {'baz': 'bug'}},
            DummyRecord(extdict={'foo': 'bar', 'baz': 'bug'}),
        ),
    ],
)
def test_log_context_filter(record, context_log_extra, expected_record):
    auto_log_extra._log_extra_var.set(context_log_extra)
    log_context_filter = auto_log_extra.AutoLogExtraFilter()
    filter_result = log_context_filter.filter(record)
    assert filter_result is True
    assert record == expected_record


async def test_set_copy_on_call_in_executor():
    auto_log_extra.update_log_extra(foo='bar')

    with concurrent.futures.ThreadPoolExecutor() as executor:

        def _get_foo_in_executor():
            log_extra = auto_log_extra.get_log_extra()
            return log_extra['extdict'].get('foo')

        assert (
            await asyncio.get_event_loop().run_in_executor(
                executor, _get_foo_in_executor,
            )
            is None
        )

        assert (
            await asyncio.get_event_loop().run_in_executor(
                executor,
                auto_log_extra.set_copy_on_call(_get_foo_in_executor),
            )
            == 'bar'
        )


async def test_set_copy_on_call_separate_task():
    auto_log_extra.update_log_extra(foo='bar')

    def _get_foo():
        return auto_log_extra.get_log_extra()['extdict']['foo']

    async def _update_foo(foo_val):
        auto_log_extra.update_log_extra(foo=foo_val)
        return _get_foo()

    assert _get_foo() == 'bar'

    assert await _update_foo('bac') == 'bac'
    assert _get_foo() == 'bac'

    foo_from_task = await asyncio.create_task(
        auto_log_extra.set_copy_on_call(_update_foo)('abacaba'),
    )
    assert foo_from_task == 'abacaba'

    assert _get_foo() == 'bac'
