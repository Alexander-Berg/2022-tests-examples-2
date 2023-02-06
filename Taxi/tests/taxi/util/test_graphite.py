# pylint: disable=redefined-outer-name
import time

import pytest

from taxi.util import graphite


@pytest.fixture
def graphite_patch(monkeypatch):
    patch = {
        'ENV': 'test',
        'GRAPHITE_SERVER': 'server',
        'GRAPHITE_PORT': 121212,
    }
    for key, value in patch.items():
        monkeypatch.setattr(graphite, key, value)
    return patch


@pytest.mark.now('2017-11-01T01:10:00+0300')
@pytest.mark.parametrize('timestamp', [None, 12121212])
async def test_send(graphite_patch, patch, timestamp):
    class WriterMock:
        def __init__(self):
            self.datas = []
            self.closed = False

        def write(self, data):
            self.datas.append(data)

        def close(self):
            self.closed = True

    writer = WriterMock()

    @patch('asyncio.open_connection')
    async def open_connection(server, port):
        return None, writer

    await graphite.send('metric', 'value', timestamp)

    timestamp = timestamp or int(time.time())

    assert open_connection.calls == [
        {
            'server': graphite_patch['GRAPHITE_SERVER'],
            'port': graphite_patch['GRAPHITE_PORT'],
        },
    ]
    assert writer.datas == [b'metric value %d\n' % timestamp]
    assert writer.closed


async def test_send_taxi_cluster_metric(graphite_patch, patch):
    @patch('taxi.util.graphite.send')
    async def send(metric, value, timestamp):
        pass

    await graphite.send_taxi_cluster_metric('metric', 'value', 12121212)

    env = graphite_patch['ENV']
    assert send.calls == [
        {
            'metric': 'cluster.geo.taxi.service_stats.%s.metric' % env,
            'value': 'value',
            'timestamp': 12121212,
        },
    ]
