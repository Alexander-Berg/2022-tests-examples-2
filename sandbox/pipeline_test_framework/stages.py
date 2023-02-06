import json
import logging
from itertools import chain

from sandbox import sdk2

from sandbox.projects.common.yabs.server.util import truncate_output_parameters
from sandbox.projects.common.yabs.server.util.general import check_tasks
from sandbox.projects.yabs.qa.spec.constants import META_MODES
from sandbox.projects.yabs.qa.pipeline.stage import stage
from sandbox.projects.yabs.qa.pipeline_test_framework.helpers import (
    _launch_task,
    _launch_shoot_task,
    _launch_shoot_tasks,
)
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShoot2 import YabsServerB2BFuncShoot2
from sandbox.projects.yabs.qa.tasks.YabsServerPerformanceMetaCmp import YabsServerPerformanceMetaCmp
from sandbox.projects.yabs.qa.tasks.YabsServerStatPerformanceBestCmp2 import YabsServerStatPerformanceBestCmp2
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp import YabsServerB2BFuncShootCmp
from sandbox.projects.yabs.qa.tasks.YabsServerValidateResponses import YabsServerValidateResponses
from sandbox.projects.yabs.qa.tasks.YabsServerValidateResponsesCmp import YabsServerValidateResponsesCmp
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootStability import YabsServerB2BFuncShootStability
from sandbox.projects.yabs.qa.tasks.YabsServerStatPerformancePrepareDplan import YabsServerStatPerformancePrepareDplan
from sandbox.projects.yabs.qa.tasks.YabsServerPrepareStatStub import YabsServerPrepareStatStub


logger = logging.getLogger(__name__)


@stage(provides=(
    'shard_map',
    'ft_shard_nums',
    'stat_load_shard_nums',
    'meta_load_shard_nums',
    'ft_shard_keys',
    'stat_load_shard_keys',
    'meta_load_shard_keys',
))
def get_shard_map(task, spec_shard_map_resource_id, ft_shards=(), stat_load_shards=(), meta_load_shards=(), stat_load=False, meta_load=False):
    shard_map_resource = sdk2.Resource[spec_shard_map_resource_id]
    with open(str(sdk2.ResourceData(shard_map_resource).path), 'r') as shard_map_file:
        shard_map = json.load(shard_map_file)

    ft_shard_keys = ft_shards
    stat_load_shard_keys = stat_load_shards if stat_load else []
    meta_load_shard_keys = meta_load_shards if meta_load else []

    ft_shard_nums = [shard_num for shard_name, shard_num in shard_map.items() if shard_name in ft_shards]
    stat_load_shard_nums = [shard_num for shard_name, shard_num in shard_map.items() if shard_name in stat_load_shards] if stat_load else []
    meta_load_shard_nums = [shard_num for shard_name, shard_num in shard_map.items() if shard_name in meta_load_shards] if meta_load else []

    return (
        shard_map,
        ft_shard_nums,
        stat_load_shard_nums,
        meta_load_shard_nums,
        ft_shard_keys,
        stat_load_shard_keys,
        meta_load_shard_keys,
    )


@stage(provides=('baseline_ft_shoot_tasks', 'test_ft_shoot_tasks'))
def launch_ft_shoot_tasks(
        task,
        ft_shard_keys,
        spec_ft_shoot_tasks,
        spec_stat_base_tags_map,
        spec_meta_base_tags_map,
        shard_map,
        test_stat_binary_base_resource_id_by_tag,
        baseline_stat_binary_base_resource_id_by_tag,
        test_meta_binary_base_resource_id_by_tag,
        baseline_meta_binary_base_resource_id_by_tag,
        test_linear_models_service_data_resource,
        shoot_baseline_tasks=False,
        test_description='',
        ammo_overrides=None,
        meta_modes=META_MODES,
):
    ft_shoot_tasks = {'test': {}, 'baseline': {}}
    run_type_parameters = (
        (
            'test',
            test_stat_binary_base_resource_id_by_tag,
            test_meta_binary_base_resource_id_by_tag,
        ),
        (
            'baseline',
            baseline_stat_binary_base_resource_id_by_tag,
            baseline_meta_binary_base_resource_id_by_tag,
        ),
    )
    for run_type, stat_binary_base_resource_id_by_tag, meta_binary_base_resource_id_by_tag in run_type_parameters:
        if run_type == 'baseline' and not shoot_baseline_tasks:
            ft_shoot_tasks[run_type] = spec_ft_shoot_tasks
            continue
        ft_shoot_tasks[run_type] = _launch_shoot_tasks(
            task,
            ft_shard_keys,
            shard_map,
            spec_ft_shoot_tasks,
            spec_stat_base_tags_map,
            stat_binary_base_resource_id_by_tag,
            spec_meta_base_tags_map,
            meta_binary_base_resource_id_by_tag,
            description='{} ft shoot'.format(run_type),
            parent_description=test_description,
            ammo_overrides=ammo_overrides,
            task_type=YabsServerB2BFuncShoot2,
            meta_modes=meta_modes,
        )

    return ft_shoot_tasks['baseline'], ft_shoot_tasks['test']


@stage(provides=('test_ft_stability_tasks'))
def launch_ft_stability_tasks(
        task,
        ft_shard_keys,
        spec_ft_stability_shoot_tasks,
        spec_stat_base_tags_map,
        spec_meta_base_tags_map,
        shard_map,
        test_stat_binary_base_resource_id_by_tag,
        test_meta_binary_base_resource_id_by_tag,
        test_linear_models_service_data_resource,
        shoot_baseline_tasks=False,
        test_description='',
        ammo_overrides=None,
        meta_modes=META_MODES,
):
    return _launch_shoot_tasks(
        task,
        ft_shard_keys,
        shard_map,
        spec_ft_stability_shoot_tasks,
        spec_stat_base_tags_map,
        test_stat_binary_base_resource_id_by_tag,
        spec_meta_base_tags_map,
        test_meta_binary_base_resource_id_by_tag,
        task_type=YabsServerB2BFuncShootStability,
        description='ft stability shoot',
        parent_description=test_description,
        meta_modes=meta_modes,
        ammo_overrides=ammo_overrides,
    )


@stage(provides=('test_ft_validation_tasks', 'baseline_ft_validation_tasks'))
def launch_ft_validation_tasks(task, test_ft_shoot_tasks, baseline_ft_shoot_tasks, spec_ft_validation_tasks, test_description='', shoot_baseline_tasks=False):
    check_tasks(
        task,
        list(chain(
            *(meta_mode_ft_shoot_tasks.values() for meta_mode_ft_shoot_tasks in test_ft_shoot_tasks.values())
        ))
    )
    validation_tasks = {'test': {}, 'baseline': {}}
    for run_type, ft_shoot_tasks in (('test', test_ft_shoot_tasks), ('baseline', baseline_ft_shoot_tasks)):
        if run_type == 'baseline' and not shoot_baseline_tasks:
            validation_tasks[run_type] = spec_ft_validation_tasks
            continue
        for meta_mode, meta_mode_ft_shoot_tasks in ft_shoot_tasks.items():
            for shard_num_str, ft_shoot_task_id in meta_mode_ft_shoot_tasks.items():
                baseline_task_id = spec_ft_validation_tasks[meta_mode][shard_num_str]
                task_parameters = truncate_output_parameters(dict(sdk2.Task[baseline_task_id].Parameters), YabsServerValidateResponses.Parameters)
                task_parameters.update(shoot_task=ft_shoot_task_id)
                validation_tasks[run_type].setdefault(meta_mode, {})[shard_num_str] = _launch_task(
                    task,
                    YabsServerValidateResponses,
                    description='{} validate responses for {} {} | {}'.format(run_type, meta_mode, shard_num_str, test_description),
                    **task_parameters
                )

    return validation_tasks['test'], validation_tasks['baseline']


@stage(provides=('baseline_stat_load_shoot_tasks', 'test_stat_load_shoot_tasks'))
def launch_stat_load_shoot_tasks(
        task,
        spec_stat_load_baseline_tasks,
        spec_stat_base_tags_map,
        spec_meta_base_tags_map,
        shard_map,
        stat_load_shard_keys,
        test_stat_binary_base_resource_id_by_tag,
        baseline_stat_binary_base_resource_id_by_tag,
        test_meta_binary_base_resource_id_by_tag,
        baseline_meta_binary_base_resource_id_by_tag,
        stat_load=False,
        test_description='',
        shoot_baseline_tasks=False,
        meta_modes=META_MODES,
):
    if not stat_load:
        return {}, {}
    stat_load_shoot_tasks = {'test': {}, 'baseline': {}}
    run_type_parameters = (
        (
            'test',
            test_stat_binary_base_resource_id_by_tag,
            test_meta_binary_base_resource_id_by_tag,
        ),
        (
            'baseline',
            baseline_stat_binary_base_resource_id_by_tag,
            baseline_meta_binary_base_resource_id_by_tag,
        ),
    )
    for run_type, stat_binary_base_resource_id_by_tag, meta_binary_base_resource_id_by_tag in run_type_parameters:
        if run_type == 'baseline' and not shoot_baseline_tasks:
            stat_load_shoot_tasks[run_type] = spec_stat_load_baseline_tasks
            continue

        stat_load_shoot_tasks[run_type] = _launch_shoot_tasks(
            task,
            stat_load_shard_keys,
            shard_map,
            spec_stat_load_baseline_tasks,
            spec_stat_base_tags_map,
            stat_binary_base_resource_id_by_tag,
            spec_meta_base_tags_map,
            meta_binary_base_resource_id_by_tag,
            description='{} stat_load shoot'.format(run_type),
            parent_description=test_description,
            task_type=YabsServerStatPerformancePrepareDplan,
            meta_modes=meta_modes,
        )

    return stat_load_shoot_tasks['baseline'], stat_load_shoot_tasks['test']


@stage(provides=('baseline_meta_load_shoot_tasks', 'test_meta_load_shoot_tasks'))
def launch_meta_load_shoot_tasks(
        task,
        spec_stat_base_tags_map,
        spec_meta_base_tags_map,
        spec_meta_load_baseline_tasks,
        meta_load_shard_keys,
        test_stat_binary_base_resource_id_by_tag,
        baseline_stat_binary_base_resource_id_by_tag,
        test_meta_binary_base_resource_id_by_tag,
        baseline_meta_binary_base_resource_id_by_tag,
        meta_load=False,
        test_description='',
        shoot_baseline_tasks=False,
        meta_modes=META_MODES,
):
    if not meta_load:
        return {}, {}

    meta_load_shoot_tasks = {'test': {}, 'baseline': {}}
    run_type_parameters = (
        (
            'test',
            test_stat_binary_base_resource_id_by_tag,
            test_meta_binary_base_resource_id_by_tag,
        ),
        (
            'baseline',
            baseline_stat_binary_base_resource_id_by_tag,
            baseline_meta_binary_base_resource_id_by_tag,
        ),
    )
    for run_type, stat_binary_base_resource_id_by_tag, meta_binary_base_resource_id_by_tag in run_type_parameters:
        if run_type == 'baseline' and not shoot_baseline_tasks:
            meta_load_shoot_tasks[run_type] = spec_meta_load_baseline_tasks
            continue

        meta_load_shoot_tasks[run_type] = {
            meta_mode: _launch_shoot_task(
                task,
                spec_meta_load_baseline_tasks[meta_mode],
                YabsServerPrepareStatStub,
                meta_mode,
                meta_load_shard_keys,
                spec_stat_base_tags_map,
                stat_binary_base_resource_id_by_tag,
                spec_meta_base_tags_map,
                meta_binary_base_resource_id_by_tag,
                description='{} meta_load shoot {}'.format(run_type, meta_mode),
                parent_description=test_description,
            )
            for meta_mode in meta_modes
        }

    return meta_load_shoot_tasks['baseline'], meta_load_shoot_tasks['test']


@stage(provides='ft_validation_cmp_tasks')
def launch_ft_validation_cmp_tasks(task, baseline_ft_validation_tasks, test_ft_validation_tasks, test_description=''):
    meta_modes = set(baseline_ft_validation_tasks.keys()).intersection(set(test_ft_validation_tasks.keys()))
    check_tasks(task, list(chain(*(
        [
            baseline_ft_validation_tasks[meta_mode].values() for meta_mode in meta_modes
        ] + [
            test_ft_validation_tasks[meta_mode].values() for meta_mode in meta_modes
        ]
    ))))
    return {
        meta_mode: {
            ft_shard_num: _launch_task(
                task,
                YabsServerValidateResponsesCmp,
                description='ft validation cmp {}, shard {} | {}'.format(meta_mode, ft_shard_num, test_description),
                pre_task=baseline_ft_validation_tasks[meta_mode][ft_shard_num],
                test_task=test_ft_validation_tasks[meta_mode][ft_shard_num],
            )
            for ft_shard_num in set(test_ft_validation_tasks[meta_mode].keys()).intersection(set(baseline_ft_validation_tasks[meta_mode].keys()))
        }
        for meta_mode in meta_modes
    }


@stage(provides='ft_cmp_tasks')
def launch_ft_cmp_tasks(task, baseline_ft_shoot_tasks, test_ft_shoot_tasks, ttl_for_dump_with_diff=4, test_description='', compare_statuses=True):
    meta_modes = set(baseline_ft_shoot_tasks.keys()).intersection(set(test_ft_shoot_tasks.keys()))
    check_tasks(task, list(chain(*(
        [
            baseline_ft_shoot_tasks[meta_mode].values() for meta_mode in meta_modes
        ] + [
            test_ft_shoot_tasks[meta_mode].values() for meta_mode in meta_modes
        ]
    ))))
    return {
        meta_mode: {
            ft_shard_num: _launch_task(
                task,
                YabsServerB2BFuncShootCmp,
                description='ft cmp {}, shard {} | {}'.format(meta_mode, ft_shard_num, test_description),
                pre_task=baseline_ft_shoot_tasks[meta_mode][ft_shard_num],
                test_task=test_ft_shoot_tasks[meta_mode][ft_shard_num],
                ttl_for_dump_with_diff=ttl_for_dump_with_diff,
                compare_statuses=compare_statuses,
            )
            for ft_shard_num in set(test_ft_shoot_tasks[meta_mode].keys()).intersection(set(baseline_ft_shoot_tasks[meta_mode].keys()))
        }
        for meta_mode in meta_modes
    }


@stage(provides='stat_load_cmp_tasks')
def launch_stat_load_cmp_tasks(task, baseline_stat_load_shoot_tasks, test_stat_load_shoot_tasks, stat_load=False, test_description=''):
    if not stat_load:
        return {}
    meta_modes = set(baseline_stat_load_shoot_tasks.keys()).intersection(set(test_stat_load_shoot_tasks.keys()))
    logger.debug('Will compare stat_load for %s', meta_modes)
    check_tasks(task, list(chain(*(
        [
            baseline_stat_load_shoot_tasks[meta_mode].values() for meta_mode in meta_modes
        ] + [
            test_stat_load_shoot_tasks[meta_mode].values() for meta_mode in meta_modes
        ]
    ))))
    stat_load_cmp_tasks = {}
    for meta_mode in meta_modes:
        baseline_shoot_tasks_by_shard = baseline_stat_load_shoot_tasks[meta_mode]
        test_shoot_tasks_by_shard = test_stat_load_shoot_tasks[meta_mode]
        for shard_num in set(test_shoot_tasks_by_shard.keys()).intersection(set(test_shoot_tasks_by_shard.keys())):
            stat_load_cmp_tasks.setdefault(meta_mode, {})[shard_num] = _launch_task(
                task,
                YabsServerStatPerformanceBestCmp2,
                description='stat_load at {} shard cmp {} | {}'.format(shard_num, meta_mode, test_description),
                pre_task=baseline_shoot_tasks_by_shard[shard_num],
                test_task=test_shoot_tasks_by_shard[shard_num],
            )
    return stat_load_cmp_tasks


@stage(provides='meta_load_cmp_tasks')
def launch_meta_load_cmp_tasks(task, baseline_meta_load_shoot_tasks, test_meta_load_shoot_tasks, meta_load=False, test_description=''):
    if not meta_load:
        return {}
    meta_modes = set(baseline_meta_load_shoot_tasks.keys()).intersection(set(test_meta_load_shoot_tasks.keys()))
    check_tasks(task, baseline_meta_load_shoot_tasks.values() + test_meta_load_shoot_tasks.values())
    meta_load_cmp_tasks = {}
    for meta_mode in meta_modes:
        baseline_shoot_task_id = baseline_meta_load_shoot_tasks[meta_mode]
        test_shoot_task_id = test_meta_load_shoot_tasks[meta_mode]
        meta_load_cmp_tasks[meta_mode] = _launch_task(
            task,
            YabsServerPerformanceMetaCmp,
            description='meta_load cmp {} | {}'.format(meta_mode, test_description),
            pre_task=baseline_shoot_task_id,
            test_task=test_shoot_task_id,
            shoot_request_limit=min(
                sdk2.Task[baseline_shoot_task_id].Parameters.shoot_request_limit,
                sdk2.Task[test_shoot_task_id].Parameters.shoot_request_limit,
            ),
        )
    return meta_load_cmp_tasks
