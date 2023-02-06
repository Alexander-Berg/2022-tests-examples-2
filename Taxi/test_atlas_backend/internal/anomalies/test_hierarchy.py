import pytest

from atlas_backend.domain import anomaly
from atlas_backend.internal.anomalies import hierarchy as ah


@pytest.mark.config(
    ATLAS_BACKEND_ANOMALY_HIERARCHY=[
        {'source_name': 'uber', 'parent_name': 'all'},
        {'source_name': 'callcenter', 'parent_name': 'all'},
    ],
)
def test_hierarchy(web_context):
    hierarchy = ah.SourceHierarchy.from_context(web_context)
    assert hierarchy.get_children(anomaly.TaxiDowntimeOrderSource.ALL) == [
        anomaly.TaxiDowntimeOrderSource.UBER,
        anomaly.TaxiDowntimeOrderSource.CALLCENTER,
    ]
    assert hierarchy.get_children(anomaly.TaxiDowntimeOrderSource.UBER) == []
