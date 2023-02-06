import pytest

from sandbox.projects.yabs.qa.utils.base import get_max_unpacking_workers
from sandbox.projects.yabs.qa.utils.importer import (
    truncate_base_prefix,
)


@pytest.mark.parametrize(('base', 'expected'), [
    ('bs_st', 'st'),
    ('bs_st_bs_st', 'st_bs_st'),
    ('bs_st_yabs_st', 'st_yabs_st'),
    ('bsst', 'bsst'),
    ('yabs_st', 'st'),
    ('yabs_st_yabs_st', 'st_yabs_st'),
    ('yabs_st_bs_st', 'st_bs_st'),
    ('yabsst', 'yabsst'),
    ('bs_lmng', 'lmng'),
    ('yabs_lmng', 'lmng'),
])
def test_truncate_base_prefix(base, expected):
    assert truncate_base_prefix(base) == expected


@pytest.mark.parametrize(('bin_bases_unpacked_size', 'ram', 'ramdrive', 'expected'), [
    (
        [],
        240,
        10,
        4
    ),
    (
        [50, 40, 30, 20, 10],
        100,
        0,
        4
    ),
    (
        [10, 10, 10, 10],
        20,
        0,
        4
    ),
    (
        [10, 10, 10, 10],
        20,
        30,
        4
    )
])
def test_get_max_unpacking_workers(bin_bases_unpacked_size, ram, ramdrive, expected):
    assert get_max_unpacking_workers(bin_bases_unpacked_size, ram, ramdrive) == expected
