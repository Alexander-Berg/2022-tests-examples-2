from atlas.service_utils.geosubventions.ticket_preparation import format_draft_table_wiki, get_draft_table_data
from .common import load_test_json
import pytest

test_data = load_test_json('ticket_test_data.json')

@pytest.mark.parametrize(
    "single_test",
    test_data
)
def test_get_multidraft_table_wiki(single_test):
    result_raw = get_draft_table_data(single_test['input'], only_hour_intervals=single_test['only_hour_intervals'])
    result_wiki = format_draft_table_wiki(result_raw)
    assert result_wiki == single_test['expected']

