import unittest


class DmpTestCase(unittest.TestCase):
    def assert_records_equal(self, expected, actual):
        assert_records_equal(expected, actual, comparator=self.assertEqual)

    def assertItemsEqual(self, left, right):
        return self.assertCountEqual(left, right)


def assert_records_equal(expected, actual, comparator=None):
    """Проверяет, что списки записей типа Record идентичны.

       Почему лучше использовать этот хелпер, чем другие методы?

       Потому что pytest и PyCharm умееют показывать понятный diff
       для словарей, а тип Record – не поддерживают. В понятном
       диффе удобно искать проблемы."""
    def to_dict(value):
        if isinstance(value, dict):
            return value
        else:
            return value.to_dict()

    expected = list(map(to_dict, expected))
    actual = list(map(to_dict, actual))

    if comparator is None:
        assert expected == actual
    else:
        comparator(expected, actual)
