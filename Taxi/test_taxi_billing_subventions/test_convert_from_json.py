import pytest

from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'source_json, expected_json',
    [
        ('discount_w_value.json', 'expected_discount_w_value.json'),
        ('discount_wo_value.json', 'expected_discount_wo_value.json'),
        ('discount_w_limit.json', 'expected_discount_w_limit.json'),
    ],
)
@pytest.mark.nofilldb()
def test_discount_object(source_json, expected_json, load_py_json_dir):
    source_obj, expected_obj = load_py_json_dir(
        'test_discount_object', source_json, expected_json,
    )
    actual = models.doc.OrderDiscount.from_json(source_obj)
    assert actual == expected_obj
