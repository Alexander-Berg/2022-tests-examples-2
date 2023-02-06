SIZE(LARGE)
TAG(ya:fat ya:not_autocheck ya:force_sandbox)

INCLUDE(${ARCADIA_ROOT}/robot/blrt/library/local_blrt/local_blrt_deps.make)

ENV(YT_TOKEN="empty_token")
ENV(YT_USER="root")

PEERDIR(
    robot/blrt/test/common
    robot/library/python/common_test
    robot/blrt/library/python/bindings
)

DEPENDS(
    robot/blrt/tools/difftool
)
