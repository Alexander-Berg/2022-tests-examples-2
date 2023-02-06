import pytest


async def _make_request(uafs, time, distance, subvention_type):
    return await uafs.post(
        'v1/subvention/check_order',
        {
            'order': {
                'id': 'order_id1',
                'transporting_time': time,
                'transporting_distance': distance,
            },
            'subvention': {'type': subvention_type},
        },
    )


def _make_cfg(single_ride=None, single_ontop=None):
    cfg = {
        '__default__': {
            'transporting_time': 100,
            'transporting_distance': 500,
        },
    }
    if single_ride is not None:
        cfg['single_ride'] = single_ride
    if single_ontop is not None:
        cfg['single_ontop'] = single_ontop
    return cfg


async def _test_base(uafs, time, distance, subvention_type, status):
    response = await _make_request(uafs, time, distance, subvention_type)
    assert response.status_code == 200
    assert response.json() == {'status': status}


@pytest.mark.parametrize(
    'time,distance,subvention_type,status',
    [
        (100, 500, 'single_ride', 'allow'),
        (100, 500, 'single_ontop', 'allow'),
        (99, 500, 'single_ride', 'block'),
        (100, 499, 'single_ontop', 'block'),
    ],
)
@pytest.mark.config(AFS_ORDER_PARAMS_FOR_SUBVENTION=_make_cfg())
async def test_base1(taxi_uantifraud, time, distance, subvention_type, status):
    await _test_base(taxi_uantifraud, time, distance, subvention_type, status)


@pytest.mark.parametrize(
    'time,distance,subvention_type,status',
    [
        (20, 100, 'single_ride', 'allow'),
        (20, 100, 'single_ontop', 'allow'),
        (19, 100, 'single_ride', 'block'),
        (20, 99, 'single_ontop', 'block'),
    ],
)
@pytest.mark.config(
    AFS_ORDER_PARAMS_FOR_SUBVENTION=_make_cfg(
        single_ride={'transporting_time': 20, 'transporting_distance': 100},
        single_ontop={'transporting_time': 20, 'transporting_distance': 100},
    ),
)
async def test_base2(taxi_uantifraud, time, distance, subvention_type, status):
    await _test_base(taxi_uantifraud, time, distance, subvention_type, status)
