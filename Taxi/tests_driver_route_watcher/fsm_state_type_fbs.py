# pylint: disable=import-error
# pylint: disable=no-name-in-module

import flatbuffers
import fsm_state_type_entry.fbs.FsmStateTypeEntry as FsmStateTypeEntry


def serialize_fsm_state_type_entry(raw_state):
    fsm_state_type_map = {
        'unknown': -1,
        'wait_data': 0,
        'tracking': 1,
        'fallback_tracking': 2,
        'route_request': 3,
        'route_rebuild': 4,
        'unknown_destination': 5,
    }
    state = fsm_state_type_map[raw_state]

    builder = flatbuffers.Builder(0)

    FsmStateTypeEntry.FsmStateTypeEntryStart(builder)
    FsmStateTypeEntry.FsmStateTypeEntryAddState(builder, state)
    obj = FsmStateTypeEntry.FsmStateTypeEntryEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())
