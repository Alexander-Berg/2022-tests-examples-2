# -*- coding: utf-8 -*-

import difflib


def build_diff(a, b):
    matcher = SequenceMatcher(a=b, b=a)
    return a, b, matcher.get_opcodes()


def format_diff(diff_result):
    a, b, opcodes = diff_result
    messages = []
    for tag, start_b, end_b, start_a, end_a in opcodes:
        messages += _diff_opcode_to_messages(tag, a[start_a:end_a], b[start_b:end_b])
    return '%s\n' % '\n'.join(messages)


_DIFF_OPCODE_TO_PREFIX = {
    'equal': ' ',
    'delete': '-',
    'insert': '+',
}


def _diff_opcode_to_messages(tag, actual_slice, expected_slice):
    messages = []
    for item in expected_slice:
        messages.append('%s %r' % (_DIFF_OPCODE_TO_PREFIX.get(tag, '-'), item))
    if tag != 'equal':
        for item in actual_slice:
            messages.append('%s %r' % (_DIFF_OPCODE_TO_PREFIX.get(tag, '+'), item))
    return messages


class SequenceMatcher(difflib.SequenceMatcher):
    """
    Добавляет возможность сравнивать последовательности из нехешируемых
    объектов.
    """
    def set_seq2(self, b):
        if b is self.b:
            return
        self.b = b
        self.matching_blocks = self.opcodes = None
        self.fullbcount = None
        self.__chain_b()

    def __chain_b(self):
        b = self.b
        self.b2j = b2j = _B2j()

        for i, elt in enumerate(b):
            indices = b2j.setdefault(elt, [])
            indices.append(i)

        # Purge junk elements
        junk = []
        isjunk = self.isjunk
        if isjunk:
            for elt in list(b2j.keys()):  # using list() since b2j is modified
                if isjunk(elt):
                    if elt not in junk:
                        junk.append(elt)
                    del b2j[elt]

        # Purge popular elements that are not junk
        popular = []
        n = len(b)
        if self.autojunk and n >= 200:
            ntest = n // 100 + 1
            for elt, idxs in list(b2j.items()):
                if len(idxs) > ntest:
                    if elt not in popular:
                        popular.append(elt)
                    del b2j[elt]

        # Now for x in b, isjunk(x) == x in junk, but the latter is much faster.
        # Sicne the number of *unique* junk elements is probably small, the
        # memory burden of keeping this set alive is likely trivial compared to
        # the size of b2j.
        self.isbjunk = junk.__contains__
        self.isbpopular = popular.__contains__


class _B2j(object):
    """
    Вспомогательный класс имитирующий часть интерфейса словаря, но способный
    хранить в качестве ключей нехешируемые объекты.

    Нужен для того, чтобы минимальными изменениями научить
    difflib.SequenceMatcher сравнивать последовательности из нехешируемых
    объектов.
    """
    def __init__(self):
        self._keys = []
        self._values = []
        return

    def setdefault(self, key, default):
        try:
            i = self._keys.index(key)
        except ValueError:
            self._keys.append(key)
            self._values.append(default)
            return default
        else:
            return self._values[i]

    def keys(self):
        return self._keys

    def items(self):
        return zip(self._keys, self._values)

    def get(self, key, default):
        try:
            i = self._keys.index(key)
        except ValueError:
            return default
        else:
            return self._values[i]

    def __delitem__(self, key):
        try:
            i = self._keys.index(key)
        except ValueError:
            raise KeyError(key)
        else:
            del self._keys[i]
            del self._values[i]
