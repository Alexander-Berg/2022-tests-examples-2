from copy import deepcopy
from six import string_types

from sandbox import sdk2
from sandbox.projects.common.yabs.server.util import truncate_output_parameters
from sandbox.projects.yabs.qa.spec.misc import get_base_resource_ids
from sandbox.projects.yabs.qa.spec.constants import META_MODES
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShoot2 import YabsServerB2BFuncShoot2


def get_meta_base_tags_to_create(base_tags_map, bases_to_create=(), meta_modes=META_MODES):
    base_tags_to_create = {}
    for meta_mode in meta_modes:
        meta_mode_bases = set(base_tags_map['base_tags_meta_{}'.format(meta_mode)])
        if bases_to_create:
            meta_mode_bases &= set(bases_to_create)
        base_tags_to_create['base_tags_meta_{}'.format(meta_mode)] = list(meta_mode_bases)
    return base_tags_to_create


def get_stat_base_tags_to_create(base_tags_map, shard_keys, bases_to_create=(), meta_modes=META_MODES):
    base_tags_to_create = {}
    for meta_mode in META_MODES:
        for shard_key in set(shard_keys + ['COMMON']):
            mbb_key = 'base_tags_stat_{}'.format(meta_mode)
            meta_mode_shard_bases = set(base_tags_map['base_tags_stat_{}_{}'.format(meta_mode, shard_key)])
            if bases_to_create:
                meta_mode_shard_bases &= set(bases_to_create)
            base_tags_to_create[mbb_key] = list(
                set(base_tags_to_create.get(mbb_key, []) + list(meta_mode_shard_bases))
            )
    return base_tags_to_create


def _launch_task(
        parent_task,
        task_type,
        description='',
        **task_parameters
):
    return task_type(
        sdk2.Task.current,
        tags=getattr(parent_task, 'tags', sdk2.Task[parent_task.id].Parameters.tags),
        description=description,
        **task_parameters
    ).enqueue().id


def _launch_shoot_task(
        parent_task,
        baseline_task_id,
        task_type,
        meta_mode,
        shard_keys,
        stat_base_tags_map,
        stat_binary_base_resource_id_by_tag,
        meta_base_tags_map,
        meta_binary_base_resource_id_by_tag,
        description='',
        parent_description='',
        shoot_task_update_parameters=None,
):
    if isinstance(shard_keys, string_types):
        shard_keys = [shard_keys]

    task_parameters = truncate_output_parameters(dict(sdk2.Task[baseline_task_id].Parameters), task_type.Parameters)

    stat_binary_base_resource_ids = get_base_resource_ids(stat_base_tags_map, stat_binary_base_resource_id_by_tag, shard_keys, meta_mode, server_mode='stat')
    meta_binary_base_resource_ids = get_base_resource_ids(meta_base_tags_map, meta_binary_base_resource_id_by_tag, shard_keys, meta_mode, server_mode='meta')

    task_parameters.update(
        stat_binary_base_resources=stat_binary_base_resource_ids,
        meta_binary_base_resources=meta_binary_base_resource_ids,
        **(shoot_task_update_parameters or {})
    )
    return _launch_task(
        parent_task,
        task_type,
        description='{} {}, shard {}, {}'.format(description, meta_mode, ", ".join(shard_keys), parent_description),
        **task_parameters
    )


def _launch_shoot_tasks(
        task,
        shard_keys,
        shard_map,
        baseline_shoot_tasks,
        stat_base_tags_map,
        stat_binary_base_resource_id_by_tag,
        meta_base_tags_map,
        meta_binary_base_resource_id_by_tag,
        description='',
        parent_description='',
        meta_modes=META_MODES,
        ammo_overrides=None,
        additional_parameters=None,
        task_type=YabsServerB2BFuncShoot2,
):
    shoot_tasks = {}
    for meta_mode in meta_modes:
        for shard_key in shard_keys:
            _additional_parameters = deepcopy(additional_parameters or {})
            if ammo_overrides and meta_mode in ammo_overrides:
                _additional_parameters.update(
                    cache_daemon_stub_resource=ammo_overrides[meta_mode]['stub_resource'],
                    requestlog_resource=ammo_overrides[meta_mode]['requestlog_resource'],
                )

            shoot_tasks.setdefault(meta_mode, {})[str(shard_map[shard_key])] = _launch_shoot_task(
                task,
                baseline_shoot_tasks[meta_mode][shard_map[shard_key]],
                task_type,
                meta_mode,
                shard_key,
                stat_base_tags_map,
                stat_binary_base_resource_id_by_tag,
                meta_base_tags_map,
                meta_binary_base_resource_id_by_tag,
                description=description,
                parent_description=parent_description,
                shoot_task_update_parameters=_additional_parameters,
            )

    return shoot_tasks
