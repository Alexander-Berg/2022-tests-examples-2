# pylint: disable=C5521
from collections import defaultdict
import json

import pytest


class SubventionsScheduleContext:
    def __init__(self):
        self.schedules = []
        self.calls = defaultdict(int)
        self.requests = {'schedule': []}

        self.schedule = None

    def set_schedules(self, schedules):
        self.schedules = schedules


@pytest.fixture
def ssch(mockserver):
    ssch_context = SubventionsScheduleContext()

    @mockserver.json_handler(
        '/subvention-schedule/internal/subvention-schedule/v1/schedule',
    )
    async def _mock_schedule(request_data):
        ssch_context.calls['schedule'] += 1
        ssch_context.requests['schedule'].append(
            json.loads(request_data.get_data()),
        )

        return {'schedules': ssch_context.schedules}

    ssch_context.schedule = _mock_schedule

    return ssch_context
