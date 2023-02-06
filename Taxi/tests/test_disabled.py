# pylint: disable=no-member
import test_utils


def test_error():
    remarks = test_utils.check_string('SELECT * FROM t')
    assert len(remarks) == 1

    cmd = '# sql-hints: disable=dml-select-star\nSELECT * FROM t'
    remarks = test_utils.check_string(cmd)
    assert not remarks
