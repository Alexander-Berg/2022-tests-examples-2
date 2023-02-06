def test_simple(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'nginx': {
                    'upstream_name': 'upstream_name',
                    'server_names': [
                        'empty.yandex-team.ru',
                        'empty.yandex.net',
                    ],
                    'sockets': ['localhost:8080', 'localhost:8081'],
                },
                'rate-limiter': {},
            },
        },
    )
    dir_comparator(tmp_dir, 'test_rate_limiter')
