# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from discounts_admin_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture()
def tvm_ticket():
    # Generated via `tvmknife unittest service -s 123 -d 2345`
    return (
        '3:serv:CBAQ__________9_IgUIexCpEg:Hv3ePYa'
        'kdwt-qi_HD0jhU8WoNj-JX_2wxDfwiA7cwb38Npgw'
        'zCsgm0quaT38eR2lXX1HcF03_BdSbdK-5Hxh-mDTm'
        'xcLNOd0VuMBRN90paNzV8mmGbKqe-tpYP6IPZRFmt'
        'cepZdEYlDxKd1UI36ch3BGv6fgr8Eyh6EXqUHMXKs'
    )
