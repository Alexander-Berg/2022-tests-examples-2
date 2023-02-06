

from app.tvm import get_waffles_tvm_ticket
from app.engines.molly_engine import MollyEngine
from builtins import map
import pytest


def test_get_waffles_tvm_ticket():
    ticket = get_waffles_tvm_ticket()
    assert ticket is not None


@pytest.mark.filterwarnings("ignore")
def test_waffles():
    get_waffles_tvm_ticket()
    vhosts = MollyEngine._get_virtual_hosts('2a02:6b8:0:3400::519')
    assert 'debby-test.sec.yandex-team.ru' in vhosts


def test_molly_target_prepare():
    t1 = 'ya1.ru'
    t2 = 'ya23.ru'
    t3 = 'yango.ru'
    t4 = 'www.yango.ru'
    t5 = 'yango.com.tr'
    t6 = 'yango.com'
    t7 = 'yango.co.il'
    t8 = 'an.yandex.ru'

    all_targets = [t1, t2, t3, t4, t5, t6, t7, t8]
    targets_to_scan = MollyEngine._prepare_targets(all_targets)
    targets = list([x[0][0] for x in targets_to_scan])

    assert list([t in [t1, t3, t5, t6] for t in targets])
    assert list([t in targets for t in [t1, t3, t5, t6]])
