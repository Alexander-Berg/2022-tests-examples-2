import pytest

from taxi_billing_subventions.common import models


@pytest.mark.parametrize('test_case_json', ['fit.json', 'unfit.json'])
@pytest.mark.nofilldb()
def test_from_subvention_journal(test_case_json, load_py_json):
    test_case = load_py_json(test_case_json)
    journal = test_case['journal']
    kind = test_case['kind']
    expected = test_case['expected']
    actual = models.doc.InfoJournal.from_subvention_journal(
        journal, kind, None,
    )
    assert actual == expected
