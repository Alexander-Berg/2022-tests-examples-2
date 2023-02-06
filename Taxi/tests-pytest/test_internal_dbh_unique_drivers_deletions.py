import bson
import pytest

from taxi.internal import dbh


@pytest.inline_callbacks
def test_insert_drivers():
    current_timestamp = 123456789

    class Doc(dbh.unique_drivers_deletions.Doc):

        @classmethod
        def _insert(cls, *args, **kwargs):
            query = args[0]
            for i, doc in enumerate(query):
                doc[cls.deleted_ts] = bson.timestamp.Timestamp(current_timestamp, i)

            return super(Doc, cls)._insert(*args, **kwargs)

    doc_ids = ['test_id_1', 'test_id_2']
    yield Doc.insert_drivers(doc_ids)
    inserted = yield dbh.unique_drivers_deletions.Doc.find_many({})

    assert len(doc_ids) == len(inserted)
    for i, doc in enumerate(inserted):
        assert doc.doc_id == doc_ids[i]
        assert doc.deleted_ts == bson.timestamp.Timestamp(current_timestamp, i)
