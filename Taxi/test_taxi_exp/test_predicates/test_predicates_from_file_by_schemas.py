import json
import logging

import jsonschema

logger = logging.getLogger(__name__)


async def test_file_with_predicates_by_schemas(
        taxi_exp_client, relative_load_jsons_from_file,
):
    predicates = relative_load_jsons_from_file('predicates.txt')
    validator = taxi_exp_client.app.json_validators[
        'predicates.yaml#/definitions/CommonPredicate'
    ]
    errors = False
    unique = set()
    unique_count = 0
    index = 0
    for index, predicate in enumerate(predicates):
        try:
            validator.validate(predicate)
            raw_predicate = json.dumps(predicate)
            if raw_predicate not in unique:
                unique_count += 1
                unique.add(raw_predicate)
            else:
                logger.debug(
                    'Duplicate: index - %s, predicate - %s',
                    index,
                    raw_predicate,
                )
        except (jsonschema.ValidationError, json.decoder.JSONDecodeError):
            logger.exception('Index: %s', index)
            errors = True
    assert not errors
    assert (index + 1) == unique_count
