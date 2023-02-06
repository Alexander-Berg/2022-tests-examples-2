def test_simple(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'supervisor': {
                    'program_name': 'simple-program',
                    'working_dir': '/home/me/my/service',
                    'command': 'sleep infinity',
                },
            },
        },
    )
    dir_comparator(
        tmp_dir, 'test_supervisor/test_simple', 'test_supervisor/base', 'base',
    )


def test_full(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'supervisor': {
                    'program_name': 'simple-program',
                    'working_dir': '/home/me/my/service',
                    'command': 'sleep infinity',
                    'user': 'alberist',
                    'numprocs_start': 10,
                    'startsecs': 15,
                    'startretries': 20,
                    'stopwaitsecs': 25,
                    'num_procs': 30,
                    'env_vars': {
                        'PATH': '$PATH:/usr/lib/uber/taxi-deps-py3-2/bin',
                        'PYTHONPATH': '/usr/lib/uber/taxi-stq',
                    },
                    'kill_as_group': True,
                },
            },
        },
    )
    dir_comparator(
        tmp_dir, 'test_supervisor/test_full', 'test_supervisor/base', 'base',
    )


def test_env(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'supervisor': {
                    'program_name': 'my-simple-program',
                    'working_dir': '/',
                    'command': 'python -m this',
                    'num_procs': {
                        'production': 10,
                        'testing': 5,
                        'unstable': 500,
                    },
                },
            },
        },
    )
    dir_comparator(
        tmp_dir, 'test_supervisor/test_env', 'test_supervisor/base', 'base',
    )
