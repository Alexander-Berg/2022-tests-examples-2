import os.path


def test_local_files_dependencies(
        generate_services_and_libraries,
        default_repository,
        default_base,
        codegen_uservices_path,
):
    default_repository['services/test-service/service.yaml'].update(
        {
            'local-files-dependencies': {
                'paths': [
                    os.path.join(codegen_uservices_path, 'local/path3'),
                    os.path.join(codegen_uservices_path, 'local/path1'),
                    os.path.join(codegen_uservices_path, 'local/path2'),
                ],
            },
        },
    )
    generate_services_and_libraries(
        default_repository, 'test_local_files_dependencies/test', default_base,
    )
