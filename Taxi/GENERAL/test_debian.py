import multiprocessing
import os


def test_no_binary_package_name(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    service = base_service
    service['debian'].pop('binary_package_name')
    plugin_manager_test(tmp_dir, service=service)
    dir_comparator(tmp_dir, 'test_debian/test_no_binary_package_name', 'base')


def test_compat_level(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    service_activation = base_service
    service_activation['debian']['compat_level'] = 7
    plugin_manager_test(tmp_dir, service=service_activation)
    dir_comparator(tmp_dir, 'test_debian/test_compat_level', 'base')


def test_init_version(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    service_activation = base_service
    service_activation['debian']['init_version'] = '1.2.3'
    plugin_manager_test(tmp_dir, service=service_activation)
    dir_comparator(tmp_dir, 'test_debian/test_init_version', 'base')


def test_changelog_exists(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    debian_dir = os.path.join(tmp_dir, 'test-service', 'debian')
    os.makedirs(debian_dir)
    with open(os.path.join(debian_dir, 'changelog'), 'w') as fchangelog:
        fchangelog.write('already exists\n')
    plugin_manager_test(tmp_dir, service=base_service)
    dir_comparator(tmp_dir, 'test_debian/test_changelog_exists', 'base')


def test_rules_override(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'rules_override': [
                        {'name': 'dh_nginx', 'value': 'any extra args'},
                        {'name': 'dh_nginx', 'value': 'any extra args'},
                        {'name': 'dh_supervisor', 'value': 'do nothing'},
                    ],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_rules_override', 'base')


def test_dependencies(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {'dependencies': ['dep2', 'dep1', 'dep3 (>=3)']},
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_dependencies', 'base')


def test_conflicts_and_replaces(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'conflicts': ['yandex-geo-dorblu-agent'],
                    'replaces': ['yandex-geo-dorblu-agent'],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_conflicts_and_replaces', 'base')


def test_build_dependencies(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    build_depends = multiprocessing.Manager().list()

    class SomePlugin:
        name = 'some-plugin'
        scope = 'unit'
        depends = ['debian']

        def __init__(self):
            pass

        @staticmethod
        def generate(manager):
            build_depends.append(manager.params.debian_build_depends)

    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'build_dependencies': ['dep2', 'dep1', 'dep3 (=4)'],
                },
            },
        },
        plugins=[SomePlugin],
    )
    dir_comparator(tmp_dir, 'test_debian/test_build_dependencies', 'base')
    assert list(build_depends) == [['dep1', 'dep2', 'dep3 (=4)']]


def test_rules_with(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={'unit': {'debian': {'rules_with': ['supervisor', 'cmake']}}},
    )
    dir_comparator(tmp_dir, 'test_debian/test_rules_with', 'base')


def test_env_export(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {'debian': {'env_export': ['VAR=VALUE', 'AVAR=AVALUE']}},
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_env_export', 'base')


def test_parallel(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={'unit': {'debian': {'parallel': True}}},
    )
    dir_comparator(tmp_dir, 'test_debian/test_parallel', 'base')


def test_buildsystem(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={'unit': {'debian': {'buildsystem': 'cmake'}}},
    )
    dir_comparator(tmp_dir, 'test_debian/test_buildsystem', 'base')


def test_debhelper_depends(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'build_dependencies': [
                        'whelper',
                        'debhelper (>=11)',
                        'ahelper',
                    ],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_debhelper_depends', 'base')


def test_generate_debian(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(tmp_dir, service=base_service, generate_debian=False)
    dir_comparator(tmp_dir, 'test_debian/empty')


def test_source_format(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={'unit': {'debian': {'source_format': 'some source format'}}},
    )
    dir_comparator(tmp_dir, 'test_debian/test_source_format', 'base')


def test_etc_dir(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'etc_dir': '/etc/ya/srv',
                    'environment_install': [{'src': 'srcf.*', 'dst': 'destf'}],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_etc_dir', 'base')


def test_dirs(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={'unit': {'debian': {'dirs': ['dir3', 'dir1', 'dir2']}}},
    )
    dir_comparator(tmp_dir, 'test_debian/test_dirs', 'base')


def test_install(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'install': [
                        {'src': 'source3/f', 'dst': 'dest3/f'},
                        {'src': 'source1/f', 'dst': 'dest1/f'},
                        {'src': 'source2/f', 'dst': 'dest2/f'},
                    ],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_install', 'base')


def test_environment_install(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'environment_install': [
                        {'src': 'source3/f.*', 'dst': 'dest3/f'},
                        {
                            'src': 'source1/f.*',
                            'dst': 'dest1/%(binary_package_name)s',
                        },
                        {
                            'src': 'source2/%(binary_package_name)s.*',
                            'dst': 'dest2/f',
                        },
                    ],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_environment_install', 'base')


def test_generate(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    os.makedirs(os.path.join(tmp_dir, 'test-service'))
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'generate': [
                        {
                            'target': '%(binary_package_name)s.asdf',
                            'content': 'asd\n',
                        },
                        {
                            'target': 'debian/some-file',
                            'content': 'some\nfile\n',
                        },
                    ],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_generate', 'base')


def test_postinst_configure(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'postinst_configure': [
                        'line3',
                        'line1',
                        'line2',
                        'line %(binary_package_name)s',
                    ],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_postinst_configure', 'base')


def test_preinst(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={'unit': {'debian': {'preinst': ['line3', 'line1', 'line2']}}},
    )
    dir_comparator(tmp_dir, 'test_debian/test_preinst', 'base')


def test_prerm_remove(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {'debian': {'prerm_remove': ['line3', 'line1', 'line2']}},
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_prerm_remove', 'base')


def test_postrm(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'postrm_remove': [
                        'remove3',
                        'remove1',
                        'remove2',
                        'r%(binary_package_name)s',
                    ],
                    'postrm_purge': [
                        'purge3',
                        'purge1',
                        'purge2',
                        'p%(binary_package_name)s',
                    ],
                    'postrm_upgrade': [
                        'upgrade3',
                        'upgrade1',
                        'upgrade2',
                        'u%(binary_package_name)s',
                    ],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_postrm', 'base')


def test_links(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'links': [
                        {'src': 'lnk_from3', 'dst': 'lnk_to3'},
                        {'src': 'lnk_from1', 'dst': 'lnk_to1'},
                        {'src': 'lnk_from2', 'dst': 'lnk_to2'},
                    ],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_links', 'base')


def test_add_new_package(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'add_new_package': True,
                    'binary_package_name': 'new-package-name',
                    'description': 'new package description',
                    'install': [{'src': 'asdf', 'dst': 'asdf'}],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_add_new_package', 'base')


def test_multi_units(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    service = base_service
    service['debian'].pop('binary_package_name')
    plugin_manager_test(
        tmp_dir,
        service=service,
        units={
            'unit3': {
                'debian': {
                    'binary_package_name': 'package-3',
                    'rules_override': [
                        {'name': 'rule1', 'value': 'value1'},
                        {'name': 'rule2', 'value': 'value2'},
                    ],
                },
            },
            'unit1': {
                'debian': {
                    'binary_package_name': 'package-1',
                    'rules_override': [{'name': 'rule1', 'value': 'value1'}],
                },
            },
            'unit2': {
                'debian': {
                    'binary_package_name': 'package-2',
                    'rules_override': [{'name': 'rule3', 'value': 'value3'}],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_multi_units', 'base')


def test_debticket_disabled(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    service = base_service
    service['debian'].pop('binary_package_name')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'binary_package_name': 'some-package-name',
                    'debticket_disabled': True,
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_debian/test_debticket_disabled', 'base')


class YaFakePlugin:
    name = 'ya_make'
    scope = 'service'
    depends = ['debian']

    def configure(self, manager):
        manager.activate(
            'debian',
            {
                'use-ya-make': True,
                'allowed-overrides': ['dh_nginx'],
                'allowed-build-depends': ['build-essential'],
            },
        )


def test_ya_make(
        tmpdir, monkeypatch, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')

    plugin_manager_test(
        tmp_dir,
        plugins=[YaFakePlugin],
        service=base_service,
        units={
            'unit': {
                'debian': {
                    'environment_install': [
                        {'src': 'source/conf.*', 'dst': 'dest/conf'},
                    ],
                    'build_dependencies': ['build-essential', 'lib1-dev'],
                    'dependencies': ['lib1', 'lib2'],
                    'arcadia_dependencies': ['lib1'],
                    'rules_override': [
                        {'name': 'dh_nginx', 'value': '--no-restart'},
                        {'name': 'dh_foo', 'value': '--bar'},
                    ],
                },
            },
        },
    )

    dir_comparator(tmp_dir, 'test_debian/test_ya_make', 'base')
