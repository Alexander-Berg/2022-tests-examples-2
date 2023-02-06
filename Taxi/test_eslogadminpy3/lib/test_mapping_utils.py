import pytest

from eslogadminpy3.lib import mapping_utils


@pytest.mark.parametrize(
    'mapping, no_changes, template_name',
    [
        ({}, True, 'taxi-wont-change'),
        ('mapping_wont_change_es_7.json', True, 'taxi-wont-change'),
        ('mapping_wont_change_es_7.json', False, 'taxi-timings-mapping'),
        ('mapping_will_change_es_7.json', False, 'taxi-timings-mapping'),
        ('mapping_will_change_es_7.json', False, 'taxi-wont-change'),
        (
            'mapping_will_change_for_dynamic_rules_es_7.json',
            False,
            'taxi-timings-mapping',
        ),
        (
            'mapping_will_change_for_dynamic_rules_es_7.json',
            True,
            'taxi-wont-change',
        ),
    ],
)
def test_apply_white_list(
        load_json, cron_context, mapping, no_changes, template_name,
):
    if isinstance(mapping, str):
        mapping = load_json(mapping)
    mapping = mapping.get('mappings', {})

    result = mapping_utils.apply_white_list_rules(
        mapping=mapping,
        template_name=template_name,
        static_rules=cron_context.service_schemas.static_includes,
        dynamic_rules=cron_context.service_schemas.dynamic_includes,
        es_version=7,
        log_extra=None,
    )
    assert (result == mapping) == no_changes


@pytest.mark.parametrize(
    'mapping, no_changes, template_name',
    [
        ({}, True, 'taxi-wont-change'),
        ('mapping_wont_change_es_7.json', True, 'taxi-any'),
        ('mapping_will_change_es_7.json', False, 'taxi-any'),
        ('mapping_will_change_for_dynamic_rules_es_7.json', False, 'taxi-any'),
    ],
)
def test_apply_black_list(
        load_json, cron_context, mapping, no_changes, template_name,
):
    if isinstance(mapping, str):
        mapping = load_json(mapping)
    mapping = mapping.get('mappings', {})

    result = mapping_utils.apply_black_list_rules(
        mapping=mapping,
        template_name=template_name,
        static_rules=cron_context.service_schemas.static_excludes,
        dynamic_rules=cron_context.service_schemas.dynamic_excludes,
        es_version=7,
        log_extra=None,
    )
    assert (result == mapping) == no_changes
