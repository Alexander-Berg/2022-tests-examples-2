import pathlib

import yaml


SERVICES_YAML_CONTENT = """
lang: cpp
services:
    directory: services
common:
    shared-dirs:
      - ../other-proj/ml
      - ../other-proj/schemas/stq
      - ../other-proj/schemas/mongo
      - ../other-proj/schemas/services

arcadia-additional-projects:
    - projects/other-proj/ml
    - projects/other-proj/schemas
"""
LFD_CONTENT = """
../other-proj/ml/taxi_ml_cxx
../other-proj/schemas/stq/driver_set_remove_tag.yaml
../other-proj/schemas/mongo/lavka_isr_invoices.yaml
"""


def init_dummy(tmpdir):
    root_dir = pathlib.Path(tmpdir)
    root_dir.joinpath('.arc').mkdir(parents=True, exist_ok=True)
    work_dir = root_dir / 'taxi'
    work_dir.mkdir(parents=True, exist_ok=True)
    return work_dir


def init_uservices(
        tmpdir,
        main_service,
        changelog_content,
        service_yaml=None,
        versioning='changelog',
):
    work_dir = init_dummy(tmpdir)
    init_schemas(work_dir)

    service_dir = work_dir / 'services' / main_service
    debian_dir = service_dir / 'debian'
    debian_dir.mkdir(exist_ok=True, parents=True)

    da_dir = work_dir / 'services' / 'driver-authorizer'
    debian_da_dir = da_dir / 'debian'
    debian_da_dir.mkdir(exist_ok=True, parents=True)

    if service_yaml:
        with (service_dir / 'service.yaml').open(
                'w', encoding='utf-8',
        ) as service_yaml_file:
            yaml.dump(service_yaml, service_yaml_file)

    (work_dir / 'services.yaml').write_text(
        f"""
lang: cpp
services:
    directory: services
versioning: {versioning}
common:
    shared-dirs:
      - ../schemas/schemas/stq
      - ../schemas/schemas/mongo
      - ../schemas/schemas/postgresql
      - ../schemas/schemas/services

arcadia-additional-projects:
    - schemas/schemas
    """.strip(),
    )
    (service_dir / 'local-files-dependencies.txt').write_text(
        """
../schemas/schemas/stq/driver_set_remove_tag.yaml
../schemas/schemas/mongo/lavka_isr_invoices.yaml
    """.strip(),
    )
    if changelog_content:
        (debian_dir / 'changelog').write_text(changelog_content)
    (debian_da_dir / 'changelog').touch()
    return work_dir


def init_graph(tmpdir, changelog_content):
    work_dir = init_dummy(tmpdir)

    graph_dir = work_dir / 'graph'
    debian_dir = graph_dir / 'debian'
    debian_dir.mkdir(exist_ok=True, parents=True)
    changelog = debian_dir / 'changelog'
    changelog.write_text(changelog_content)

    package_json = graph_dir / 'package.json'
    package_json.write_text('{"meta":{"name": "libyandex-taxi-graph"}}')

    return graph_dir


def init_telematics(tmpdir, changelog_content):
    work_dir = init_dummy(tmpdir)

    telematics_dir = work_dir / 'telematics'
    debian_dir = telematics_dir / 'debian'
    debian_dir.mkdir(exist_ok=True, parents=True)
    changelog = debian_dir / 'changelog'
    changelog.write_text(changelog_content)

    package_json = telematics_dir / 'service.yaml'
    package_json.write_text(
        """
arcadia-additional-projects:
    - taxi/graph/
    - taxi/services/driver-authorizer/
    """.rstrip(),
    )

    return telematics_dir


def init_schemas(work_dir):
    schemas_dir = work_dir / '..' / 'schemas'
    schemas_dir.mkdir(parents=True, exist_ok=True)

    configs_dir = schemas_dir / 'schemas' / 'configs' / 'declarations' / 'ubic'
    configs_dir.mkdir(parents=True, exist_ok=True)
    (configs_dir / 'UBIC_CLIENT_QOS.yaml').write_text(
        """
description: Settings for ubic client
default:
    __default__:
        attempts: 1
        timeout-ms: 200
maintainers: []
tags: [notfallback]
schema:
    $ref: 'common/client_qos.yaml#/QosInfoDict'
""".strip(),
    )

    postgresql_dir = schemas_dir / 'schemas' / 'postgresql' / 'plus' / 'plus'
    postgresql_dir.mkdir(parents=True, exist_ok=True)
    (postgresql_dir / 'migrations.yml').write_text(
        """
callbacks:
    afterAll:
      - grants
""".strip(),
    )

    mongo_dir = schemas_dir / 'schemas' / 'mongo'
    mongo_dir.mkdir(parents=True, exist_ok=True)
    (mongo_dir / 'partners.yaml').write_text(
        """
description: partners registration
settings:
    collection: partners
    connection: taxi
    database: dbtaxi
""".strip(),
    )


def init_arcadia_base(builder) -> None:
    builder.root.joinpath('.arcadia.root').write_text(
        'should not rely on its contents',
    )
    builder.add(builder.root / '.arcadia.root')
    builder.commit('base commit')


def init_arcadia_nested_services(builder) -> None:
    init_arcadia_base(builder)
    base_path = builder.root.joinpath('projects/nested-example')
    base_path.mkdir(parents=True)

    base_path.joinpath('.arcignore').write_text('.*\n')
    builder.add(base_path / '.arcignore')

    nested_path = 'nested/services'
    base_path.joinpath('services.yaml').write_text(
        yaml.dump({'services': {'directory': nested_path}}),
    )
    builder.add(base_path / 'services.yaml')
    builder.commit('feat all: first commit')

    first_service_path = base_path / nested_path / 'first-service'
    first_service_path.mkdir(parents=True)
    first_service_path.joinpath('service.yaml').write_text(
        yaml.dump({'useless': 'stuff'}),
    )
    builder.add(first_service_path / 'service.yaml')
    builder.commit('feat first-service: add service.yaml')


def init_arcadia_basic_project(builder) -> None:
    init_arcadia_base(builder)
    base_path = builder.root.joinpath('projects/basic-project')
    base_path.mkdir(parents=True)
    base_path.joinpath('.arcignore').write_text('.*\n')
    builder.add(base_path / '.arcignore')

    builder.commit('feat basic-project: create project')

    (base_path / 'feature1').write_text('feature code')
    builder.add(base_path / 'feature1')
    builder.commit('feat basic-project: add feature')

    (base_path / 'feature1').write_text('fixed feature code')
    builder.add(base_path / 'feature1')
    builder.commit('feat basic-project: fix feature')

    update_arcadia_project(
        builder,
        {
            'services.yaml': SERVICES_YAML_CONTENT,
            'services/my-service/local-files-dependencies' '.txt': LFD_CONTENT,
        },
        'add services.yaml and l-f-d',
    )
    init_arcadia_dependant_project(builder)


def update_arcadia_project(
        builder, files, message, *, project_path='projects/basic-project',
) -> None:
    base_path = builder.root.joinpath(project_path)
    for file_path, file_content in files.items():
        full_file_path = base_path.joinpath(file_path)
        full_file_path.parent.mkdir(parents=True, exist_ok=True)
        full_file_path.write_text(file_content)
        builder.add(full_file_path)
    builder.commit(message)


def init_arcadia_dependant_project(builder) -> None:
    base_path = builder.root.joinpath('projects/other-proj')
    base_path.mkdir(parents=True)
    base_path.joinpath('.arcignore').write_text('.*\n')
    builder.add(base_path / '.arcignore')

    builder.commit('feat other-proj: create project')

    configs_path = base_path.joinpath('schemas/configs/declarations')
    configs_path.mkdir(parents=True)

    services_path = base_path.joinpath('schemas/services')
    services_path.mkdir(parents=True)

    stq_path = base_path.joinpath('schemas/stq')
    stq_path.mkdir(parents=True)

    mongo_path = base_path.joinpath('schemas/mongo')
    mongo_path.mkdir(parents=True)

    adjust_config = configs_path.joinpath('adjust')
    adjust_config.mkdir(parents=True)
    (adjust_config / 'ADJUST_CONFIG.yaml').write_text('some config')

    driver_authorizer_client = services_path.joinpath('driver-authorizer/api')
    driver_authorizer_client.mkdir(parents=True)
    (driver_authorizer_client / 'api.yaml').write_text('some client')

    (stq_path / 'driver_set_remove_tag.yaml').write_text('some stq')

    (mongo_path / 'lavka_isr_invoices.yaml').write_text('some mongo')

    ml_path = base_path.joinpath('ml/taxi_ml_cxx')
    ml_path.mkdir(parents=True)

    (ml_path / 'objects.cpp').write_text('some cpp')

    builder.add(base_path)
    builder.commit('feat other-proj: add data')
