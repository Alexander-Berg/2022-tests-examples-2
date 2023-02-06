def test_redis(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['redis'] = {
        'databases': ['db3', 'db1', 'db2'],
        'subscribe-databases': ['sdb3', 'sdb1', 'sdb2'],
    }
    generate_services_and_libraries(
        default_repository, 'test_redis/test', default_base,
    )
