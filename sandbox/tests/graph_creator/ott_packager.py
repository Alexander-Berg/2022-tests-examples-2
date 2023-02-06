from datetime import datetime
from typing import Optional, List


from sandbox.projects.ott.packager_management_system.lib.graph_creator.ott_packager import (
    OttPackagerReleaseStatus,
    OttPackagerResourceAttrs,
    OttPackagerRepository,
    OttPackager,
    OttPackagerStage,
    OttPackagerService
)

stable_ott_packager = OttPackager(
    '/stable',
    OttPackagerResourceAttrs(
        datetime.fromisoformat('2021-09-22T10:00'),
        'stable_revision',
        OttPackagerReleaseStatus.STABLE
    )
)

new_testing_ott_packager = OttPackager(
    '/new-testing',
    OttPackagerResourceAttrs(
        datetime.fromisoformat('2021-09-22T11:00'),
        'new_testing_revision',
        OttPackagerReleaseStatus.TESTING
    )
)

old_testing_ott_packager = OttPackager(
    '/old-testing',
    OttPackagerResourceAttrs(
        datetime.fromisoformat('2021-09-22T09:00'),
        'old_testing_revision',
        OttPackagerReleaseStatus.TESTING
    )
)


class LocalOttPackagerRepository(OttPackagerRepository):
    def __init__(self, ott_packagers: List[OttPackager]):
        self._ott_packagers = sorted(ott_packagers, key=lambda ott_packager: ott_packager.attrs.create_time,
                                     reverse=True)

    def fetch(self, arc_revision: str) -> Optional[OttPackager]:
        for ott_packager in self._ott_packagers:
            if ott_packager.attrs.arc_revision == arc_revision:
                return ott_packager

    def fetch_resource_attrs(self, release_status: OttPackagerReleaseStatus) -> OttPackagerResourceAttrs:
        for ott_packager in self._ott_packagers:
            if ott_packager.attrs.release_status == release_status:
                return ott_packager.attrs


def test_find_by_stable_ott_packager_stage():
    repository = LocalOttPackagerRepository([stable_ott_packager, old_testing_ott_packager, new_testing_ott_packager])
    ott_packager_service = OttPackagerService(repository)

    assert ott_packager_service.find_by_stage(OttPackagerStage.STABLE) == stable_ott_packager


def test_find_by_testing_ott_packager_stage_with_new_testing_release():
    repository = LocalOttPackagerRepository([stable_ott_packager, old_testing_ott_packager, new_testing_ott_packager])
    ott_packager_service = OttPackagerService(repository)

    assert ott_packager_service.find_by_stage(OttPackagerStage.TESTING) == new_testing_ott_packager


def test_find_by_testing_ott_packager_stage_without_new_testing_release():
    repository = LocalOttPackagerRepository([stable_ott_packager, old_testing_ott_packager])
    ott_packager_service = OttPackagerService(repository)

    assert ott_packager_service.find_by_stage(OttPackagerStage.TESTING) == stable_ott_packager
