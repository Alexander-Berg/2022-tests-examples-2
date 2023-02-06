import pytest
from metrika.pylib.clickhouse.lib import ClickHouse
from metrika.pylib.vault import Secret
from yatest.common import get_param


@pytest.fixture(scope='session')
def clickhouse():
    host = get_param('host')
    if not host:
        raise ValueError('Укажите хост КХ через --test-param host=XXX')
    port = get_param('port')
    if not port:
        raise ValueError('Укажите порт КХ через --test-param port=XXX')
    port = int(port)
    user = 'robot-metrika-test'
    password = Secret(uuid='sec-01cq6h5rtj649gg8h94zwqshc8', auth_type='oauth').get_latest_secret()['clickhouse-password']
    return ClickHouse(host=host, port=port, user=user, password=password)
