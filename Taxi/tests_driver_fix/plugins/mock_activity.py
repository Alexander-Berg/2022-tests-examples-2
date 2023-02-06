import pytest


@pytest.fixture(name='activity', autouse=True)
def mock_activity(mockserver):
    class Context:
        def __init__(self):
            self.activity = {}
            self.mock_dms = {}

        def add_driver(self, unique_driver_id, activity):
            self.activity[unique_driver_id] = activity

    context = Context()

    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _mock_dms(request):
        doc = request.json
        ids = doc['unique_driver_ids']
        response_items = []
        for udid in ids:
            response_items.append(
                {'unique_driver_id': udid, 'value': context.activity[udid]},
            )
        return {'items': response_items}

    context.mock_dms = _mock_dms

    return context
