import pathlib

import yaml


def test_taxi(
        generate_services_and_libraries,
        default_repository,
        default_base,
        uservices_path,
):
    default_repository['services/test-service/service.yaml']['realm'] = 'taxi'
    generate_services_and_libraries(
        default_repository, 'test_realm/taxi', default_base,
    )

    # Default config_vars values
    filepath = pathlib.Path(uservices_path).joinpath(
        'tests-pytest/tests/plugins/static/test_realm/taxi/build/services/'
        'test-service/configs/config_vars.production.yaml',
    )
    assert not filepath.exists()


def test_bank(
        generate_services_and_libraries,
        default_repository,
        default_base,
        uservices_path,
):
    default_repository['services/test-service/service.yaml']['realm'] = 'bank'
    generate_services_and_libraries(
        default_repository, 'test_realm/bank', default_base,
    )

    filepath = pathlib.Path(uservices_path).joinpath(
        'tests-pytest/tests/plugins/static/test_realm/bank/build/services/'
        'test-service/configs/config_vars.production.yaml',
    )
    with filepath.open() as ifile:
        variables = yaml.safe_load(ifile)
        assert (
            variables['config_server_url']
            == 'http://configs.fintech.yandex.net'
        )


def test_multiunit_differentunits(
        generate_services_and_libraries,
        multi_unit_repository,
        multi_unit_base,
        uservices_path,
):
    service_yaml = multi_unit_repository['services/test-service/service.yaml']
    service_yaml['units'][0]['realm'] = 'bank'
    service_yaml['units'][1]['realm'] = 'taxi'

    generate_services_and_libraries(
        multi_unit_repository, 'test_realm/multi', multi_unit_base,
    )

    filepath = pathlib.Path(uservices_path).joinpath(
        'tests-pytest/tests/plugins/static/test_realm/multi/build/services/'
        'test-service/units/first-unit/configs/config_vars.production.yaml',
    )
    with filepath.open() as ifile:
        variables = yaml.safe_load(ifile)
        assert (
            variables['config_server_url']
            == 'http://configs.fintech.yandex.net'
        )

    second_filepath = pathlib.Path(uservices_path).joinpath(
        'tests-pytest/tests/plugins/static/test_realm/multi/build/services/'
        'test-service/units/second-unit/configs/config_vars.production.yaml',
    )
    assert not second_filepath.exists()
