from metrika.pylib.maas import MaaS
from metrika.pylib.maas import exceptions
from metrika.pylib.log import base_logger, init_logger
import pytest
import time

logger = base_logger.getChild(__name__)
init_logger('mtutils', stdout=True)

HOST = 'velom-caas-dev.mtrs.yandex.ru'
# TODO: замокать, конечно


@pytest.fixture
def maas_instance():
    m = MaaS(host=HOST)
    m.DEFAULT_TTL = 60
    yield m
    if m.status == 'active' and m.properties.get('ttl', 0) == 0:
        m.delete()


@pytest.fixture(scope='session')
def created_instance():
    m = MaaS(host=HOST)
    m.create(ttl=600)
    yield m
    if m.status == 'active' and m.properties.get('ttl', 0) == 0:
        m.delete()


@pytest.fixture
def mock_status_dead(monkeypatch):
    def mock_status_response(*args, **kwargs):
        return dict(
            status='dead',
            ports=dict(
                mysql=1111,
            ),
        )
    monkeypatch.setattr(MaaS, '_http_query', mock_status_response)
    yield


def test_create(maas_instance):
    """
    :type maas_instance: MaaS
    """
    assert maas_instance.id is None

    ports = maas_instance.create()
    assert isinstance(ports, dict)
    assert maas_instance.id is not None
    assert maas_instance.status == 'active'


def test_wrong_create_parameters(maas_instance):
    """
    :type maas_instance: MaaS
    """
    with pytest.raises(exceptions.MaaSException):
        maas_instance.create(ttl=-25)


def test_too_little_ttl(maas_instance):
    """
    :type maas_instance: MaaS
    """
    maas_instance.create(ttl=1)
    time.sleep(20)
    with pytest.raises(exceptions.GetStatusError):
        maas_instance.get_status()


def test_failed_create(maas_instance, mock_status_dead):
    """
    :type maas_instance: MaaS
    """
    with pytest.raises(exceptions.CreateError):
        maas_instance.create()


def test_update(created_instance):
    """
    :type created_instance: MaaS
    """
    data = created_instance.update(ttl=400, name='test')
    assert isinstance(data, dict)


def test_wrong_update_parameters(created_instance):
    """
    :type created_instance: MaaS
    """
    with pytest.raises(exceptions.UpdateError):
        created_instance.update(ttl=-1)


def test_delete(created_instance):
    """
    :type created_instance: MaaS
    """
    assert created_instance.delete()
    assert created_instance.status == 'deleted'


def test_failed_delete(created_instance, mock_status_dead):
    """
    :type created_instance: MaaS
    """
    with pytest.raises(exceptions.DeleteError):
        created_instance.delete()
    assert created_instance.status == 'dead'
