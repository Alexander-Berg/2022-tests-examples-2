# pylint: disable=protected-access
import datetime

from replication import core_context
from replication.rule_keeper import sandbox_resources

_PACKAGES = ['rule1', 'rules2']
_VERSIONS = 30


async def test_sandbox_resource(replication_ctx: core_context.TasksCoreData):
    resources = await replication_ctx.sandbox_resources.get_resources()
    assert resources == []

    for package in _PACKAGES:
        for version in range(_VERSIONS):
            await replication_ctx.sandbox_resources.store_resource(
                sandbox_resources.SandboxResource(
                    package=package,
                    version=str(version),
                    download_link='http://link1',
                    resource_link='http://link2',
                    register_at=datetime.datetime(2021, 8, 1, 10, 0)
                    + datetime.timedelta(seconds=version),
                ),
            )

    await replication_ctx.sandbox_resources.refresh_cache()

    resources = await replication_ctx.sandbox_resources.get_resources()
    assert len(resources) == sandbox_resources._STORE_PACKAGE_COUNT * 2, str(
        resources,
    )

    for package in _PACKAGES:
        for version in range(
                _VERSIONS - sandbox_resources._STORE_PACKAGE_COUNT, _VERSIONS,
        ):
            await replication_ctx.sandbox_resources.get_resource(
                package=package, version=str(version),
            )
