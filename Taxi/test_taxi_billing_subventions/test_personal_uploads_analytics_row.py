import pytest

from taxi_billing_subventions.personal_uploads import models


@pytest.mark.parametrize(
    'row_json, expected_hash',
    [('row.json', '89efc1df7d78789e775349c9102269f8737e5e40')],
)
@pytest.mark.nofilldb()
def test_get_deterministic_hash(row_json, expected_hash, load_py_json_dir):
    row: models.AnalyticsRow = load_py_json_dir(
        'test_get_deterministic_hash', row_json,
    )
    assert row.get_deterministic_hash() == expected_hash
