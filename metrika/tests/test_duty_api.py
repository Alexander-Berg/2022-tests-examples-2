import six

from metrika.pylib.mtapi.duty import DutyAPI, DutyAPIException
from metrika.pylib.structures.dotdict import DotDict
from metrika.pylib.log import init_logger
import pytest


init_logger('mtutils', stdout=True)
init_logger('urllib3', stdout=True)


@pytest.fixture(scope='session')
def api():
    yield DutyAPI(url='https://mtapi01kt.mtrs.yandex-team.ru/v1/duty')


def test_get_all(api):
    data = api.all_duties

    assert isinstance(data, DotDict)
    assert isinstance(data.on_call, DotDict)
    assert isinstance(data.on_call.login, six.string_types)

    assert len(data.keys()) > 1


def test_get_one_duty(api):
    data = api.get_duty('admin')

    assert isinstance(data.login, six.string_types)


def test_set_duty(api):
    data = api.set_duty('admin', 'velom')

    assert isinstance(data, bool) and data
    assert api.get_duty('admin').login == 'velom'

    data = api.set_duty('admin', 'frenz')

    assert isinstance(data, bool) and data
    assert api.get_duty('admin').login == 'frenz'


def test_get_unexists_duty(api):
    with pytest.raises(DutyAPIException) as e:
        api.get_duty('ololo')
        assert isinstance(e.message, six.string_types) and e.message

        assert 'Unknown duty_name' in e.message
