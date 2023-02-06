def test_simple(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'syslog': {
                    'log_ident': 'ident',
                    'log_file': '/file/with/logs',
                    'conf_filename': 'smart-log-file.syslog.conf',
                },
            },
        },
    )
    dir_comparator(
        tmp_dir, 'test_syslog/test_simple', 'test_syslog/base', 'base',
    )


def test_not_rtc(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')

    class SomePlugin:
        name = 'some-plugin'
        scope = 'service'
        depends = ['syslog']

        def __init__(self):
            pass

        @staticmethod
        def configure(manager):
            manager.activate('syslog', {'rtc_postrotate': False})

    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'syslog': {
                    'log_ident': 'ident',
                    'log_file': '/file/with/logs',
                    'conf_filename': 'smart-log-file.syslog.conf',
                },
            },
        },
        plugins=[SomePlugin],
    )
    dir_comparator(
        tmp_dir, 'test_syslog/test_not_rtc', 'test_syslog/base', 'base',
    )


def test_full(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'syslog': {
                    'log_ident': 'ident',
                    'log_file': '/file/with/logs',
                    'conf_filename': 'smart-log-file.syslog.conf',
                    'levels': 'info..emerg',
                    'rotate_num': 700,
                    'rotate_policy': 'century',
                    'dir_owner': 'some_owner',
                },
            },
        },
    )
    dir_comparator(
        tmp_dir, 'test_syslog/test_full', 'test_syslog/base', 'base',
    )
