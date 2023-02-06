INCLUDE(${ARCADIA_ROOT}/robot/mercury/library/local_mercury/deps_minimal.make)  # dependencies for local_mercury

DATA(
    arcadia/robot/mercury/test/worker_test
    arcadia/robot/mercury/test/indexer_test
)

PEERDIR(
    mapreduce/yt/python
    robot/library/python/common_test
    robot/library/yuppie
    robot/mercury/scripts
    robot/jupiter/library/python/dump_shards
    robot/mercury/test/common
)

DEPENDS(
    robot/jupiter/packages/printers
    robot/mercury/packages/worker
    robot/mercury/test/common/config
    saas/rtyserver_test/jupi_dump_test
)
