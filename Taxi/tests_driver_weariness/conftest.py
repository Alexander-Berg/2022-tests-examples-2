import json

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from driver_weariness_plugins import *  # noqa: F403 F401
import pytest

from tests_driver_weariness import const


class CshContext:
    def __init__(self):
        self.events = {}
        self.times_called = 0

    def reset(self):
        self.events = {}
        self.times_called = 0

    def set_events(self, events):
        self.events = events


@pytest.fixture(name='csh_mock')
def _csh_mock(mockserver):
    csh_context = CshContext()

    @mockserver.json_handler('/contractor-status-history/extended-events')
    def _mock_csh_events(request):
        csh_context.times_called += 1

        assert request.json['verbose'] is True

        contractors = []
        for contractor in request.json['contractors']:
            profile = contractor['park_id'] + '_' + contractor['profile_id']
            if profile in csh_context.events:
                contractor['events'] = csh_context.events[profile]
                contractors.append(contractor)

        return {'contractors': contractors}

    return csh_context


@pytest.fixture(name='csh_fixture', autouse=True)
def _csh_fixture(csh_mock, request):
    csh_mock.reset()

    for marker in request.node.iter_markers(const.CSH_MARKER):
        if marker.kwargs:
            csh_mock.set_events(**marker.kwargs)

    yield csh_mock

    csh_mock.reset()


@pytest.fixture(name='contractor_transport_updates', autouse=True)
def mock_contractor_transport(request, mockserver, load_json):
    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/updates',
    )
    def _mock_transport_active(request):
        assert request.method == 'GET'
        data = load_json('contractors_transport.json')
        return mockserver.make_response(response=json.dumps(data))


def pytest_configure(config):
    config.addinivalue_line(
        'markers', f'{const.CSH_MARKER}: contractor status history',
    )


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(pytest.mark.geoareas(filename='geoareas.json'))
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))
