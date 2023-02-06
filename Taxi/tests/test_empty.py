# pylint: disable=no-member
import test_utils


def test_empty():
    remarks = test_utils.check_string('')
    assert not remarks
