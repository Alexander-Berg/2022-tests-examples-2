import pytest

from taxi.core import arequests
from taxi.external import solomon_push
from taxi_maintenance.stuff import import_permits_monitoring


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
@pytest.mark.now('2020-09-08 17:12:53+03')
def test_import_permits_monitoring(mock, patch, load, monkeypatch):
    @patch('taxi.core.arequests.post')
    def solomon_request(url, json=None, **kwargs):
        return arequests.Response(status_code=200)

    yield import_permits_monitoring.do_stuff()
    calls = solomon_request.calls
    assert len(calls) == 1
    assert calls[0]['url'] == solomon_push.SOLOMON_DEFAULT_AGENT_URL

    sensors = calls[0]['json']['sensors']
    assert len(sensors) == 2

    areas = ['moscow', 'moscow_oblast']
    values = [
        10,  # moscow was updated 10 minutes ago
        7,  # moscow_oblast was updated 7 minutes age
    ]
    for sensor, area, value in zip(sensors, areas, values):
        assert sensor['kind'] == 'IGAUGE'
        assert sensor['labels'] == {
            'application': 'taxi_maintenance',
            'sensor': 'permits.{}.minutes-from-last-update'.format(area),
        }
        assert sensor['value'] == value
