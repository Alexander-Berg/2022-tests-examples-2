import pytest

from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'test_case_json',
    ['new_doc.json', 'old_doc.json', 'only_required_fields.json'],
)
def test_marshalling_subventions_update_needed(test_case_json, load_py_json):
    test_case = load_py_json(test_case_json)
    doc_data = test_case['doc_data']
    data = models.doc.SubventionsUpdateNeededInput.load(doc_data)
    assert data.dump().items() <= doc_data.items()
