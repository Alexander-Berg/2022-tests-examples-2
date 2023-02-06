import os


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
            },
        },
    )
    dir_comparator(tmp_dir, 'test_nginx/test_simple', 'test_nginx/base')


def test_full(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    cfg = os.path.join(tmp_dir, 'test-service', 'nginx', 'global_extra.nginx')
    os.makedirs(os.path.dirname(cfg))
    with open(cfg, 'w') as fcfg:
        fcfg.write('some\n"data"\n')

    cfg = os.path.join(
        tmp_dir, 'test-service', 'nginx', 'default_location_extra.nginx',
    )
    with open(cfg, 'w') as fcfg:
        fcfg.write('other\n"data"\n')

    cfg = os.path.join(tmp_dir, 'test-service', 'nginx', 'server_extra.nginx')
    with open(cfg, 'w') as fcfg:
        fcfg.write('server\n"extra"\n')

    unit = os.path.join(tmp_dir, 'test-service', 'nginx', 'unit')
    os.makedirs(unit)
    cfg = os.path.join(unit, 'server_extra.nginx')
    with open(cfg, 'w') as fcfg:
        fcfg.write('unit\'s server extra\n')

    cfg = os.path.join(unit, 'default_location_extra.nginx')
    with open(cfg, 'w') as fcfg:
        fcfg.write('unit default location extra\n')

    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'nginx': {
                    'listen_http': True,
                    'listen_https': True,
                    'upstream_name': 'service_upstream_name',
                    'server_names': {
                        'production': [
                            'empty.yandex-team.ru',
                            'empty.yandex.ru',
                        ],
                        'testing': [
                            'empty.tst.yandex-team.ru',
                            'empty.yandex.net',
                        ],
                        'unstable': ['empty.dev.yandex-team.ru'],
                    },
                    'sockets': {
                        'production': ['unix:srv_01.sock', 'unix:srv_02.sock'],
                        'testing': ['unix:srv_tst_01.sock'],
                        'unstable': ['unix:srv_dev_01.sock'],
                    },
                    'include_location': ['random str1', 'random str2'],
                    'proxy_set_header': ['Connection ""'],
                    'proxy_hide_header': ['X-YaTaxi-Api-OperationId'],
                    'config_name': '99-myservice-upstream',
                    'proxy_ignore_client_abort': 'on',
                    'keepalive': 123,
                    'client_max_body_size': 12345,
                    'global_extra': ['some global extra'],
                    'server_extra': ['some server extra'],
                    'default_location_extra': ['some location extra'],
                },
            },
        },
    )
    dir_comparator(tmp_dir, 'test_nginx/test_full', 'test_nginx/base')


def test_config(tmpdir, plugin_manager_test, dir_comparator, base_service):
    tmp_dir = tmpdir.mkdir('repo')
    cfg = os.path.join(tmp_dir, 'test-service', 'nginx_config_dir', 'filename')
    os.makedirs(os.path.dirname(cfg))
    with open(cfg, 'w') as fcfg:
        fcfg.write('some\ndata\n')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={'unit': {'nginx': {'config': 'nginx_config_dir/filename'}}},
    )
    os.remove(cfg)
    dir_comparator(tmp_dir, 'test_nginx/test_config', 'test_nginx/base')


def test_single_upstream_install(
        tmpdir, plugin_manager_test, dir_comparator, base_service,
):
    tmp_dir = tmpdir.mkdir('repo')
    plugin_manager_test(
        tmp_dir,
        service=base_service,
        units={
            'unit': {
                'nginx': {
                    'config_name': '99-my-upstream',
                    'upstream_name': 'upstream_name',
                    'server_names': ['empty.yandex-team.ru'],
                    'sockets': ['localhost:8080'],
                },
            },
        },
    )
    dir_comparator(
        tmp_dir, 'test_nginx/test_single_upstream', 'test_nginx/base',
    )
