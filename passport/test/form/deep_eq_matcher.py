# -*- coding: utf-8 -*-
from hamcrest.core.base_matcher import BaseMatcher
from passport.backend.core.test.test_utils.utils import (
    _diff_opcode_to_messages,
    _SequenceMatcher,
    uniq,
)


class DeepEqual(BaseMatcher):
    def __init__(self, expected):
        self.expected = expected

    def _matches(self, actual):
        return actual == self.expected

    def describe_to(self, description):
        description.append_text('should be ').append_description_of(self.expected)

    def describe_mismatch(self, actual, description):
        a = actual
        b = self.expected

        if isinstance(a, dict) and isinstance(b, dict):
            a = sorted(a.items())
            b = sorted(b.items())

        if isinstance(a, set) and isinstance(b, set):
            description.append_text(
                '\nIn first: %s\nIn second: %s' % (
                    uniq(a, b),
                    uniq(b, a),
                ),
            )
        elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
            matcher = _SequenceMatcher(a=b, b=a)
            messages = []
            for tag, start_b, end_b, start_a, end_a in matcher.get_opcodes():
                messages += _diff_opcode_to_messages(tag, a[start_a:end_a], b[start_b:end_b])
            description.append_text(
                'sequences not equal\n '
                'Do the transformations in order to get first from second:\n '
                '%s\n' % '\n'.join(messages),
            )
        else:
            description.append_text('was <%s>' % a)


def deep_eq(expected):
    """Матчится, если объект равен ожидаемому

    :param expected: Ожидаемый объект, с которым сравниваем

    Сравнивает пришедший объект с изначально заданным ``expected`` на равенство
    и дает расширенное описание в случае проблем

    Примеры::

        assert_that(some_obj, deep_eq(expected))
    """
    return DeepEqual(expected)
