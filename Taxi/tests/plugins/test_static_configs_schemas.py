def test_default(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository[
        'services/test-service/src/component.schema.yaml'
    ] = """
type: object
description: for schemas generation test
additionalProperties: false
properties: {}
"""

    generate_services_and_libraries(
        default_repository, 'test_static_configs_schemas/test', default_base,
    )
