def test_cmake(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['libraries'] = [
        'yandex-taxi-library-user-agent-parser',
    ]
    default_repository['libraries/user-agent-parser/library.yaml'][
        'submodules'
    ] = (
        {
            'submodule1': {'includes': ['includes'], 'sources': ['src']},
            'submodule2': {
                'includes': ['includes', 'nested_lib/include'],
                'sources': ['src', 'nested_lib/src'],
            },
        }
    )
    generate_services_and_libraries(
        default_repository, 'test_submodules/test', default_base,
    )
