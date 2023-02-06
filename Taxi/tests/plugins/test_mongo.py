def test_service(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['mongo'] = {
        'collections': ['parks', 'drivers', 'cars', 'user_phones'],
        'connections': ['con3', 'con1', 'con2'],
        'testsuite': {
            'extra-connections': ['phone_history', 'geoareas', 'tariffs'],
        },
    }
    generate_services_and_libraries(
        default_repository, 'test_mongo/service', default_base,
    )


def test_library(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['libraries'] = [
        'yandex-taxi-library-mongo-lib',
    ]
    default_repository['libraries/mongo-lib/library.yaml'] = {
        'maintainers': ['mon-go-lang'],
        'description': 'MonGoLang',
        'project-name': 'yandex-taxi-library-mongo-lib',
        'mongo': {'collections': ['parks', 'drivers', 'cars', 'user_phones']},
    }
    generate_services_and_libraries(
        default_repository, 'test_mongo/library', default_base,
    )
