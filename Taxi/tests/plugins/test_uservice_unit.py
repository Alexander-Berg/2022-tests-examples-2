def test_logrotate(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['uservice_unit'][
        'logrotate'
    ] = {'maxsize': '1G', 'rotate': 42, 'rotate_policy': 'daily'}
    generate_services_and_libraries(
        default_repository, 'test_uservice_unit/logrotate', default_base,
    )


def test_nginx_set_x_real_ip(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['uservice_unit']['nginx'] = {'set_x_real_ip': False}
    generate_services_and_libraries(
        default_repository, 'test_uservice_unit/nginx', default_base,
    )


def test_monitor_port(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['uservice_unit']['monitor-port'] = 2211
    generate_services_and_libraries(
        default_repository, 'test_uservice_unit/test', default_base,
    )


def test_ltsv_logs(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['uservice_unit']['log_format'] = 'ltsv'
    generate_services_and_libraries(
        default_repository, 'test_uservice_unit/ltsv_logs', default_base,
    )
