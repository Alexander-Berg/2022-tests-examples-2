import os

import pytest

import sandbox.serviceq.journal as qjournal

JOURNAL_FILE_SIZE = 1000


@pytest.fixture()
def operation():
    return qjournal.Operation(0, 123, [42, "abc"])


class TestJournal(object):
    @staticmethod
    def __journal(tmpdir):
        journal_path = os.path.join(str(tmpdir), "test.journal")
        return qjournal.OperationJournal(journal_path, file_size=JOURNAL_FILE_SIZE)

    @staticmethod
    def __fill_journal(journal, operation):
        op = operation
        data_size = qjournal.OperationJournal.Header.DATA_OFFSET
        file_size = journal.file_size
        for i in xrange(1, JOURNAL_FILE_SIZE + 1):
            op = qjournal.Operation(op.operation_id + 1, op.method, op.args)
            journal.add(op, op.operation_id)
            op_size = len(journal.pack_operation(op)) + qjournal.ST_SIZE.size
            data_size += op_size
            if data_size >= file_size:
                file_size <<= 1
            assert journal.counter == i
            assert journal.operation_id == op.operation_id
            assert journal.data_size == data_size
            assert journal.file_size == file_size
        return op

    def test__init(self, tmpdir, operation):
        journal = self.__journal(tmpdir)
        assert journal.data_size == qjournal.OperationJournal.Header.DATA_OFFSET
        assert journal.file_size == JOURNAL_FILE_SIZE
        assert journal.counter == 0
        assert journal.operation_id == 0
        assert journal.newly_created
        assert list(journal) == []

    def test__fill(self, tmpdir, operation):
        journal = self.__journal(tmpdir)
        op = self.__fill_journal(journal, operation)
        assert list(journal) == [qjournal.Operation(i, op.method, op.args) for i in xrange(1, op.operation_id + 1)]

    def test__persistence(self, tmpdir, operation):
        journal = self.__journal(tmpdir)
        op = self.__fill_journal(journal, operation)
        journal_path = journal.path
        journal_counter = journal.counter
        journal_operation_id = journal.operation_id
        journal_data_size = journal.data_size
        journal_file_size = journal.file_size
        del journal
        journal = qjournal.OperationJournal(journal_path)
        assert not journal.newly_created
        assert journal.counter == journal_counter
        assert journal.operation_id == journal_operation_id
        assert journal.data_size == journal_data_size
        assert journal.file_size == journal_file_size
        assert list(journal) == [qjournal.Operation(i, op.method, op.args) for i in xrange(1, op.operation_id + 1)]
