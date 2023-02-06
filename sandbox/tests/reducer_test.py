import json
import pytest
from io import StringIO
from contextlib import redirect_stdout
from sandbox.projects.k50.sow_map_reduce import reducer

HISTORICAL_INITIAL_CONTENT = [
    json.dumps({"_k50_query_id": 1, "_k50_date": "2020-01-01", "_k50_uploaded_at": 100}),
    json.dumps({"_k50_query_id": 1, "_k50_date": "2020-01-01", "_k50_uploaded_at": 90}),
    json.dumps({"_k50_query_id": 1, "_k50_date": "2020-01-08", "_k50_uploaded_at": 90}),
    json.dumps({"_k50_query_id": 1, "_k50_date": "2020-01-08", "_k50_uploaded_at": 80}),
    json.dumps({"_k50_query_id": 2, "_k50_date": "2020-01-08", "_k50_uploaded_at": 80}),
    json.dumps({"_k50_query_id": 2, "_k50_date": "2020-01-08", "_k50_uploaded_at": 70}),
]
NON_HISTORICAL_INITIAL_CONTENT = [
    json.dumps({"_k50_query_id": 1, "_k50_uploaded_at": 100}),
    json.dumps({"_k50_query_id": 1, "_k50_uploaded_at": 90}),
    json.dumps({"_k50_query_id": 1, "_k50_uploaded_at": 90}),
    json.dumps({"_k50_query_id": 1, "_k50_uploaded_at": 80}),
    json.dumps({"_k50_query_id": 2, "_k50_uploaded_at": 80}),
    json.dumps({"_k50_query_id": 2, "_k50_uploaded_at": 70}),
]

HISTORICAL_EXP_TABLE = '\n'.join([
    json.dumps({"_k50_query_id": 1, "_k50_date": "2020-01-01", "_k50_uploaded_at": 100}),
    json.dumps({"_k50_query_id": 1, "_k50_date": "2020-01-08", "_k50_uploaded_at": 90}),
    json.dumps({"_k50_query_id": 2, "_k50_date": "2020-01-08", "_k50_uploaded_at": 80}),
    ''
])
NON_HISTORICAL_EXP_TABLE = '\n'.join([
    json.dumps({"_k50_query_id": 1, "_k50_uploaded_at": 100}),
    json.dumps({"_k50_query_id": 2, "_k50_uploaded_at": 80}),
    ''
])


@pytest.mark.parametrize("testdata, expected", [(HISTORICAL_INITIAL_CONTENT, HISTORICAL_EXP_TABLE),
                                                (NON_HISTORICAL_INITIAL_CONTENT, NON_HISTORICAL_EXP_TABLE)])
def test_historical_reducer(testdata, expected):
    res = StringIO()
    with redirect_stdout(res):
        reducer.reducer(testdata)

    assert expected == res.getvalue()
