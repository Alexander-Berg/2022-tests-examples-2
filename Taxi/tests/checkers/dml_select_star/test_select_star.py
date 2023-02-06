# pylint: disable=no-member
import test_utils


def test_error():
    remarks = test_utils.check_string('SELECT * FROM t')
    assert len(remarks) == 1

    expect_msg = (
        'Do not use SELECT * in the root query, '
        'it will break on the next column removal/addition.'
    )
    assert remarks[0].message == expect_msg


def test_ok():
    remarks = test_utils.check_string('SELECT a,b FROM t')
    assert not remarks

    remarks = test_utils.check_string('SELECT a,b FROM (SELECT * FROM t)')
    assert not remarks
