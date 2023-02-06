import pytest

from clowny_alert_manager.internal.models import default_checkfile as df


async def test_storage_empty():
    storage = df.DefaultCheckfileStorage(base_path='/my/base/path/')
    assert storage.find(path='') is None
    assert storage.find(path='/') is None
    assert storage.find(path='/my/base/path/') is None
    assert storage.find(path='/my/base/path/any/path.yaml') is None


async def test_storage():
    storage = df.DefaultCheckfileStorage(base_path='/my/base/path/')
    file1 = df.DefaultCheckfile(data={'hello': 'world'})

    storage.set(path='/my/base/path/taxi.graph.prod/default.yaml', file=file1)
    assert storage.find(path='') is None
    assert storage.find(path='/') is None
    assert storage.find(path='/my/base/path/') is None
    assert storage.find(path='taxi.graph.prod/rtc_service_stable') == file1
    assert storage.find(path='./taxi.graph.prod/rtc_service_stable') == file1
    assert (
        storage.find(path='taxi.graph.prod/rtc_service-name_stable.yaml')
        == file1
    )
    assert (
        storage.find(path='./taxi.graph.prod/rtc_service-name_stable.yaml')
        == file1
    )
    assert (
        storage.find(path='/my/base/path/taxi.graph.prod/checkfile.yaml')
        == file1
    )
    assert (
        storage.find(path='taxi.graph.prod/another-subdir/checkfile.yaml')
        == file1
    )
    assert (
        storage.find(
            path='taxi.graph.prod/another-subdir/deeper/checkfile.yaml',
        )
        == file1
    )

    file2 = df.DefaultCheckfile(data={'deep': 'default'})
    storage.set(
        path='./taxi.graph.prod/another-subdir/deeper/default.yaml',
        file=file2,
    )
    assert (
        storage.find(path='taxi.graph.prod/another-subdir/checkfile.yaml')
        == file1
    )
    assert (
        storage.find(
            path='taxi.graph.prod/another-subdir/deeper/checkfile.yaml',
        )
        == file2
    )
    assert storage.find(path='') is None
    assert storage.find(path='/') is None

    file3 = df.DefaultCheckfile(data={'root': 'default'})
    storage.set(path='/my/base/path/./default.yaml', file=file3)
    assert (
        storage.find(path='taxi.graph.prod/another-subdir/checkfile.yaml')
        == file1
    )
    assert (
        storage.find(
            path='taxi.graph.prod/another-subdir/deeper/checkfile.yaml',
        )
        == file2
    )
    assert storage.find(path='cargo.prod/subdir/checkfile.yaml') == file3


@pytest.mark.parametrize(
    'default_filename, checkfile_filename, result_filename',
    [
        pytest.param('default.yaml', 'rtc_1.yaml', 'rtc_1_result.yaml'),
        pytest.param(
            'default.yaml',
            'rtc_1_secondary.yaml',
            'rtc_1_secondary_result.yaml',
        ),
        pytest.param(
            'default.yaml', 'postgres_1.yaml', 'postgres_1_result.yaml',
        ),
        pytest.param('default.yaml', 'cgroup.yaml', 'cgroup_result.yaml'),
        pytest.param(
            'graph_default.yaml',
            'graph_rtc_1.yaml',
            'graph_rtc_1_result.yaml',
        ),
        pytest.param(
            'graph_default.yaml',
            'graph_redis_1.yaml',
            'graph_redis_1_result.yaml',
        ),
    ],
)
async def test_generate_full_checkfile(
        default_filename, checkfile_filename, result_filename, load_yaml,
):
    default_checkfile_data = load_yaml(default_filename)
    checkfile = load_yaml(checkfile_filename)
    expected = load_yaml(result_filename)

    default_checkfile = df.DefaultCheckfile(data=default_checkfile_data)
    full_checkfile = default_checkfile.generate_full_checkfile(checkfile)
    assert expected == full_checkfile


async def test_find_and_generate(load_yaml):
    storage = df.DefaultCheckfileStorage(base_path='')
    default = df.DefaultCheckfile(data=load_yaml('graph_default.yaml'))
    storage.set(path='/taxi.graph.prod/default.yaml', file=default)

    checkfile = load_yaml('graph_rtc_1.yaml')
    full_checkfile = storage.generate_full_checkfile(
        path='/taxi.graph.prod/rtc_taxi_driver-route-watcher_stable',
        checkfile=checkfile,
    )

    assert full_checkfile == load_yaml('graph_rtc_1_result.yaml')
