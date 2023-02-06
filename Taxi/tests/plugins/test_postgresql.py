def test_postgresql(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['postgresql'] = {
        'databases': ['orders', 'categories', 'misc', 'shared'],
    }
    path = 'services/test-service/postgresql/'
    default_repository.update(
        {
            path + 'orders/migrations/V01__single_shard.sql': '',
            path + 'categories/migrations/V02__categories@2.sql': '',
            path + 'misc/migrations/V03__misc.sql': '',
            path + 'misc/migrations.yml': '',
            (
                '../schemas/schemas/postgresql/shared/shared/'
                + 'migrations/V04__shared.sql'
            ): '',
        },
    )

    generate_services_and_libraries(
        default_repository, 'test_postgresql/test', default_base,
    )


def test_postgresql_no_fstree_validation(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['postgresql'] = {
        'databases': ['orders'],
        'validate-files-tree': False,
    }
    path = 'services/test-service/postgresql/'
    default_repository.update(
        {path + 'orders/migrations/single_shard.sql': ''},
    )

    generate_services_and_libraries(
        default_repository,
        'test_postgresql_no_fstree_validation/test',
        default_base,
    )
