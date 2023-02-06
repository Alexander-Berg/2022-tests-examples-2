# pylint: disable=import-error
import dataclasses
from typing import List
from typing import Optional

from driver_mode_index.v1.drivers.snapshot.post.fbs import Request as fb_req
from driver_mode_index.v1.drivers.snapshot.post.fbs import Response as fb_resp
import flatbuffers
import pytest

from tests_driver_mode_index import utils


def _construct_fbs_post_request(
        new_park_driver_profile_ids: List[str], current_cursor: Optional[int],
) -> bytearray:
    builder = flatbuffers.Builder(initialSize=1024)

    fb_new_park_driver_profile_ids = [
        builder.CreateString(s) for s in new_park_driver_profile_ids
    ]

    fb_req.RequestStartNewParkDriverProfileIdsVector(
        builder, len(new_park_driver_profile_ids),
    )
    for fb_park_driver_profile_id in reversed(fb_new_park_driver_profile_ids):
        builder.PrependUOffsetTRelative(fb_park_driver_profile_id)
    fb_new_park_driver_profile_ids = builder.EndVector(
        len(new_park_driver_profile_ids),
    )

    fb_req.RequestStart(builder)

    if current_cursor is not None:
        fb_req.RequestAddCurrentCursor(builder, current_cursor)

    fb_req.RequestAddNewParkDriverProfileIds(
        builder, fb_new_park_driver_profile_ids,
    )

    request = fb_req.RequestEnd(builder)

    builder.Finish(request)
    return builder.Output()


@dataclasses.dataclass()
class DriverMode:
    driver: str
    mode: str
    properties: Optional[List[str]] = None


@dataclasses.dataclass()
class SnapshotResponse:
    cursor: int
    new_drivers: Optional[List[DriverMode]] = None
    drivers_update: Optional[List[DriverMode]] = None


def _decode_fbs_properties(properties) -> List[list]:
    res = []
    for i in range(properties.WorkModePropertiesLength()):
        current_properties = []
        for j in range(properties.WorkModeProperties(i).PropertiesLength()):
            current_properties.append(
                properties.WorkModeProperties(i).Properties(j).decode('utf-8'),
            )
        res.append(current_properties)
    return res


def _make_sorted(response: SnapshotResponse):
    def sort_by_driver(driver_modes):
        if not driver_modes:
            return None
        driver_modes.sort(key=lambda x: x.driver)
        return driver_modes

    response.new_drivers = sort_by_driver(response.new_drivers)
    response.drivers_update = sort_by_driver(response.drivers_update)
    return response


def _make_snapshot_response(
        response: fb_resp.Response, new_drivers: List[str],
) -> SnapshotResponse:
    mode_idx_to_name = dict(
        (i, response.WorkModes(i).decode('utf-8'))
        for i in range(response.WorkModesLength())
    )
    properties_id_to_value = dict(enumerate(_decode_fbs_properties(response)))

    def get_property(idx):
        return properties_id_to_value[idx] if idx != -1 else None

    new_drivers_modes: List[DriverMode] = []
    for i, driver in enumerate(new_drivers):
        mode_idx = response.NewDriversWorkModesIndexes(i)
        properties_idx = response.NewDriversWorkModePropertiesIndexes(i)
        new_drivers_modes.append(
            DriverMode(
                driver,
                mode_idx_to_name[mode_idx],
                get_property(properties_idx),
            ),
        )

    drivers_update = []
    for i in range(response.DriversWorkModesUpdatesLength()):
        fb_update = response.DriversWorkModesUpdates(i)
        driver = fb_update.ParkDriverProfileId().decode('utf-8')
        work_mode = mode_idx_to_name[fb_update.WorkModeIndex()]
        properties_idx = fb_update.WorkModePropertiesIndex()
        drivers_update.append(
            DriverMode(driver, work_mode, get_property(properties_idx)),
        )

    return _make_sorted(
        SnapshotResponse(
            cursor=response.NewCursor(),
            new_drivers=new_drivers_modes,
            drivers_update=drivers_update,
        ),
    )


def _compare_responses(
        lhs: fb_resp.Response, rhs: SnapshotResponse, new_drivers: List[str],
) -> None:
    assert _make_snapshot_response(lhs, new_drivers) == _make_sorted(rhs)


@pytest.mark.now('2020-01-07T12:00:00+0300')
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
@pytest.mark.pgsql('driver_mode_index', files=['init_db.sql'])
@pytest.mark.parametrize(
    'current_cursor, new_park_driver_profile_ids, expected_response',
    (
        (
            -1,
            [],
            SnapshotResponse(
                cursor=19,
                drivers_update=[
                    DriverMode(
                        'dbid1_uuid1', 'driver_fix', ['time_based_subvention'],
                    ),
                    DriverMode(
                        'dbid1_uuid2',
                        'driver_fix1',
                        ['time_based_subvention'],
                    ),
                    DriverMode('dbid2_uuid1', 'flexible_mode'),
                    DriverMode('dbid2_uuid2', 'medic'),
                    DriverMode('dbid3_uuid1', 'uberdriver'),
                    DriverMode('dbid3_uuid2', 'uberdriver'),
                    DriverMode(
                        'dbid3_uuid3',
                        'driver_fix1',
                        ['time_based_subvention'],
                    ),
                    DriverMode('dbid3_uuid4', 'uberdriver'),
                ],
            ),
        ),
        (None, [], SnapshotResponse(cursor=0)),
        (0, [], SnapshotResponse(cursor=0)),
        (
            15,
            [],
            SnapshotResponse(
                cursor=19,
                drivers_update=[
                    DriverMode('dbid3_uuid2', 'uberdriver'),
                    DriverMode(
                        'dbid3_uuid3',
                        'driver_fix1',
                        ['time_based_subvention'],
                    ),
                    DriverMode('dbid3_uuid4', 'uberdriver'),
                ],
            ),
        ),
        (19, [], SnapshotResponse(cursor=19)),
        (100, [], SnapshotResponse(cursor=100)),
        (
            15,
            ['dbid1_uuid1'],
            SnapshotResponse(
                cursor=19,
                new_drivers=[
                    DriverMode(
                        'dbid1_uuid1', 'driver_fix', ['time_based_subvention'],
                    ),
                ],
                drivers_update=[
                    DriverMode('dbid3_uuid2', 'uberdriver'),
                    DriverMode(
                        'dbid3_uuid3',
                        'driver_fix1',
                        ['time_based_subvention'],
                    ),
                    DriverMode('dbid3_uuid4', 'uberdriver'),
                ],
            ),
        ),
        (
            15,
            ['dbid3_uuid2'],
            SnapshotResponse(
                cursor=19,
                new_drivers=[DriverMode('dbid3_uuid2', 'uberdriver')],
                drivers_update=[
                    DriverMode(
                        'dbid3_uuid3',
                        'driver_fix1',
                        ['time_based_subvention'],
                    ),
                    DriverMode('dbid3_uuid4', 'uberdriver'),
                ],
            ),
        ),
        (
            15,
            ['dbid1_uuid1', 'dbid3_uuid2', 'dbid3_uuid4'],
            SnapshotResponse(
                cursor=19,
                new_drivers=[
                    DriverMode(
                        'dbid1_uuid1', 'driver_fix', ['time_based_subvention'],
                    ),
                    DriverMode('dbid3_uuid2', 'uberdriver'),
                    DriverMode('dbid3_uuid4', 'uberdriver'),
                ],
                drivers_update=[
                    DriverMode(
                        'dbid3_uuid3',
                        'driver_fix1',
                        ['time_based_subvention'],
                    ),
                ],
            ),
        ),
        (
            15,
            [
                'dbid1_uuid1',
                'dbid3_uuid2',
                'dbid3_uuid4',
                'dbid_uuid',
                'dbiduuid',
                '_uuid',
                'dbid_',
            ],
            SnapshotResponse(
                cursor=19,
                drivers_update=[
                    DriverMode(
                        'dbid3_uuid3',
                        'driver_fix1',
                        ['time_based_subvention'],
                    ),
                ],
                new_drivers=[
                    DriverMode(
                        'dbid1_uuid1', 'driver_fix', ['time_based_subvention'],
                    ),
                    DriverMode('dbid3_uuid2', 'uberdriver'),
                    DriverMode('dbid3_uuid4', 'uberdriver'),
                    DriverMode('dbid_uuid', 'orders'),
                    DriverMode('dbiduuid', 'orders'),
                    DriverMode('_uuid', 'orders'),
                    DriverMode('dbid_', 'orders'),
                ],
            ),
        ),
        (
            None,
            [
                'dbid1_uuid1',
                'dbid3_uuid2',
                'dbid3_uuid4',
                'dbid_uuid',
                'dbiduuid',
                '_uuid',
                'dbid_',
            ],
            SnapshotResponse(
                cursor=19,
                new_drivers=[
                    DriverMode(
                        'dbid1_uuid1', 'driver_fix', ['time_based_subvention'],
                    ),
                    DriverMode('dbid3_uuid2', 'uberdriver'),
                    DriverMode('dbid3_uuid4', 'uberdriver'),
                    DriverMode('dbid_uuid', 'orders'),
                    DriverMode('dbiduuid', 'orders'),
                    DriverMode('_uuid', 'orders'),
                    DriverMode('dbid_', 'orders'),
                ],
            ),
        ),
        (
            None,
            [
                'dbid1_uuid1',
                'dbid1_uuid1',
                'dbid3_uuid2',
                'dbid3_uuid4',
                'dbid_uuid',
                'dbiduuid',
                '_uuid',
                'dbid_',
            ],
            SnapshotResponse(
                cursor=19,
                new_drivers=[
                    DriverMode(
                        'dbid1_uuid1', 'driver_fix', ['time_based_subvention'],
                    ),
                    DriverMode(
                        'dbid1_uuid1', 'driver_fix', ['time_based_subvention'],
                    ),
                    DriverMode('dbid3_uuid2', 'uberdriver'),
                    DriverMode('dbid3_uuid4', 'uberdriver'),
                    DriverMode('dbid_uuid', 'orders'),
                    DriverMode('dbiduuid', 'orders'),
                    DriverMode('_uuid', 'orders'),
                    DriverMode('dbid_', 'orders'),
                ],
            ),
        ),
        (
            None,
            ['dbiduuid', '_uuid', 'dbid_'],
            SnapshotResponse(
                cursor=19,
                new_drivers=[
                    DriverMode('dbiduuid', 'orders'),
                    DriverMode('_uuid', 'orders'),
                    DriverMode('dbid_', 'orders'),
                ],
            ),
        ),
        (
            15,
            [
                'dbid1_uuid1',
                'dbid1_uuid1',
                'dbid3_uuid2',
                'dbid3_uuid4',
                'dbid_uuid',
                'dbiduuid',
                '_uuid',
                'dbid_',
            ],
            SnapshotResponse(
                cursor=19,
                new_drivers=[
                    DriverMode(
                        'dbid1_uuid1', 'driver_fix', ['time_based_subvention'],
                    ),
                    DriverMode(
                        'dbid1_uuid1', 'driver_fix', ['time_based_subvention'],
                    ),
                    DriverMode('dbid3_uuid2', 'uberdriver'),
                    DriverMode('dbid3_uuid4', 'uberdriver'),
                    DriverMode('dbid_uuid', 'orders'),
                    DriverMode('dbiduuid', 'orders'),
                    DriverMode('_uuid', 'orders'),
                    DriverMode('dbid_', 'orders'),
                ],
                drivers_update=[
                    DriverMode(
                        'dbid3_uuid3',
                        'driver_fix1',
                        ['time_based_subvention'],
                    ),
                ],
            ),
        ),
        (
            15,
            ['dbiduuid', '_uuid', 'dbid_'],
            SnapshotResponse(
                cursor=19,
                new_drivers=[
                    DriverMode('dbiduuid', 'orders'),
                    DriverMode('_uuid', 'orders'),
                    DriverMode('dbid_', 'orders'),
                ],
                drivers_update=[
                    DriverMode('dbid3_uuid2', 'uberdriver'),
                    DriverMode(
                        'dbid3_uuid3',
                        'driver_fix1',
                        ['time_based_subvention'],
                    ),
                    DriverMode('dbid3_uuid4', 'uberdriver'),
                ],
            ),
        ),
    ),
)
async def test_drivers_snapshot(
        taxi_driver_mode_index,
        current_cursor,
        new_park_driver_profile_ids,
        expected_response,
):
    data = _construct_fbs_post_request(
        new_park_driver_profile_ids, current_cursor,
    )
    response = await taxi_driver_mode_index.post(
        'v1/drivers/snapshot',
        data=data,
        headers={'Content-Type': 'application/flatbuffer'},
    )
    assert response.status_code == 200
    parsed_response = fb_resp.Response.GetRootAsResponse(
        bytearray(response.content), 0,
    )
    _compare_responses(
        parsed_response, expected_response, new_park_driver_profile_ids,
    )


@pytest.mark.now('2020-01-07T12:00:00+0300')
@pytest.mark.config(DRIVER_MODE_INDEX_CONFIG=utils.get_config())
@pytest.mark.parametrize(
    'current_cursor, new_park_driver_profile_ids, expected_response',
    (
        (None, [], SnapshotResponse(cursor=0)),
        (0, [], SnapshotResponse(cursor=0)),
        (-1, [], SnapshotResponse(cursor=-1)),
        (15, [], SnapshotResponse(cursor=15)),
        (
            15,
            ['dbid1_uuid1', 'dbid3_uuid2', 'dbid3_uuid4', 'dbid_uuid', ''],
            SnapshotResponse(
                cursor=15,
                new_drivers=[
                    DriverMode('dbid1_uuid1', 'orders'),
                    DriverMode('dbid3_uuid2', 'orders'),
                    DriverMode('dbid3_uuid4', 'orders'),
                    DriverMode('dbid_uuid', 'orders'),
                    DriverMode('', 'orders'),
                ],
            ),
        ),
        (
            None,
            ['dbid1_uuid1', 'dbid3_uuid2', 'dbid3_uuid4', 'dbid_uuid', ''],
            SnapshotResponse(
                cursor=0,
                new_drivers=[
                    DriverMode('dbid1_uuid1', 'orders'),
                    DriverMode('dbid3_uuid2', 'orders'),
                    DriverMode('dbid3_uuid4', 'orders'),
                    DriverMode('dbid_uuid', 'orders'),
                    DriverMode('', 'orders'),
                ],
            ),
        ),
        (
            15,
            [
                'dbid1_uuid1',
                'dbid3_uuid2',
                'dbid3_uuid4',
                'dbid_uuid',
                'dbid_uuid',
                '',
                '',
            ],
            SnapshotResponse(
                cursor=15,
                new_drivers=[
                    DriverMode('dbid1_uuid1', 'orders'),
                    DriverMode('dbid3_uuid2', 'orders'),
                    DriverMode('dbid3_uuid4', 'orders'),
                    DriverMode('dbid_uuid', 'orders'),
                    DriverMode('dbid_uuid', 'orders'),
                    DriverMode('', 'orders'),
                    DriverMode('', 'orders'),
                ],
            ),
        ),
        (
            None,
            [
                'dbid1_uuid1',
                'dbid3_uuid2',
                'dbid3_uuid4',
                'dbid_uuid',
                'dbid_uuid',
                '',
                '',
            ],
            SnapshotResponse(
                cursor=0,
                new_drivers=[
                    DriverMode('dbid1_uuid1', 'orders'),
                    DriverMode('dbid3_uuid2', 'orders'),
                    DriverMode('dbid3_uuid4', 'orders'),
                    DriverMode('dbid_uuid', 'orders'),
                    DriverMode('dbid_uuid', 'orders'),
                    DriverMode('', 'orders'),
                    DriverMode('', 'orders'),
                ],
            ),
        ),
    ),
)
async def test_drivers_snapshot_empty_db(
        taxi_driver_mode_index,
        current_cursor,
        new_park_driver_profile_ids,
        expected_response,
):
    data = _construct_fbs_post_request(
        new_park_driver_profile_ids, current_cursor,
    )
    response = await taxi_driver_mode_index.post(
        'v1/drivers/snapshot',
        data=data,
        headers={'Content-Type': 'application/flatbuffer'},
    )
    assert response.status_code == 200
    parsed_response = fb_resp.Response.GetRootAsResponse(
        bytearray(response.content), 0,
    )
    _compare_responses(
        parsed_response, expected_response, new_park_driver_profile_ids,
    )
