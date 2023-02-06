INCLUDE_ONCE(yes)

DEPENDS(
    devtools/local_cache/toolscache/server
    devtools/ya/bin
    devtools/ymake/bin
)

PEERDIR(
    contrib/python/pytest
    contrib/python/pytest-asyncio
    taxi/integration_testing/framework
)

REQUIREMENTS(
    container:3322861118
    dns:dns64
)

SIZE(LARGE)

TAG(
    ya:external
    ya:fat
    ya:force_sandbox
)
