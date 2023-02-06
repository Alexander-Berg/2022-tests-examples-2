from operation_calculations.geosubventions import data_formats
from operation_calculations.geosubventions.multidraft import (
    multidraft_internal,
)
import operation_calculations.geosubventions.multidraft.report as report_lib


def test_get_multidraft_table_wiki(load_json):
    test_data = load_json('ticket_test_data.json')
    for single_test in test_data:
        result_raw = report_lib.get_draft_table_data(
            single_test['input'],
            only_hour_intervals=single_test['only_hour_intervals'],
        )
        result_wiki = report_lib.format_draft_table_wiki(result_raw)
        assert result_wiki == single_test['expected']


def test_rules_format(load_json):
    test_data = load_json('rules_format_data.json')
    polygons_zones_mapping = test_data['polygons_zones_mapping']
    task_result = data_formats.prepare_data_common(test_data['task'])
    result = multidraft_internal.format_rules_create(
        result_dicts={'': task_result},
        polygons_zones_mapping=polygons_zones_mapping,
    )
    assert result == test_data['formatted']
    warnings = multidraft_internal.get_empty_rates(
        result, task_result['polygons'],
    )
    assert warnings == test_data['warnings']
