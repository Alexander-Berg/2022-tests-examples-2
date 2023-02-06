# pylint: disable=no-member
import test_utils


def test_ok():
    remarks = test_utils.check_string('CREATE INDEX x ON y(z)')
    assert len(remarks) == 1

    expect_msg = (
        'CREATE/DROP INDEX without CONCURENTLY might lock the whole table.'
    )
    assert remarks[0].message == expect_msg


def test_error():
    remarks = test_utils.check_string('CREATE INDEX CONCURRENTLY x ON y(z)')
    assert not remarks


def test_disabled():
    remarks = test_utils.check_string(
        '-- sql-hints: disable=ddl-nonconcurrent-index\n'
        'CREATE INDEX x ON y(z)',
    )
    assert not remarks
