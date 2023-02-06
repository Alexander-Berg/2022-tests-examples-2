import dataclasses
from typing import Dict
from typing import FrozenSet
from typing import List

# pylint: disable=import-error
from driver_mode_index.v1.drivers.snapshot.post.fbs import (
    DriverWorkModeUpdate as fb_update,
)
from driver_mode_index.v1.drivers.snapshot.post.fbs import Response as fb_resp
from driver_mode_index.v1.drivers.snapshot.post.fbs import (
    WorkModeProperties as fb_properties,
)
import flatbuffers


@dataclasses.dataclass
class DriverMode:
    work_mode: str
    properties: List[str] = dataclasses.field(default_factory=list)


def _default_driver_mode() -> DriverMode:
    return DriverMode(work_mode='orders')


def _make_work_mode_to_idx_map(
        new_drivers: List[str],
        update_drivers: List[str],
        drivers_work_modes: Dict[str, DriverMode],
) -> Dict[str, int]:
    modes = {
        drivers_work_modes.get(d, _default_driver_mode()).work_mode: 0
        for d in new_drivers
    }
    modes.update(
        {
            drivers_work_modes.get(d, _default_driver_mode()).work_mode: 0
            for d in update_drivers
        },
    )
    for index, mode in enumerate(modes.keys()):
        modes[mode] = index
    return modes


def _make_properties_to_idx_map(
        new_drivers: List[str],
        update_drivers: List[str],
        drivers_work_modes: Dict[str, DriverMode],
) -> Dict[FrozenSet[str], int]:
    properties: Dict[FrozenSet[str], int] = {}

    for driver in new_drivers:
        properties_list = drivers_work_modes.get(
            driver, _default_driver_mode(),
        ).properties
        if properties_list:
            properties.update({frozenset(properties_list): 0})
    for driver in update_drivers:
        properties_list = drivers_work_modes.get(
            driver, _default_driver_mode(),
        ).properties
        if properties_list:
            properties.update({frozenset(properties_list): 0})

    for index, properties_set in enumerate(properties.keys()):
        properties[properties_set] = index
    return properties


def _make_fbs_modes(builder, modes: Dict[str, int]):
    fb_modes = [builder.CreateString(mode) for mode in modes.keys()]
    fb_resp.ResponseStartWorkModesVector(builder, len(modes))
    for fb_mode in reversed(fb_modes):
        builder.PrependUOffsetTRelative(fb_mode)
    return builder.EndVector(len(modes))


def _make_fbs_properties(
        builder, properties_to_idx: Dict[FrozenSet[str], int],
):
    def _create_mode_properties(properties: FrozenSet[str]):
        fbs_properties_list = [
            builder.CreateString(property) for property in properties
        ]
        fb_properties.WorkModePropertiesStartPropertiesVector(
            builder, len(properties),
        )
        for fbs_property in reversed(fbs_properties_list):
            builder.PrependUOffsetTRelative(fbs_property)
        fbs_properties = builder.EndVector(len(fbs_properties_list))
        fb_properties.WorkModePropertiesStart(builder)
        fb_properties.WorkModePropertiesAddProperties(builder, fbs_properties)
        return fb_properties.WorkModePropertiesEnd(builder)

    fbs_properties = [
        _create_mode_properties(properties)
        for properties in properties_to_idx.keys()
    ]
    fb_resp.ResponseStartWorkModePropertiesVector(
        builder, len(properties_to_idx),
    )
    for fbs_properties in reversed(fbs_properties):
        builder.PrependUOffsetTRelative(fbs_properties)
    return builder.EndVector(len(properties_to_idx))


def _make_fbs_new_drivers_work_mode_idxs(
        builder,
        new_drivers: List[str],
        drivers_work_modes: Dict[str, DriverMode],
        work_mode_to_idx: Dict[str, int],
):
    fb_resp.ResponseStartNewDriversWorkModesIndexesVector(
        builder, len(new_drivers),
    )
    for driver in reversed(new_drivers):
        builder.PrependUint32(
            work_mode_to_idx[
                drivers_work_modes.get(
                    driver, _default_driver_mode(),
                ).work_mode
            ],
        )
    fb_new_drivers_work_modes_idxs = builder.EndVector(len(new_drivers))
    return fb_new_drivers_work_modes_idxs


def _make_fbs_new_drivers_properties_idxs(
        builder,
        new_drivers: List[str],
        drivers_work_modes: Dict[str, DriverMode],
        properties_to_idx: Dict[FrozenSet[str], int],
):
    fb_resp.ResponseStartNewDriversWorkModePropertiesIndexesVector(
        builder, len(new_drivers),
    )
    for driver in reversed(new_drivers):
        properties_list = drivers_work_modes.get(
            driver, _default_driver_mode(),
        ).properties
        properties_idx = -1
        if frozenset(properties_list) in properties_to_idx:
            properties_idx = properties_to_idx[frozenset(properties_list)]
        builder.PrependInt32(properties_idx)
    return builder.EndVector(len(new_drivers))


def _make_fbs_drivers_update(
        builder,
        update_drivers: List[str],
        drivers_work_modes: Dict[str, DriverMode],
        work_mode_to_idx: Dict[str, int],
        properties_to_idx: Dict[FrozenSet[str], int],
):
    fb_update_drivers = [
        builder.CreateString(driver) for driver in update_drivers
    ]
    fb_drivers_work_modes_updates = []
    for i, driver in enumerate(update_drivers):
        fb_update.DriverWorkModeUpdateStart(builder)
        fb_update.DriverWorkModeUpdateAddParkDriverProfileId(
            builder, fb_update_drivers[i],
        )
        driver_mode = drivers_work_modes.get(driver, _default_driver_mode())
        fb_update.DriverWorkModeUpdateAddWorkModeIndex(
            builder, work_mode_to_idx[driver_mode.work_mode],
        )
        properties_idx = -1
        if driver_mode.properties:
            properties_idx = properties_to_idx[
                frozenset(driver_mode.properties)
            ]
        fb_update.DriverWorkModeUpdateAddWorkModePropertiesIndex(
            builder, properties_idx,
        )
        fb_drivers_work_modes_updates.append(
            fb_update.DriverWorkModeUpdateEnd(builder),
        )

    fb_resp.ResponseStartDriversWorkModesUpdatesVector(
        builder, len(update_drivers),
    )
    for update_offset in reversed(fb_drivers_work_modes_updates):
        builder.PrependUOffsetTRelative(update_offset)
    return builder.EndVector(len(update_drivers))


def construct_dmi_fbs_post_response(
        new_drivers: List[str],
        update_drivers: List[str],
        drivers_work_modes: Dict[str, DriverMode],
        new_cursor,
) -> bytearray:
    builder = flatbuffers.Builder(initialSize=1024)

    work_mode_to_idx = _make_work_mode_to_idx_map(
        new_drivers, update_drivers, drivers_work_modes,
    )
    properties_to_idx = _make_properties_to_idx_map(
        new_drivers, update_drivers, drivers_work_modes,
    )

    fbs_modes = _make_fbs_modes(builder, work_mode_to_idx)
    fbs_new_drivers_mode_idxs = _make_fbs_new_drivers_work_mode_idxs(
        builder, new_drivers, drivers_work_modes, work_mode_to_idx,
    )
    fbs_drivers_update = _make_fbs_drivers_update(
        builder,
        update_drivers,
        drivers_work_modes,
        work_mode_to_idx,
        properties_to_idx,
    )
    fbs_new_drivers_properties_idxs = _make_fbs_new_drivers_properties_idxs(
        builder, new_drivers, drivers_work_modes, properties_to_idx,
    )
    fbs_properties = (
        _make_fbs_properties(builder, properties_to_idx)
        if properties_to_idx
        else None
    )

    fb_resp.ResponseStart(builder)
    fb_resp.ResponseAddNewCursor(builder, new_cursor)
    fb_resp.ResponseAddWorkModes(builder, fbs_modes)
    fb_resp.ResponseAddNewDriversWorkModesIndexes(
        builder, fbs_new_drivers_mode_idxs,
    )
    fb_resp.ResponseAddDriversWorkModesUpdates(builder, fbs_drivers_update)
    fb_resp.ResponseAddNewDriversWorkModePropertiesIndexes(
        builder, fbs_new_drivers_properties_idxs,
    )
    if fbs_properties:
        fb_resp.ResponseAddWorkModeProperties(builder, fbs_properties)
    response = fb_resp.ResponseEnd(builder)

    builder.Finish(response)
    return builder.Output()
