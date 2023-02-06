import pytest

from taxi_exp.util import exceptions
from taxi_exp.util import values

SCHEMA = """
type: object
additionalProperties: false
properties:
    option:
        type: string"""

SCHEMA_WITH_KEYWORD_PROPERTY = """
type: object
additionalProperties: false
properties:
    type:
        type: string"""

SCHEMA_WITHOUT_ADDITIONAL_PROPERTIES = """
type: object
properties:
    type:
        type: string"""

SCHEMA_WITH_ADDITIONAL_PROPERTIES_WITHOUT_REASON = """
type: object
additionalProperties: true
required:
  - type
properties:
    type:
        type: string
    another:
        type: number"""

SCHEMA_WITH_ADDITIONAL_PROPERTIES_AND_REASON = """
type: object
additionalProperties: true
x-taxi-additional-properties-true-reason: cause i can
required:
  - type
properties:
    type:
        type: string
    another:
        type: number"""


@pytest.mark.parametrize(
    'schema,is_correct',
    [
        (SCHEMA, True),
        (SCHEMA_WITH_KEYWORD_PROPERTY, True),
        (SCHEMA_WITHOUT_ADDITIONAL_PROPERTIES, False),
        (SCHEMA_WITH_ADDITIONAL_PROPERTIES_WITHOUT_REASON, False),
        (SCHEMA_WITH_ADDITIONAL_PROPERTIES_AND_REASON, True),
    ],
)
@pytest.mark.config(
    EXP_VALUES_SCHEMA_SETTINGS={
        'block_additionalproperties_true': {'for_all': True, 'for_some': []},
    },
)
async def test_get_and_check_schema(taxi_exp_client, schema, is_correct):
    processor = values.ValuesProcessor.from_context(
        context=taxi_exp_client.app, schema=schema,
    )
    if is_correct:
        processor.check_schema()
    else:
        with pytest.raises(exceptions.RequestError400):
            processor.check_schema()
