INCLUDE(${ARCADIA_ROOT}/metrika/java/api/builder/versions_common.inc)
INCLUDE(${ARCADIA_ROOT}/metrika/java/api/builder/excludes_common.inc)
JDK_VERSION(17)

SYSTEM_PROPERTIES(
    ru.yandex.metrika.daemon.env development
)
