from atlas.service_utils.geosubventions.core.scarlett import ScarlettCalculator
from src.tests.atlas.api.geosubventions.common import load_test_json
import pandas as pd

def test_scarlett():
    scarlet_input = load_test_json('scarlett_input.json')
    sc = ScarlettCalculator(pd.DataFrame.from_dict(scarlet_input))
    draft_rules = load_test_json('scarlett_draft_rules.json')
    result = sc.enrich_rules(draft_rules, step_up=0.1, step_down=0.1, round_to=5)
    result = sorted(result, key=lambda r: (r['interval']['start_dayofweek'], r['interval']['start_time'],
                                          r['geoareas']))
    expected = load_test_json('scarlett_expected_responce.json')
    assert result == expected
