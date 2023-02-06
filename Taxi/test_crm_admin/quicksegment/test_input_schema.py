import pytest

from crm_admin.quicksegment import error
from crm_admin.quicksegment import input_schema


@pytest.mark.parametrize(
    'schema, error_msg',
    [
        ({'id': 'id', 'label': 'label', 'type': 'type'}, 'must be a list'),
        ([{'id': 'id', 'type': 'type'}], 'missing required keys'),
        ([{'id': 'id', 'label': 'label'}], 'missing required keys'),
        ([{'label': 'label', 'type': 'type'}], 'missing required keys'),
        ([{'id': 'id', 'label': 'label', 'type': 'type'}], None),
        (
            [
                {'id': 'dup_id', 'label': 'label', 'type': 'type'},
                {'id': 'dup_id', 'label': 'label', 'type': 'type'},
            ],
            'duplicated id: dup_id',
        ),
    ],
)
def test_validate(schema, error_msg):
    if not error_msg:
        assert input_schema.validate(schema)
    else:
        with pytest.raises(error.ValidationError, match=error_msg):
            input_schema.validate(schema)
