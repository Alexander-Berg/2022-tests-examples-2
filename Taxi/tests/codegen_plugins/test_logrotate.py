def test_base(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'logrotate': {
                    'files_paths': {
                        'maxsize': '25G',
                        'name': 'some-name',
                        'postrotate': [],
                        'rotate': 1,
                    },
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_logrotate/test_base', 'base')


def test_multiple(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'logrotate': {
                    'files_paths': [
                        {
                            'maxsize': '25G',
                            'name': 'second-file',
                            'postrotate': [],
                            'rotate': 2,
                            'rotate_policy': 'some rotate policy',
                        },
                        {
                            'maxsize': '50G',
                            'name': 'first-file',
                            'postrotate': ['command 1', 'command 2'],
                            'rotate': 11,
                            'notifempty': True,
                        },
                    ],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_logrotate/test_multiple', 'base')


def test_service_scope(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    service_with_logrotate = base_service
    service_with_logrotate['logrotate'] = {
        'files_paths': {
            'maxsize': '5G',
            'name': 'some-service-name',
            'postrotate': [],
            'rotate': 5,
        },
    }
    plugin_manager_test(
        tmp_dir,
        service=service_with_logrotate,
        units={
            'unit': {
                'logrotate': {
                    'files_paths': [
                        {
                            'maxsize': '25G',
                            'name': 'some-name',
                            'postrotate': [],
                            'rotate': 1,
                        },
                        {
                            'maxsize': '25G',
                            'name': 'notify-service',
                            'postrotate': 'notify_service',
                            'rotate': 1,
                        },
                    ],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_logrotate/test_library', 'base')
