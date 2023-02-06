import unittest
from taxi.robowarehouse.lib.misc import helpers


def assert_items_equal(result, expected):
    """
    result and expected have the same elements in the same number, regardless of their order
    """

    case = unittest.TestCase()
    case.maxDiff = None
    case.assertCountEqual(result, expected)


def convert_to_frontend_response(obj):
    res = helpers.enum_to_str_nested(obj)
    res = helpers.date_to_iso_format_nested(res)
    res = helpers.to_camel_nested(res)
    res = helpers.drop_none_nested(res)
    return res
