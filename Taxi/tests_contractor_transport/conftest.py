# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from contractor_transport_plugins import *  # noqa: F403 F401

import tests_contractor_transport.driver_status


@pytest.fixture(autouse=True)
def driver_statuses_request(mockserver, load_json):
    @mockserver.handler('/driver-status/v2/statuses/updates')
    def _mock_driver_statuses(request):

        statuses = (
            tests_contractor_transport.driver_status.load_drv_statuses_mock(
                load_json, 'driver_status_statuses_response.json',
            )
        )
        result = tests_contractor_transport.driver_status.build_statuses_fbs(
            statuses['revision'], statuses['statuses'],
        )

        return mockserver.make_response(
            response=result,
            headers={'Content-Type': 'application/x-flatbuffers'},
            status=200,
        )
