from datetime import datetime, timedelta

from sandbox.projects.masstransit.MapsMasstransitDataDeploymentStatistics import (
    GARDEN_BUILD_HIERARCHY_URL,
    GARDEN_MODULE_STATISTICS_URL,
    RELEASE_STAGES_URL,
    SRC_MODULE,

    build_statistics,
    make_report,
    request_builds,
)


def _create_build(build_name, build_id, sources=[], status="completed", shipping_date="20200701_473190_1621_188219215"):
    return {
        "id": build_id,
        "name": build_name,
        "properties": {
            "shipping_date": shipping_date,
        },
        "sources": sources,
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat() if status == "completed" else None,
    }


MASSTRANSIT_BUILDS = [
    _create_build(
        build_name=SRC_MODULE,
        build_id=1,
        shipping_date="20200701_473190_1621_188219215",
    ),
    _create_build(
        build_name=SRC_MODULE,
        build_id=2,
        shipping_date="20200705_473190_0000_123456789",
    ),
    # not completed build
    _create_build(
        build_name=SRC_MODULE,
        build_id=3,
        status="failed",
    ),
]


BUILD_0_HIERARCHY = [
    MASSTRANSIT_BUILDS[0],
    # should not be included in the statistics
    _create_build(
        build_name="gtfs_export",
        build_id=1,
    )
]


BUILD_1_HIERARCHY = [
    MASSTRANSIT_BUILDS[1],
    _create_build(
        build_name="masstransit_deployment",
        build_id=1,
    )
]


def test_build_statistics(requests_mock):
    from_time = datetime.now()
    requests_mock.get(
        GARDEN_MODULE_STATISTICS_URL.format("localhost", SRC_MODULE, from_time),
        json=MASSTRANSIT_BUILDS
    )

    requests_mock.get(
        GARDEN_BUILD_HIERARCHY_URL.format(
            "localhost", MASSTRANSIT_BUILDS[0]["name"],
            MASSTRANSIT_BUILDS[0]["id"]
        ),
        json=BUILD_0_HIERARCHY
    )

    requests_mock.get(
        GARDEN_BUILD_HIERARCHY_URL.format(
            "localhost", MASSTRANSIT_BUILDS[1]["name"],
            MASSTRANSIT_BUILDS[1]["id"]
        ),
        json=BUILD_1_HIERARCHY
    )

    requests_mock.get(
        RELEASE_STAGES_URL.format("1621"),
        json={
            "stages": [{
                "name": "create_stable",
                "start": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%S+0300")
            }]
        }
    )

    requests_mock.get(
        RELEASE_STAGES_URL.format("0000"),
        json={
            "stages": [{
                "name": "create_stable",
                "start": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S+0300")
            }]
        }
    )

    builds = request_builds("localhost", from_time)

    assert len(builds) == 2
    ids = set(build["id"] for build in builds)
    assert ids == set([1, 2])

    shippings_stats = build_statistics("localhost", builds)
    assert set(shippings_stats.keys()) == set(["0000", "1621"])
    assert len(shippings_stats["1621"]) == 1
    assert len(shippings_stats["0000"]) == 2

    report = make_report(shippings_stats)

    assert len(report["values"]) == 3
