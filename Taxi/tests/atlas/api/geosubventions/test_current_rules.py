from .common import load_test_json
from atlas.api.geosubventions.current_rules_adapters import convert_old_rules_to_draft_intervals


def test_convert_old_rules_to_draft_intervals():
    old_raw_rules = load_test_json("old_api_select_responce.json")['subventions']
    expected = load_test_json("current_draft_rules_expected.json")
    rez = convert_old_rules_to_draft_intervals(old_raw_rules)
    rez = sorted(rez, key=lambda r: (r['interval']['start_dayofweek'], r['interval']['start_time'],
                                 r['interval']['end_dayofweek'], r['interval']['end_time'], r['geoareas']))
    assert rez == expected
