# pylint: disable=protected-access
import pytest

from clownductor.internal.components import disk_profiles

POINT_KEYS = {
    'type',
    'size',
    'bandwidth_limit_mb_per_sec',
    'bandwidth_guarantee_mb_per_sec',
    'path',
}


@pytest.mark.parametrize(
    'is_valid, content',
    [
        (
            True,
            {
                'mount_points': {
                    '/': {
                        'type': 'hdd',
                        'size': 123,
                        'bandwidth_guarantee_mb_per_sec': 1,
                    },
                },
                'root_point': {
                    'size': 10240,
                    'type': 'hdd',
                    'work_dir_size': 256,
                    'bandwidth_guarantee_mb_per_sec': 1,
                },
            },
        ),
        (
            True,
            {
                'mount_points': {
                    '/': {
                        'type': 'hdd',
                        'size': 123,
                        'bandwidth_guarantee_mb_per_sec': 1,
                    },
                },
                'name': 'bla',
                'root_point': {
                    'size': 10240,
                    'type': 'hdd',
                    'work_dir_size': 256,
                    'bandwidth_guarantee_mb_per_sec': 1,
                },
            },
        ),
        (False, {}),
        (False, {'mount_points': {'abc': {'type': 'hdd', 'size': 123}}}),
        (False, {'mount_points': {'/abc': {'type': 'hddd', 'size': 123}}}),
        (False, {'mount_points': {'/abc': {'type': 'hdd', 'size': 123.123}}}),
    ],
)
def test_validation(is_valid, content):
    if not is_valid:
        with pytest.raises(disk_profiles.BadProfileSchema):
            disk_profiles._create_profile(content, 'test')
    else:
        result = disk_profiles._create_profile(content, 'test')
        assert result.name
        assert result.mount_points
        item = next(iter(result.mount_points.values()))
        assert set(item.keys()) == POINT_KEYS


def test_real_validation():
    real_profiles = disk_profiles._get_profiles()
    for profile in real_profiles:
        assert profile.name
        assert profile.mount_points
        for path, props in profile.mount_points.items():
            assert path, profile.name
            assert set(props.keys()) == POINT_KEYS, profile.name
