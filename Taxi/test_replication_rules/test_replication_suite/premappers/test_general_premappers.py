import datetime
import pytest

from replication_suite.premappers import general_premappers


_DOC = {
    'datetime_type': 1234567890,
    'interval_type': 123456789000000,
    'string_type': b'Hello',
}


@pytest.mark.parametrize(
    'fields, doc, expected_doc, premapper',
    (
        (
            ('datetime_type',),
            _DOC,
            {
                'datetime_type': datetime.datetime(
                    1970, 1, 1, 0, 20, 34, 567890,
                ),
                'interval_type': 123456789000000,
                'string_type': b'Hello',
            },
            general_premappers.int_microseconds_to_py_datetime,
        ),
        (
            ('interval_type',),
            _DOC,
            {
                'datetime_type': 1234567890,
                'interval_type': datetime.timedelta(days=1428, seconds=77589),
                'string_type': b'Hello',
            },
            general_premappers.int_microseconds_to_py_interval,
        ),
        (
            ('string_type',),
            _DOC,
            {
                'datetime_type': 1234567890,
                'interval_type': 123456789000000,
                'string_type': 'Hello',
            },
            general_premappers.byte_string_to_utf8,
        ),
    ),
)
def test_premapper(fields, doc, expected_doc, premapper):
    doc_premapper = premapper(fields)
    for mapped_doc in doc_premapper(doc):
        assert mapped_doc == expected_doc
