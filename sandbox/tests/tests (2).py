from datetime import datetime

import sandbox.projects.garden.RenderModulesToStat as RM


GARDEN_HOST = "http://localhost"

RENDER_MODULES = {
    0: "stylerepo_map_design_src",
    1: "renderer_design_testing",
    2: "renderer_design_testing_deploy",
    3: "renderer_map_stable_bundle",
    4: "renderer_publication",
    5: "renderer_deployment_to_testing",
    6: "renderer_deployment_to_dataprestable",
    7: "renderer_deployment",
}


def _create_build(build_name, build_id, release_name="", status="completed"):
    return {
        "id": build_id,
        "name": build_name,
        "properties": {
            "release_name": release_name
        },
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
    }


STYLEREPO_BUILDS = [
    _create_build(RM.STYLEREPO_MODULE, 0, release_name="release_0"),
    _create_build(RM.STYLEREPO_MODULE, 1, release_name="release_1"),
]

STYLEREPO_0_HIERARCHY = [
    STYLEREPO_BUILDS[0],
    _create_build("some_module", 0),
    _create_build("renderer_deployment", 0),
]

STYLEREPO_1_HIERARCHY = [
    STYLEREPO_BUILDS[1],
    _create_build("some_module", 1),
    _create_build("renderer_publication", 1),
]

STYLEREPO_HIERARCHY = {
    STYLEREPO_BUILDS[0]["id"]: STYLEREPO_0_HIERARCHY,
    STYLEREPO_BUILDS[1]["id"]: STYLEREPO_1_HIERARCHY,
}

RENDER_HIERARCHY = {
    RM.STYLEREPO_MODULE: STYLEREPO_BUILDS,
}


def test_render_modules_to_stat(requests_mock):
    garden_url = "http://localhost"
    render_modules = {v: k for k, v in RENDER_MODULES.iteritems()}
    from_date = datetime.now().isoformat()

    module_path = RM.GARDEN_MODULE_STATISTICS_URL + "?from={}&module={}"
    for module in render_modules.keys():
        requests_mock.get(module_path.format(garden_url, from_date, module),
                          json=RENDER_HIERARCHY.get(module, []))

    build_path = RM.GARDEN_BUILD_HIERARCHY_URL + "?build_id={}&module={}"
    for build in STYLEREPO_BUILDS:
        requests_mock.get(build_path.format(garden_url, build["id"], build["name"]),
                          json=STYLEREPO_HIERARCHY[build["id"]])

    render_builds = []
    for module in render_modules.keys():
        render_builds.extend(RM.get_render_builds(garden_url, module, from_date))

    render_builds_info = RM.get_render_builds_info(garden_url, render_builds, render_modules)
    data = RM.make_stats(render_builds_info, render_modules)

    assert len(data) == 4
