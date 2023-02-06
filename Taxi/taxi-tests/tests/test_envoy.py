import dataclasses
from typing import Dict
from typing import List

import pytest


@dataclasses.dataclass(frozen=True)
class Param:
    test_id: str
    dest: List[str]
    info: List[Dict[str, str]]


def _params(*params: Param) -> Dict:
    return {
        'argnames': ['dest', 'info'],
        'argvalues': [(p.dest, p.info) for p in params],
        'ids': [p.test_id for p in params],
    }


def _info(key: str, value: str) -> Dict[str, str]:
    return {'key': key, 'value': value}


# Following destinations allowed in the service.yaml of services:
#   alpha -> (bravo, delta)
#   bravo -> (charlie, delta)
#   charlie -> ()
#   delta -> ()
@pytest.mark.parametrize(
    **_params(
        Param(test_id='alpha', dest=[], info=[_info('service', 'alpha')]),
        Param(
            test_id='alpha-alpha',
            dest=['alpha'],
            info=[
                _info('service', 'alpha'),
                _info('error', 'wrong dest "alpha"'),
            ],
        ),
        Param(
            test_id='alpha-bravo',
            dest=['bravo'],
            info=[
                _info('service', 'alpha'),
                _info('header-dstvhost', 'taxi_tst_envoy-exp-bravo_stable'),
                _info('service', 'bravo'),
            ],
        ),
        Param(
            test_id='alpha-bravo-charlie',
            dest=['bravo', 'charlie'],
            info=[
                _info('service', 'alpha'),
                _info('header-dstvhost', 'taxi_tst_envoy-exp-bravo_stable'),
                _info('service', 'bravo'),
                _info('header-dstvhost', 'taxi_tst_envoy-exp-charlie_stable'),
                _info('service', 'charlie'),
            ],
        ),
        Param(
            test_id='alpha-bravo-delta',
            dest=['bravo', 'delta'],
            info=[
                _info('service', 'alpha'),
                _info('header-dstvhost', 'taxi_tst_envoy-exp-bravo_stable'),
                _info('service', 'bravo'),
                _info('error', 'delta request fails'),
            ],
        ),
        Param(
            test_id='alpha-charlie',
            dest=['charlie'],
            info=[
                _info('service', 'alpha'),
                _info('error', 'wrong dest "charlie"'),
            ],
        ),
        Param(
            test_id='alpha-delta',
            dest=['delta'],
            info=[
                _info('service', 'alpha'),
                _info('error', 'delta request fails'),
            ],
        ),
    ),
)
def test_v2_visit(envoy_v2_visit, dest, info):
    resp_info = envoy_v2_visit(dest)
    assert resp_info == info
