DATA(
    arcadia/robot/jupiter/cm
    arcadia/robot/jupiter/cmpy
)

PEERDIR(
    mapreduce/yt/python
    robot/jupiter/test/common
    robot/library/yuppie
)

DEPENDS(
    library/python/testing/deprecated/setup_environment/recipe
    robot/jupiter/packages/cmpy
    tools/clustermaster/bundle
    tools/clustermaster/utils/cmcheck
)

IF(NOT NO_PRINTERS)
    DEPENDS(
        robot/jupiter/packages/printers
    )
ENDIF()

IF(NOT NO_BINARIES)
    DEPENDS(
        robot/jupiter/packages/canonized_factors_bundle
        robot/jupiter/packages/dessert_bundle
        robot/jupiter/packages/externaldat_host_bundle
        robot/jupiter/packages/gemini_saas_bundle
        robot/jupiter/packages/hostdat_bundle
        robot/jupiter/packages/rt_yandex_bundle
        robot/jupiter/packages/shard_deploy_bundle
        robot/jupiter/packages/shards_prepare_bundle
        robot/jupiter/packages/yandex_bundle
        robot/jupiter/packages/yandex_deploy_bundle
        yt/packages/latest
    )
ENDIF()
