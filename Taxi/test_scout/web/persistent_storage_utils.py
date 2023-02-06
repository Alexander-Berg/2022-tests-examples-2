import contextlib
import dataclasses
import os
from typing import AsyncIterator
from typing import cast
from typing import Optional

from scout import persistent_storage as persist
from scout.generated.web import web_context


TEST_DUMP_INTERVAL_SEC = 0.1


@dataclasses.dataclass(frozen=True)
class ContextForTest:
    settings: dict


class PersistentComponent:
    def __init__(
            self, *, dir_path: str, version: int, prev_version: Optional[int],
    ) -> None:
        settings = {
            'ps-dump-interval-sec': TEST_DUMP_INTERVAL_SEC,
            'ps-dump-path': dir_path,
            'ps-dump-format-version': version,
        }
        if prev_version is not None:
            settings['ps-dump-format-prev-version'] = prev_version

        self._storage = persist.PersistentStorageComponent(
            cast(web_context.Context, ContextForTest(settings=settings)),
        )

    @property
    def storage(self) -> persist.PersistentStorageComponent:
        return self._storage

    @staticmethod
    def get_dump_file_path(dir_path: str, version: int = 1) -> str:
        return os.path.join(
            dir_path,
            f'v{version}',
            persist.PersistentStorageComponent.get_dump_filename(),
        )


@contextlib.asynccontextmanager
async def make_persistent_component(
        dir_path: str, *, version: int = 1, prev_version: Optional[int] = None,
) -> AsyncIterator[persist.PersistentStorageComponent]:
    component = PersistentComponent(
        dir_path=dir_path, version=version, prev_version=prev_version,
    )

    storage = component.storage
    await storage.on_startup()
    try:
        yield storage
    finally:
        await storage.on_shutdown()
