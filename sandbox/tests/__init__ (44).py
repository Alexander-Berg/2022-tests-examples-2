# -*- coding: utf-8 -*-

__author__ = 'alex-k'

from mock import MagicMock as MagicMockOrigin


class DotDict(dict):
    """
    Оборачивает словарь для доступа к атрибутам через точку.

    task = DotDict({
        'Parameters': DotDict({
            'foo': 1
        }),
        'Context': DotDict({
            'bar': 1
        })
    })
    assert task.Parameters.foo == 1
    assert task.Context.bar == 1
    """

    __getattr__ = dict.get


class MagicMock(MagicMockOrigin):
    """
    Оборачивает MagicMock, добавляя по умолчанию spec_set=MagicMock.

    Защищает от вызова несуществующих методов MagicMock
    https://nda.ya.ru/3TcHmG
    """

    def __init__(self, *args, **kwargs):
        super(MagicMock, self).__init__(spec=MagicMockOrigin, *args, **kwargs)

    __enter__ = MagicMockOrigin(return_value=(MagicMockOrigin(), None))
    __exit__ = MagicMockOrigin(return_value=None)


class MemoizeStageMock(MagicMockOrigin):
    u"""
    Мокает memoize_stage в sdk2.Task.

    # в тесте
    self.memoize_stage = MemoizeStageMock()

    # в таске
    with self.memoize_stage.foo(commit_on_entrace=True):
        pass

    with self.memoize_stage.bar:
        pass
    """

    pass
