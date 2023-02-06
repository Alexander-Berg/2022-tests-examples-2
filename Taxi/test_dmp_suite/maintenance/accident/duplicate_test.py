import os
from functools import partial
from dmp_suite.maintenance.accident import local_storage
from dmp_suite.maintenance.accident import shingle


def _get_shingle(client, fn):
    return shingle.ShingleAccidentProxy(
        client.to_accident(fn),
        shingle.DEFAULT_LIMIT_DESCRIPTION
    ).shingle


def _is_same_shingle(client, fn1, fn2):
    shingle1 = _get_shingle(client, fn1)
    shingle2 = _get_shingle(client, fn2)
    return shingle.compare(shingle1, shingle2) > 0.9


def test_duplicate_accidents():
    accident_path = os.path.join(os.path.dirname(__file__), 'data')
    client = local_storage.LocalFileAccidentClient(accident_path)
    is_same_shingle = partial(_is_same_shingle, client)
    assert is_same_shingle(
        '20180402000001_cpi_network',
        '20180402000002_cpi_network'
    )
    assert not is_same_shingle(
        '20180402000002_cpi_network',
        '20180402000004_cpi_network'
    )
    assert not is_same_shingle(
        '20180402000001_cpi_network',
        '20180402000004_cpi_network'
    )

    assert not is_same_shingle(
        '20180402000001_fraud',
        '20180402000002_fraud'
    )
    assert not is_same_shingle(
        '20180402000002_fraud',
        '20180402000003_fraud'
    )
    assert not is_same_shingle(
        '20180402000001_fraud',
        '20180402000003_fraud'
    )

    assert is_same_shingle(
        '20180402000001_history_leads',
        '20180402000002_history_leads'
    )

    assert not is_same_shingle(
        '20180402000001_ods_order',
        '20180402000002_ods_order'
    )

    assert not is_same_shingle(
        '20180402000001_stg_order',
        '20180402000002_stg_order'
    )

    assert not is_same_shingle(
        '20180402000001_statface',
        '20180402000002_statface'
    )

    assert is_same_shingle(
        '20180402000001_stg_mdb_drivers',
        '20180402000002_stg_mdb_drivers'
    )

    assert not is_same_shingle(
        '20180528000005_atlas_driver_pixel',
        '20180528082404_atlas_driver_pixel'
    )

    assert is_same_shingle(
        '20180528093904_atlas_driver_pixel',
        '20180528082404_atlas_driver_pixel'
    )
    assert is_same_shingle(
        '20180528082404_atlas_driver_pixel',
        '20180528100504_atlas_driver_pixel'
    )
    assert not is_same_shingle(
        '20180528000005_atlas_driver_pixel',
        '20180528100504_atlas_driver_pixel'
    )

    assert not is_same_shingle(
        '20180402000001_stdout',
        '20180402000002_stdout'
    )

