import yaml

_YAML_DATA = """
adapters:
  - type: retrieve_one_by_primary_key
    id: 'one_by_primary_key'
    model:
        name: 'handlers::ComplicatedRow'
        include: 'handlers/composite-primary-key/post/response.hpp'
    primary_key:
      - type: 'std::string'
        name: key_foo
      - type: 'std::int64_t'
        name: key_bar
    pg:
        sql: 'userver_db_adapter_sample::sql::kSampleRetrieveOne'
        database: 'random'
    yt:
        replication-target:
            target-name: 'pg_yt_composite_primary_key'
            cluster-type: 'map-reduce'
        migrations:
          - jsonpath: 'main_table.old_value'
            rename: 'value'
"""


def test_db_adapter(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']

    service_yaml['postgresql'] = {'databases': ['random', 'random2']}
    pgql = 'services/test-service/postgresql'
    default_repository.update(
        {
            f'{pgql}/random/migrations/V01__xx.sql': '',
            f'{pgql}/random2/migrations/V01__xx.sql': '',
        },
    )

    default_repository[
        'services/test-service/docs/db-adapter/adapter_pg_yt.yaml'
    ] = yaml.load(_YAML_DATA, Loader=getattr(yaml, 'CLoader', yaml.Loader))
    service_yaml['db_adapter_pg_yt'] = None

    generate_services_and_libraries(
        default_repository, 'test_db_adapter/db_adapter', default_base,
    )
