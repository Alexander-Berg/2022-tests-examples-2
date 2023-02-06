def test_geobase(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['external-deps/geobase.yaml'] = {
        'name': 'Geobase',
        'debian-names': ['libgeobase6-dev'],
        'formula-name': 'geobase6',
        'libraries': {'find': [{'names': ['geobase6']}]},
        'includes': {'find': [{'names': ['geobase6/lookup.hpp']}]},
    }
    generate_services_and_libraries(
        default_repository, 'test_external_deps/geobase', default_base,
    )


def test_static_graph(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['external-deps/StaticGraph.yaml'] = {
        'name': 'StaticGraph',
        'package-name': 'libyandex-taxi-graph2',
        'debian-names': ['libyandex-taxi-graph'],
        'formula-name': 'libyandex-taxi-graph2',
        'version': '5665817',
        'libraries': {'variable': 'YANDEX_TAXI_GRAPH2_LIBS'},
        'includes': {'enabled': False},
    }
    generate_services_and_libraries(
        default_repository, 'test_external_deps/static_graph', default_base,
    )


def test_flatbuffers(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['external-deps/Flatbuffers.yaml'] = {
        'name': 'Flatbuffers',
        'package-name': 'libflatbuffers-dev',
        'debian-names': ['libflatbuffers-dev'],
        'formula-name': 'libflatbuffers-dev',
        'version': '5615811',
        'libraries': {'find': [{'names': ['libflatbuffers-dev']}]},
        'includes': {'find': [{'names': ['flatbuffers/flatbuffers.h']}]},
    }
    generate_services_and_libraries(
        default_repository, 'test_external_deps/Flatbuffers', default_base,
    )
