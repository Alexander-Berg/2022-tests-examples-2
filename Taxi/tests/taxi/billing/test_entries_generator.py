# pylint: disable=redefined-outer-name
import json

import pytest

from taxi.billing import util
from taxi.billing.entries_generator import _generate
import taxi.util.aiohttp_kit as api_kit


@pytest.fixture
def templates_by_name():
    result = _generate.load_templates_from_dir(
        _generate.TEMPLATES_DIR, _generate.SUPPORTED_FILE_EXTENSIONS,
    )
    return result


@pytest.mark.parametrize(
    'context,expected_values,expected_formatted_strings',
    [
        (
            {
                'alias_id': 'some_alias_id',
                'driver': {
                    'park_id': 'some_park_id',
                    'driver_uuid': 'some_uuid',
                },
                'flag': True,
                'integer': 228,
                'number': 3.22,
            },
            {
                'flag': True,
                'integer': 228,
                'number': 3.22,
                'alias_id': 'some_alias_id',
                'driver': {
                    'park_id': 'some_park_id',
                    'driver_uuid': 'some_uuid',
                },
                'driver.park_id': 'some_park_id',
                'driver.driver_uuid': 'some_uuid',
            },
            {
                'taximeter_driver_id/{driver.park_id}/{driver.driver_uuid}': (
                    'taximeter_driver_id/some_park_id/some_uuid'
                ),
                'alias_id/{alias_id}': 'alias_id/some_alias_id',
                'flag/{flag}/number/{number}/integer/{integer}': (
                    'flag/True/number/3.22/integer/228'
                ),
            },
        ),
    ],
)
def test_context_wrapper(context, expected_values, expected_formatted_strings):
    wrapper = _generate.ContextWrapper('', context)

    actual_values = {
        key: wrapper.context_val(key)
        for key, expected_value in expected_values.items()
    }
    assert actual_values == expected_values

    actual_formatted_strings = {
        key: wrapper.format_str(key)
        for key, expected_value in expected_formatted_strings.items()
    }
    assert actual_formatted_strings == expected_formatted_strings


def test_validate_templates(templates_by_name):
    json_validators = api_kit.JsonValidatorStore(_generate.TEMPLATE_SCHEME_DIR)
    json_validator = json_validators[
        'template_scheme.yaml#/definitions/Template'
    ]
    for tpl in templates_by_name.values():
        json_validator.validate(tpl)


def test_actual_entries_generators(templates_by_name):
    for tpl_name, tpl in templates_by_name.items():
        for example in tpl['examples']:
            expected_actions = example['expected_actions']
            expected_entries = example['expected_entries']
            context = example['context']
            actual_entries = _generate.generate_entries(tpl_name, context)
            assert actual_entries == expected_entries
            _check_duplicate_accounts(actual_entries)
            actual_actions = _generate.generate_actions(
                tpl_name, context, _generate.DummyActions(),
            )
            assert _format_fn(actual_actions) == expected_actions


def _check_duplicate_accounts(actual_entries):
    def _key(entry):
        return (
            entry['entity_external_id'],
            entry['agreement_id'],
            entry['sub_account'],
            entry['currency'],
        )

    groupped = util.group_by(actual_entries, key=_key)
    for key, group in groupped.items():
        if len(group) > 1:
            raise RuntimeError(f'Several entries for key={key}')


def _format_fn(funcs):
    result = []
    for func in funcs:
        if hasattr(func, 'func'):
            # functools.partial wrapped
            result.append(
                {
                    'func': func.func.__name__,
                    'keywords': json.loads(util.to_json(func.keywords)),
                },
            )
            continue
        result.append({'func': func.__name__, 'keywords': {}})
    return result
