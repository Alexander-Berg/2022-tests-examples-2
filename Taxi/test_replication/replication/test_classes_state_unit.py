# pylint: disable=protected-access
import copy
import datetime

import pytest

from replication.common import replication_ids
from replication.foundation import consts
from replication.foundation.contextual_classes.states import base as state_unit
from replication.replication.classes import state_unit as state_replication
# TODO: move to contextual_classes


DB_LAST_TS = datetime.datetime(2018, 5, 5, 12, 34, 56)
NEW_DT = datetime.datetime(2018, 11, 1, 0, 0)


async def test_state_update(replication_ctx, db, _state_id):
    state = state_replication.ReplicationStateWrapper(
        _state_id,
        {},
        db=replication_ctx.db,
        rule_keeper=replication_ctx.rule_keeper,
    ).extended_class
    await state.refresh()
    assert not state.disabled

    prev_ts = state.last_synced
    assert await state.mark_synced()
    new_ts = state.last_synced
    assert prev_ts != new_ts
    await db.replication_state.update(
        {'_id': state.id}, {'$set': {state.LAST_SYNCED_KEY: None}},
    )
    assert not await state.mark_synced()
    await db.replication_state.update(
        {'_id': state.id}, {'$set': {state.LAST_TS_KEY: None}},
    )
    with pytest.raises(state_unit.StateUpdateError):
        await state.update_last_replication(NEW_DT)


async def test_state_control_disable(_state_controller):
    await _state_controller.disable()
    assert _state_controller.disabled
    with pytest.raises(state_unit.StateIncorrectControl):
        await _state_controller.disable()


async def test_state_control_enable(_state_controller):
    await _state_controller.disable()
    assert _state_controller.disabled
    await _state_controller.enable()
    assert not _state_controller.disabled
    with pytest.raises(state_unit.StateIncorrectControl):
        await _state_controller.enable()


@pytest.mark.parametrize('need_disable', [False, True])
async def test_state_control_update(_state_controller, need_disable):
    if need_disable:
        await _state_controller.disable()
        assert _state_controller.disabled

    with pytest.raises(state_unit.StateIncorrectControl):
        await _state_controller.update_last_replication(1223)

    if need_disable:
        with pytest.raises(state_unit.StateUpdateError):
            await _state_controller.update_last_replication(
                NEW_DT, only_if_enabled=True,
            )
    else:
        await _state_controller.update_last_replication(
            NEW_DT, only_if_enabled=True,
        )

    await _state_controller.update_last_replication(
        NEW_DT, only_if_enabled=False,
    )
    assert _state_controller.last_replication == NEW_DT


@pytest.mark.parametrize('need_disable', [False, True])
@pytest.mark.parametrize(
    'seconds,error',
    [
        (1, None),
        (100, None),
        (0, state_unit.StateIncorrectControl),
        (-100, state_unit.StateIncorrectControl),
    ],
)
async def test_state_control_rollback(
        _state_controller, need_disable, seconds, error,
):
    if need_disable:
        await _state_controller.disable()
        assert _state_controller.disabled

    if error:
        with pytest.raises(error):
            await _state_controller.rollback(seconds)
        assert _state_controller.current_ts == DB_LAST_TS
        await _state_controller.refresh()
        assert _state_controller.current_ts == DB_LAST_TS
    else:
        await _state_controller.rollback(seconds)
        assert _state_controller.current_ts == DB_LAST_TS - datetime.timedelta(
            seconds=seconds,
        )


# pylint: disable=invalid-name
@pytest.mark.parametrize('need_disable', [False, True])
async def test_state_control_rollback_race(
        db, _state_id, _state_controller, need_disable,
):
    if need_disable:
        await _state_controller.disable()
        assert _state_controller.disabled

    await db.replication_state.update(
        {'_id': _state_id}, {_state_controller.LAST_TS_KEY: NEW_DT},
    )
    with pytest.raises(state_unit.StateUpdateError):
        await _state_controller.rollback(100)
    assert _state_controller.current_ts == NEW_DT


# pylint: disable=protected-access
async def test_state_control_remove_and_init(_state_controller, _state_id):
    assert _state_controller._data
    await _state_controller.remove()
    assert not _state_controller._data

    await _state_controller.init()
    assert _state_controller._data['_id'] == _state_id

    await _state_controller.remove()
    assert not _state_controller._data

    with pytest.raises(state_unit.StateUpdateError):  # cannot upsert
        await _state_controller.update_last_replication(NEW_DT)


async def test_wrapper(
        replication_ctx, db, _state_source_and_target_ids, _state_id,
):
    states_wrapper = replication_ctx.rule_keeper.states_wrapper
    source_id, target_id = _state_source_and_target_ids
    state = states_wrapper.get_state(source_id=source_id, target_id=target_id)
    state2 = states_wrapper.get_state(replication_id=_state_id)
    assert state._data == state2._data
    state3 = states_wrapper.get_state(replication_id=_state_id)
    assert state._data == state3._data

    ids = list(states_wrapper.replication_ids(only_initialized=True))
    assert [_state_id] == ids

    data = copy.deepcopy(state._data)
    assert data
    cache = replication_ctx.rule_keeper.states_wrapper._common_cache

    extra_field = 'extra_field'
    extra_data = data.copy()
    extra_data[extra_field] = True

    state._data = extra_data
    assert state._data == extra_data
    assert cache[state.id] == extra_data

    await state.refresh()
    assert state._data == data
    assert cache[state.id] == data

    cache[state.id] = extra_data
    assert state._data == extra_data
    assert cache[state.id] == extra_data

    await states_wrapper.refresh(secondary=False)
    cache = replication_ctx.rule_keeper.states_wrapper._common_cache
    assert state._data == data
    assert cache[state.id] == data

    await db.replication_state.update(
        {'_id': state.id}, {'$set': {extra_field: True}},
    )
    await states_wrapper.refresh(secondary=False)
    cache = replication_ctx.rule_keeper.states_wrapper._common_cache
    assert state._data == extra_data
    assert cache[state.id] == extra_data


@pytest.fixture
async def _state_controller(replication_ctx, _state_source_and_target_ids):
    state_ctl = replication_ctx.rule_keeper.states_wrapper.get_state(
        *_state_source_and_target_ids,
    )
    assert state_ctl.current_ts == DB_LAST_TS
    assert not state_ctl.disabled
    return state_ctl


@pytest.fixture
async def _rule_and_target(replication_ctx):
    rule = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='test_rule', source_types=[consts.SOURCE_TYPE_QUEUE_MONGO],
    )[0]
    hahn_target = None
    for target in rule.targets:
        if target.id == 'yt-test_rule_struct-hahn':
            hahn_target = target
            break
    assert hahn_target
    return rule, hahn_target


@pytest.fixture
def _state_source_and_target_ids(_rule_and_target):
    rule, hahn_target = _rule_and_target
    return rule.source.id, hahn_target.id


@pytest.fixture
async def _state_id(_state_source_and_target_ids):
    return replication_ids.make_replication_id(*_state_source_and_target_ids)
