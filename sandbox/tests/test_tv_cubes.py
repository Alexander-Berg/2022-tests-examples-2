import pytest
import six

import sandbox.projects.quasar.build_types as quasar_build_types
import sandbox.projects.quasar.platform as quasar_platform

import sandbox.projects.release_machine.components.configs.smart_devices._tv_cubes as tv_cubes


def test_supported_platforms_is_subset_of_all():
    assert tv_cubes.SUPPORTED_PLATFORMS.issubset(set(quasar_platform.Platform))


@pytest.mark.parametrize("platform", tv_cubes.SUPPORTED_PLATFORMS)
def test_genrate_non_empty_graph(platform):
    build_graph = tv_cubes.TVBuildGraph(platform, tv_cubes.BuildTvImage(), (), is_factory=False)
    graph = build_graph.graph()
    assert len(graph)


@pytest.mark.parametrize("platform", tv_cubes.SUPPORTED_PLATFORMS)
def test_generates_build_apps(platform):
    build_graph = tv_cubes.TVBuildGraph(platform, tv_cubes.BuildTvImage(), (), is_factory=False)
    graph = build_graph.graph().to_dict()
    build_apps = [x for x in six.iterkeys(graph) if x.startswith("build") and x.endswith("app")]
    assert len(build_apps) == 9
    assert all(graph[x]["needs"] == ["flow_start"] for x in build_apps)


@pytest.mark.parametrize("platform", tv_cubes.SUPPORTED_PLATFORMS)
def test_generates_build_image(platform):
    build_types = [tv_cubes.BuildType(quasar_build_types.ImageBuildtype.USER, quasar_build_types.TvAppsBuildType.QA)]
    build_graph = tv_cubes.TVBuildGraph(
        platform,
        tv_cubes.BuildTvImage(),
        build_types,
        is_factory=False
    )
    graph = build_graph.graph().to_dict()
    image_builds = [x for x in six.iterkeys(graph) if x.startswith("build") and x.endswith("image")]
    assert len(image_builds) == len(build_types)
    assert graph[image_builds[0]]["input"]["build_type"] == build_types[0].image_build_type
    assert graph[image_builds[0]]["input"]["tv_apps_build_type"] == build_types[0].tv_apps_build_type


@pytest.mark.parametrize("platform", tv_cubes.SUPPORTED_PLATFORMS)
def test_generates_quasmodrom_publish(platform):
    build_graph = tv_cubes.TVBuildGraph(
        platform,
        tv_cubes.BuildTvImage(),
        (tv_cubes.BuildType(quasar_build_types.ImageBuildtype.USER, quasar_build_types.TvAppsBuildType.RELEASE), ),
        is_factory=False
    )
    graph = build_graph.graph().to_dict()
    publish_image = [x for x in six.iterkeys(graph) if x.startswith("publish_ota_to_s3")]
    assert len(publish_image) == 1
    publish_image = [x for x in six.iterkeys(graph) if x.startswith("ota_to_quasmodrom")]
    assert len(publish_image) == 1


def test_goya_image():
    goya_image = tv_cubes.BuildGoyaImage("GOYA")
    cube = goya_image.build_image_cube(
        platform="goya",
        platform_name="Goya",
        is_factory=False,
        image_build_type=quasar_build_types.ImageBuildtype.USER,
        tv_apps_build_type=quasar_build_types.TvAppsBuildType.RELEASE,
        build_apps=[]
    )
    assert cube.input.get("build_product_target_name") == "GOYA"
    assert not cube.input.get("factory")


def test_goya_factory_image():
    goya_image = tv_cubes.BuildGoyaImage("GOYA")
    cube = goya_image.build_image_cube(
        platform="goya",
        platform_name="Goya",
        is_factory=True,
        image_build_type=quasar_build_types.ImageBuildtype.USER,
        tv_apps_build_type=quasar_build_types.TvAppsBuildType.RELEASE,
        build_apps=[]
    )
    assert cube.input.get("build_product_target_name") == "GOYA"
    assert not cube.input.get("build_ota")
    assert cube.input.get("factory")
