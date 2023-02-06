# -*- coding: utf-8 -*-
import json
import logging
import os
import time

from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.common.types.misc import NotExists
from sandbox.common.types.resource import State
from sandbox.common.types.task import Status
from sandbox.projects import resource_types
from sandbox.projects.common import apihelpers
from sandbox.projects.websearch.begemot import AllBegemotServices, resources
from sandbox.projects.websearch.begemot.common import Begemots
from sandbox.projects.websearch.begemot.tasks.BegemotYT.BegemotMapper import BegemotMapper
from sandbox.projects.websearch.begemot.tasks.BegemotYT.BegemotReducer import BegemotReducer
from sandbox.projects.websearch.begemot.tasks.BegemotYT.common import CommonYtParameters
from sandbox.projects.websearch.begemot.tasks.BegemotYT.MiddleSearchCacheHitGuess2 import MiddleSearchCacheHitGuess2
from sandbox.projects.websearch.begemot.tasks.BegemotYT.paths import BegemotYtPaths
from sandbox.projects.websearch.begemot.tasks.BuildBegemotData import BuildBegemotData
from sandbox.projects.websearch.begemot.tasks.GetWorkerMaxrssDifference import GetWorkerMaxrssDifference
from sandbox.projects.websearch.begemot.tasks.MergeBegemotFreshRevisions import MergeBegemotFreshRevisions
from sandbox.sandboxsdk import environments
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.svn import Arcadia

FRESH_SVN_URL = "arcadia:/arc/trunk/arcadia/search/wizard/data/fresh"
IMAGES_CV = 'ImagesCV'

cache_affecting_rrr = {
    'Video': ['SerialStruct', 'lastEpisode', 'lastAirdate', 'lastAirdateProb', 'lastSeason',
              'recentlyReleasedEpisodes'],
    'EntityFinder': ['MatchesExport'],
}

def id_list(resources_list):
    return [r.id if r is not None else None for r in resources_list]

class TestBegemotFreshParams(sdk2.Parameters):
    fast_build = sdk2.parameters.Bool(
        "Use fast build",
        default=True,
        description="Build a resource for each rule instead of a package for each shard."
    )
    with fast_build.value[True]:
        common_config = sdk2.parameters.Bool(
            'Build common config for all services',
            default=True
        )
    with sdk2.parameters.CheckGroup('Begemot shards to test') as shards_to_test:
        for shard_name in sorted(Begemots.BegemotFreshShards):
            shard = Begemots[shard_name]
            setattr(
                shards_to_test.values, shard_name,
                shards_to_test.Value(shard_name, checked=shard.release_fresh),
            )
    cache_guess_requests = sdk2.parameters.Integer(
        'Number of rows used in %s. If 0, the task will not be started' % MiddleSearchCacheHitGuess2.type,
        default=50000,
    )
    yt_proxy = CommonYtParameters.yt_proxy()
    yt_pool = CommonYtParameters.yt_pool()
    yt_token_vault_owner = CommonYtParameters.yt_token_vault_owner()
    yt_token_vault_name = CommonYtParameters.yt_token_vault_name()
    test_maxrss_diff = sdk2.parameters.Bool('Test maxrss difference', default=False)
    prebuilt_fresh = sdk2.parameters.Integer(
        'BUILD_BEGEMOT_DATA or MERGE_BEGEMOT_FRESH_REVISIONS task id with prebuilt fresh to release',
        description='Leave blank to run a new build. If you run TEST_BEGEMOT_FRESH, you can also type WIZARD_RUNTIME_BUILD or WIZARD_RUNTIME_BUILD_PATCHED id',
        default=None,
        required=False,
    )

class TestBegemotFresh(sdk2.Task):
    __logger = logging.getLogger('TASK_LOGGER')
    __logger.setLevel(logging.DEBUG)

    class Parameters(TestBegemotFreshParams):
        arcadia_revision = sdk2.parameters.Integer(
            'Arcadia revision to checkout',
            resource_type = resource_types.WIZDATA_PATCH,
            required=False,
            default=None,
            description='Default: latest'
        )
        fresh_patch = sdk2.parameters.Resource(
            'Arcadia fresh patch',
            required=False,
            default=None,
            description='Arcadia Patch, basedir: search/wizard/data/fresh'
        )
        build_begemot = sdk2.parameters.Bool(
            'Also build begemot binary and shards from Arcadia',
            required=False,
            default=False
        )
        arcadia_patch = sdk2.parameters.String(
            'Apply patch (link to Arcanum review formatted as `arc:id`, diff file rbtorrent, paste.y-t.ru link or plain text). Doc: https://nda.ya.ru/3QTTV4',
            required=False,
            default='',
            multiline=True,
            description='Patch is used for begemot build. Use "Arcadia fresh patch" to patch fresh'
        )

    class Context(sdk2.Context):
        pending_tasks = []
        maxrss_diff = dict()
        maxrss_tasks = dict()
        fresh_resources = dict()
        fresh_torrents = dict()
        try_merge = False
        problem_tasks = {}

    class Requirements(sdk2.Requirements):
        disk_space = 512
        environments = (
            environments.PipEnvironment('yasmapi'),
        )

    @classmethod
    def get_cache_affecting_keys(cls):
        return [
            'rules.%s.%s' % (rule, field)
            for rule, fields in cache_affecting_rrr.items()
            for field in fields
        ]

    def parse_worker_stderr(self, stderr):
        splitted = stderr.split("some rules could not be initialized")
        if len(splitted) > 1:
            return splitted[1].split("E.g.: ")[1].split('"')[0]
        return None

    def check_failed_reducer(self, task_id):
        problem_rules = set()
        task = sdk2.Task.find(id=task_id).first()
        for worker in task.Context.rules_errors:
            for rule in task.Context.rules_errors[worker]:
                problem_rules.add(rule)
                self.Context.problem_tasks[rule] = task_id
        for worker in task.Context.stderrs:
            rule = self.parse_worker_stderr(task.Context.stderrs[worker])
            if rule is not None:
                problem_rules.add(rule)
                self.Context.problem_tasks[rule] = task_id
        self.Context.problem_rules = list(problem_rules)

    def check_pending_tasks(self):
        self.__logger.info('Checking tasks status %s' % ','.join(map(str, self.Context.pending_tasks)))
        found_failures = False
        for task_id in self.Context.pending_tasks:
            task = sdk2.Task.find(id=task_id, children=True).first()
            self.__logger.info('Status for task #{}: {}'.format(task_id, task.status))
            if task.status != Status.SUCCESS:
                if self.Context.begemot_reducer_new is not NotExists and task_id == self.Context.begemot_reducer_new:
                    self.check_failed_reducer(task_id)
                found_failures = True
                fail_msg = 'Task #%d failed' % task_id
        if found_failures and not (len(self.Context.problem_rules) and not self.Context.try_merge):
            raise TaskFailure(fail_msg)
        self.__logger.info('All tasks have successfully finished')
        self.Context.pending_tasks = []

    def build_patched(self):
        tasks_descr = 'Created by TEST_BEGEMOT_FRESH task #{}'.format(self.id)
        revision = self.Parameters.arcadia_revision
        if revision is None:
            revision = Arcadia.info(FRESH_SVN_URL)['commit_revision']
        shards_to_build = self.Parameters.shards_to_test
        if 'Merger' not in shards_to_build:
            shards_to_build.append('Merger')
        shards_to_build_param = ' '.join([shard for shard in self.Parameters.shards_to_test])
        patch = self.Parameters.fresh_patch.id if self.Parameters.fresh_patch is not None else None
        arcadia_url = "arcadia:/arc/trunk/arcadia@{}".format(revision)

        if not self.Parameters.fast_build:
            task = sdk2.Task['WIZARD_RUNTIME_BUILD_PATCHED']
            self.Context.new_runtime_task = task(
                self,
                production_build=False,
                begemot_shards=shards_to_build_param,
                arcadia_revision=revision,
                patch_arcadia=patch,
                description=tasks_descr,
                inherit_notifications=True,
            ).enqueue().id
        else:
            task = sdk2.Task['BUILD_BEGEMOT_DATA']
            self.Context.new_runtime_task = task(
                self,
                ShardName=shards_to_build_param,
                BuildFresh=True,
                AllInOneConfig=self.Parameters.common_config,
                UseFastBuild=True,
                checkout_arcadia_from_url=arcadia_url,
                arcadia_patch=self.Parameters.arcadia_patch,
                description=tasks_descr
            ).enqueue().id
        self.Context.pending_tasks.append(self.Context.new_runtime_task)

        if self.Parameters.build_begemot:
            mapper_task = sdk2.Task['BUILD_BEGEMOT_EXECUTABLE']
            self.Context.begemot_mapper_task = mapper_task(
                self,
                want_testing_utilities=True,
                want_release_utilities=False,
                want_begemot_binary=self.Parameters.test_maxrss_diff,
                want_begemot_fast_build_binary=False,
                checkout_arcadia_from_url=arcadia_url,
                arcadia_patch=self.Parameters.arcadia_patch,
                description=tasks_descr
            ).enqueue().id
            self.Context.pending_tasks.append(self.Context.begemot_mapper_task)
            shard_tasks = {}
            for shard in shards_to_build:
                shard_task = sdk2.Task['BUILD_BEGEMOT_DATA']
                shard_tasks[shard] = shard_task(
                    self,
                    description=tasks_descr,
                    ShardName=shard,
                    build_system='ya_force',
                    checkout_arcadia_from_url=arcadia_url,
                    arcadia_patch=self.Parameters.arcadia_patch,
                ).enqueue().id
                self.Context.pending_tasks.append(shard_tasks[shard])
            self.Context.shard_tasks = shard_tasks
        raise sdk2.WaitTask(self.Context.pending_tasks, Status.Group.FINISH | Status.Group.BREAK)

    def get_min_free_memory(self, shard_name):
        from yasmapi import GolovanRequest
        period = 300
        geo = ['sas', 'man', 'vla']
        service = AllBegemotServices.Service[shard_name]
        res = 1 << 50
        self.__logger.info('Getting free memory for shard %s:' % shard_name)
        for g in geo:
            golovan_request_prefix = 'itype=begemot;ctype=prestable,prod;geo=%s;prj=%s:' % (g, service.prj)
            limit_sig = golovan_request_prefix + 'min(portoinst-memory_guarantee_slot_hgram)'
            usage_sig = golovan_request_prefix + 'begemot-WORKER-memory-current-rss_axxx'
            signals = [limit_sig, usage_sig]
            et = time.time() - period * 5
            st = et - period * 5
            memory_limit = 0
            memory_usages = []
            for timestamp, values in GolovanRequest('ASEARCH', period, st, et, signals):
                memory_limit = max(memory_limit, int(values[limit_sig]))
                memory_usages += [values[usage_sig]]
            memory_usage = sorted(memory_usages)[2]
            self.__logger.info('Geo = %s, Memory limit = %d, memory usage = %d' % (g, memory_limit, memory_usage))
            res = min(res, memory_limit - memory_usage)
        return res

    def get_main_fresh_resources(self, task_id, res_types):
        return [
            sdk2.Resource.find(
                task_id=task_id,
                resource_type=rt
            ).first()
            for rt in res_types
        ]

    def get_fresh_resources(self):
        shard_names = [
            shard_name for shard_name in AllBegemotServices.BegemotFreshShards
            if AllBegemotServices.Service[shard_name].fresh_data_resource_packed_type.name in self.Context.fresh_resources
            or AllBegemotServices.Service[shard_name].fresh_fast_build_config_resource_type.name in self.Context.fresh_resources
        ]
        if not shard_names:
            try:
                task = sdk2.Task.find(id=self.Context.new_runtime_task).first()
                shard_names = [shard_name for shard_name in AllBegemotServices.BegemotFreshShards if AllBegemotServices.Service[shard_name].name in task.Context.begemot_shard_resource_ids]
            except Exception:
                shard_names = [name for name, s in Begemots if s.release_fresh]
        fresh_old = [
            apihelpers.get_last_released_resource_with_attr(
                resources.BEGEMOT_CYPRESS_SHARD,
                attrs={'shard_name': shard_name, 'is_fresh': 'True', 'is_broken': 'False'},
                all_attrs=True,
            )
            for shard_name in shard_names
        ]
        if None in fresh_old:
            fresh_old_found = [s.attributes['shard_name'] for s in fresh_old if s is not None]
            self.set_info('WARN: previous released fresh %s not found' % (
                ','.join(set(AllBegemotServices.BegemotFreshShards).difference(fresh_old_found))
            ))

        fresh_new = [
            sdk2.Resource.find(
                resource_type=resources.BEGEMOT_CYPRESS_SHARD,
                task_id=self.Context.new_runtime_task,
                attrs={'is_fresh': True, 'shard_name' : shard_name, 'is_broken': False}, status=State.READY,
            ).first()
            for shard_name in shard_names
        ]
        try:
            fresh_new_ids = [task.id for task in fresh_new]
        except Exception as e:
            self.set_info(e)
            raise TaskFailure("New BEGEMOT_CYPRESS_SHARD resources are broken")

        old_task = [s for s in fresh_old if s is not None][0].task_id
        self.Context.old_runtime_task = old_task
        unpacked_res_types = [AllBegemotServices.Service[shard_name].fresh_data_resource_type for shard_name in shard_names]
        fast_build_res_types = [AllBegemotServices.Service[shard_name].fresh_fast_build_config_resource_type for shard_name in shard_names]
        common_fast_build_res_types = [resources.BEGEMOT_FAST_BUILD_FRESH_CONFIG for shard_name in shard_names]

        resources_old = self.get_main_fresh_resources(old_task, unpacked_res_types)
        if None in resources_old:
            resources_old = self.get_main_fresh_resources(old_task, fast_build_res_types)
        if None in resources_old:
            resources_old = self.get_main_fresh_resources(old_task, common_fast_build_res_types)

        if self.Parameters.fast_build:
            if self.Parameters.common_config:
                resources_new = self.get_main_fresh_resources(self.Context.new_runtime_task, common_fast_build_res_types)
                self.Context.common_config = resources_new[0].id
            else:
                resources_new = self.get_main_fresh_resources(self.Context.new_runtime_task, fast_build_res_types)
        else:
            resources_new = self.get_main_fresh_resources(self.Context.new_runtime_task, unpacked_res_types)

        return fresh_old, fresh_new, resources_old, resources_new

    def get_packages(self, after_merge=False):
        try:
            self.Context.use_released_begemot = not self.Parameters.build_begemot
        except:
            self.Context.use_released_begemot = True

        old_cypress, new_cypress, old_resources, new_resources = self.get_fresh_resources()
        old_cypress_ids, new_cypress_ids, old_res_ids, new_res_ids = id_list(old_cypress), id_list(new_cypress), id_list(old_resources), id_list(new_resources)
        cypress_pairs, resources_pairs = [], []
        for i, res in enumerate(old_cypress_ids):
            cypress_pairs.append({'old': old_cypress_ids[i], 'new': new_cypress_ids[i]})
            resources_pairs.append({'old': old_res_ids[i], 'new': new_res_ids[i]})
        res_types = 'fast_build_configs' if self.Parameters.fast_build else 'unpacked_fresh'
        self.Context.resources_pairs = {'cypress_shards': cypress_pairs, res_types: resources_pairs}
        return old_cypress, new_cypress_ids

    def get_yt_output_path(self, after_merge=False):
        path = BegemotYtPaths.get_sandbox_path() + '/' + MiddleSearchCacheHitGuess2.type + '/' + str(self.id)
        if after_merge:
            path += "_2"
        return path

    def filter_shards(self, ids, shards_to_test):
        if ids is None:
            return set()
        filtered_ids = []
        for id in ids:
            for shard in shards_to_test:
                try:
                    res=sdk2.Resource.find(id=id, attrs={'shard_name': shard}).first().id
                    filtered_ids.append(id)
                    break
                except:
                    pass
        return set(filtered_ids)

    def get_last_released_evlog_mapper(self):
        return sdk2.Resource["BEGEMOT_YT_EVENTLOG_MAPPER"].find(state='READY', attrs={'released': 'stable'}).first().id

    def run_begemot_mapper(self, mapper, shard, fresh, shard_name, input_table):
        mapper_id = BegemotMapper(
            self,
            description='Begemot mapper %s' % shard_name,
            service='begemot',
            begemot_mapper=mapper.id,
            eventlog_mapper=self.get_last_released_evlog_mapper(),
            shard=shard,
            fresh=fresh,
            eventlog_table=input_table,
            output_path=self.get_yt_output_path(self.Context.try_merge) + '/answers_new/special_{}'.format(shard_name),
            yt_proxy=self.Parameters.yt_proxy,
            yt_token_vault_owner=self.Parameters.yt_token_vault_owner,
            yt_token_vault_name=self.Parameters.yt_token_vault_name,
            yt_pool=self.Parameters.yt_pool,
            wait_time=20,
            results_store_time=1,
            job_count=5,
            threads=5,
        ).enqueue().id
        self.Context.pending_tasks.append(mapper_id)

    def run_begemot_reducers(self, fresh_old, fresh_new_ids):
        self.__logger.info('Starting {}'.format(MiddleSearchCacheHitGuess2.type))
        shard_names = self.Parameters.shards_to_test
        if 'Merger' not in shard_names:
            shard_names.append('Merger')
        self.__logger.info('Shards to test: {}'.format(shard_names))

        if not self.Context.use_released_begemot:
            mapper = sdk2.Resource.find(
                type=resources.BEGEMOT_YT_MAPPER,
                task_id=self.Context.begemot_mapper_task
            ).first()
            shards = [
                sdk2.Resource.find(
                    task_id=self.Context.shard_tasks[shard_name],
                    type=resources.BEGEMOT_CYPRESS_SHARD,
                ).first()
                for shard_name in shard_names
            ]
        else:
            mapper = apihelpers.get_last_released_resource(resources.BEGEMOT_YT_MAPPER)
            if mapper is None:
                raise TaskFailure('Released begemot yt mapper not found')
            shards = [
                apihelpers.get_last_released_resource_with_attr(
                    resources.BEGEMOT_CYPRESS_SHARD,
                    attrs={'shard_name': shard_name, 'is_fresh': 'False'},
                    all_attrs=True,
                )
                for shard_name in shard_names
            ]

        if None in shards:
            shards_found = [s.attributes['shard_name'] for s in shards if s is not None]
            raise TaskFailure('Released shards {} not found'.format(set(shard_names).difference(shards_found)))
        shards_ids = [s.id for s in shards]

        if None in fresh_old:
            fresh_old_found = [s.attributes['shard_name'] for s in fresh_old if s is not None]
            self.set_info('WARN: previous released fresh %s not found' % (
                ','.join(set(AllBegemotServices.BegemotFreshShards).difference(fresh_old_found))
            ))
        fresh_old_ids = [s.id for s in fresh_old if s is not None]
        fresh_new_ids = [s for s in fresh_new_ids if s is not None]

        self.__logger.info('Mapper: {}'.format(mapper.id))
        self.__logger.info('Shards: {}'.format(shards_ids))
        self.__logger.info('Fresh old: {}'.format(fresh_old_ids))
        self.__logger.info('Fresh new: {}'.format(fresh_new_ids))

        for old in fresh_old:
            if old is not None:
                try:
                    prev_wizard_runtime_release = channel.sandbox.get_task(old.task_id).parent_id
                except:
                    prev_wizard_runtime_release = sdk2.Task.find(id=old.task_id, children=True).first().parent.id
                break
        else:
            raise TaskFailure('Unable to find any previous release, something went wrong')

        self.__logger.info('Previous %s task id = %s' % (self.type, prev_wizard_runtime_release))
        reducers = channel.sandbox.list_tasks(
            task_type=BegemotReducer.type,
            parent_id=prev_wizard_runtime_release,
            children=True,
            get_id_only=True,
        )
        reducers = sorted(reducers, reverse=True)
        self.__logger.info('%s child tasks of previous %s: %s' % (BegemotReducer.type, self.type, str(reducers)))
        reducer = BegemotReducer.find(id=reducers[0], children=True).first() if reducers else None
        self.__logger.info('Reducer: %s' % reducer)
        prev_input = reducer.Parameters.eventlog_table if reducer else None
        prev_mapper = reducer.Parameters.begemot_mapper.id if reducer else None

        input_table = BegemotYtPaths.get_last_eventlog_table() + '[#0:#%d]' % self.Parameters.cache_guess_requests

        if IMAGES_CV in shard_names:
            idx = shard_names.index(IMAGES_CV)
            shard_names.remove(IMAGES_CV)
            requests_num = self.Parameters.cache_guess_requests if self.Parameters.cache_guess_requests < 10000 else 10000
            cv_input = BegemotYtPaths.get_last_eventlog_table('cv', 'man') + '[#0:#%d]' % requests_num
            self.run_begemot_mapper(mapper, shards_ids[idx], fresh_new_ids[idx], IMAGES_CV, cv_input)

            del shards_ids[idx]
            del fresh_old_ids[idx]
            del fresh_new_ids[idx]

        prev_shards = set(map(lambda x: x.id, reducer.Parameters.shards)) if reducer else None
        prev_shards = self.filter_shards(prev_shards, shard_names)

        if prev_input != input_table or prev_shards != set(shards_ids) or prev_mapper != mapper.id:
            old_mapper_shards = shards_ids
            old_mapper_id = mapper.id
            if not self.Context.use_released_begemot:
                if prev_mapper is not None and prev_shards is not None:
                    old_mapper_id = prev_mapper
                    old_mapper_shards = prev_shards
                else:
                    self.set_info("WARNING: previous binary or slow data not found. Will run <New binary with old fresh> vs. <New binary with new fresh> test.")
            self.__logger.info('Creating new %s task' % BegemotReducer.type)
            self.Context.begemot_reducer_old = BegemotReducer(
                self, description=self.Parameters.description,
                eventlog_table=input_table, output_path=self.get_yt_output_path(self.Context.try_merge) + '/answers_old',
                begemot_mapper=old_mapper_id, shards=old_mapper_shards, fresh=fresh_old_ids,
                yt_token_vault_owner=self.Parameters.yt_token_vault_owner,
                yt_token_vault_name=self.Parameters.yt_token_vault_name,
                yt_proxy=self.Parameters.yt_proxy, yt_pool=self.Parameters.yt_pool, wait_time=20, job_count=1,
            ).enqueue().id
            self.Context.pending_tasks.append(self.Context.begemot_reducer_old)
        else:
            self.__logger.info('Using previous %s task with id = %d' % (BegemotReducer.type, reducer.id))
            self.Context.begemot_reducer_old = reducer.id

        self.__logger.info('Creating second %s task' % BegemotReducer.type)
        self.Context.begemot_reducer_new = BegemotReducer(
            self, description=self.Parameters.description,
            eventlog_table=input_table, output_path=self.get_yt_output_path(self.Context.try_merge) + '/answers_new',
            begemot_mapper=mapper.id, shards=shards_ids, fresh=fresh_new_ids,
            yt_token_vault_owner=self.Parameters.yt_token_vault_owner,
            yt_token_vault_name=self.Parameters.yt_token_vault_name,
            yt_proxy=self.Parameters.yt_proxy, yt_pool=self.Parameters.yt_pool, wait_time=20, job_count=1,
        ).enqueue().id
        self.Context.pending_tasks.append(self.Context.begemot_reducer_new)

    def run_maxrss_diff_tests(self, after_merge=False):
        self.__logger.info('Getting memory usage difference')
        if not after_merge:
            task = channel.sandbox.get_task(self.Context.new_runtime_task)
        else:
            task = sdk2.Task.find(id=self.Context.new_runtime_task).first()
        if self.Context.use_released_begemot:
            begemot_binary = apihelpers.get_last_released_resource(resources.BEGEMOT_EXECUTABLE)
        else:
            begemot_binary = sdk2.Resource.find(type=resources.BEGEMOT_EXECUTABLE, task_id=self.Context.begemot_mapper_task).first()
        bstr_callback_binary = apihelpers.get_last_released_resource(resources.BEGEMOT_BSTR_CALLBACK)
        for shard in self.Parameters.shards_to_test:
            self.__logger.info('Running worker %s' % shard)
            res_name = AllBegemotServices.Service[shard].fresh_resource_name if not self.Parameters.fast_build else AllBegemotServices.Service[shard].fresh_fast_build_config_resource_name
            if not after_merge:
                fresh_resource = task.ctx.get(res_name) or task.ctx.get('begemot_shard_resource_ids')[shard]
            else:
                fresh_resource = task.Context.out_resources.get(res_name)

            if self.Context.use_released_begemot:
                fb_config=apihelpers.get_last_released_resource(AllBegemotServices.Service[shard].fast_build_config_resource_name).id
            else:
                fb_config=sdk2.Resource.find(type=AllBegemotServices.Service[shard].fast_build_config_resource_name, task_id=self.Context.shard_tasks[shard]).first().id

            try:
                old_fresh_res = sdk2.Resource.find(task_id=self.Context.old_runtime_task, type=AllBegemotServices.Service[shard].fresh_resource_name).first().id
            except AttributeError:
                old_fresh_res = sdk2.Resource.find(task_id=self.Context.old_runtime_task, type=AllBegemotServices.Service[shard].fresh_fast_build_config_resource_name).first().id
            self.Context.maxrss_tasks[shard] = GetWorkerMaxrssDifference(
                self,
                description='Begemot worker %s' % shard,
                begemot_binary=begemot_binary.id,
                bstr_callback_binary=bstr_callback_binary.id,
                fast_build_config=fb_config,
                fresh_old=old_fresh_res,
                fresh_new=fresh_resource
            ).enqueue().id

    def run_cache_guess(self):
        answers_old = BegemotReducer.find(id=self.Context.begemot_reducer_old, children=True).first().Parameters.answers
        answers_new = BegemotReducer.find(id=self.Context.begemot_reducer_new, children=True).first().Parameters.answers
        task = MiddleSearchCacheHitGuess2(
            self, description=self.Parameters.description,
            begemot_answers_old=answers_old, begemot_answers_new=answers_new,
            output_path=self.get_yt_output_path(self.Context.try_merge) + '/cache_guess',
            keys=self.get_cache_affecting_keys(), limit=1000,
            yt_token_vault_owner=self.Parameters.yt_token_vault_owner,
            yt_token_vault_name=self.Parameters.yt_token_vault_name,
            yt_proxy=self.Parameters.yt_proxy, yt_pool=self.Parameters.yt_pool,
        )
        self.Context.cache_guess_2 = task.enqueue().id
        self.Context.pending_tasks.append(self.Context.cache_guess_2)

    def collect_tests_results(self, after_merge=False):
        info = []
        for shard_name, task_id in self.Context.maxrss_tasks.items():
            maxrss_diff = GetWorkerMaxrssDifference.find(id=task_id, children=True).first().Parameters.maxrss_diff
            self.Context.maxrss_diff[shard_name] = maxrss_diff
            info.append("Maxrss diff for shard %s: %.2fGB" % (shard_name, float(maxrss_diff) / (1 << 30)))

        cache_guess_task = MiddleSearchCacheHitGuess2.find(id=self.Context.cache_guess_2, children=True).first()
        self.Context.cache_guess_stats = cache_guess_task.Context.diff_rules
        info.extend([
            "Answers diff: %f%%" % (float(cache_guess_task.Parameters.answers_diff) * 100),
            "Cache guess: %.4f -> %.4f" % (cache_guess_task.Parameters.cache_guess_old, cache_guess_task.Parameters.cache_guess_new),
            "See more in MIDDLE_SEARCH_CACHE_HIT_GUESS_2 child task info"
        ])
        self.set_info("\n".join(info))

    def run_all_tests(self, prefix):
        with self.memoize_stage[prefix + "_get_packages"](commit_on_entrance=False):
            old_cypress, new_cypress_ids = self.get_packages(after_merge=self.Context.try_merge)

        with self.memoize_stage[prefix + "_run_maxrss_tests"](commit_on_entrance=False):
            if self.Parameters.test_maxrss_diff:
                self.run_maxrss_diff_tests(after_merge=self.Context.try_merge)
            else:
                self.__logger.info('Maxrss difference test disabled')

        with self.memoize_stage[prefix + "_run_begemot_reducers"](commit_on_entrance=False):
            self.run_begemot_reducers(old_cypress, new_cypress_ids)
            raise sdk2.WaitTask(self.Context.pending_tasks, Status.Group.FINISH | Status.Group.BREAK)

        with self.memoize_stage[prefix + "_run_cache_hit_guess_2"](commit_on_entrance=False):
            if self.Context.problem_rules is NotExists or not len(self.Context.problem_rules):
                self.run_cache_guess()
            for task_id in self.Context.maxrss_tasks.values():
                self.Context.pending_tasks.append(task_id)
            raise sdk2.WaitTask(self.Context.pending_tasks, Status.Group.FINISH | Status.Group.BREAK)

        with self.memoize_stage[prefix + "_check_diff"](commit_on_entrance=False):
            if self.Context.problem_rules is NotExists or not len(self.Context.problem_rules):
                self.collect_tests_results(after_merge=self.Context.try_merge)
            else:
                self.set_info("Found problems with following rules: {}".format(self.Context.problem_rules))

    def on_execute(self):
        self.check_pending_tasks()

        if self.Parameters.prebuilt_fresh is not None:
            self.Context.new_runtime_task = self.Parameters.prebuilt_fresh

        # check if new_runtime_task has MERGE_BEGEMOT_FRESH_REVISIONS type
        try:
            merge_task = sdk2.Task.find(task_type=MergeBegemotFreshRevisions, id=self.Context.new_runtime_task).first().id
            self.set_info("Merge task: {}".format(merge_task))
            self.Context.try_merge = True
        except:
            self.Context.try_merge = False

        with self.memoize_stage.build_patched(commit_on_entrance=False):
            if self.Parameters.prebuilt_fresh is None:
                self.build_patched()

        if self.Parameters.cache_guess_requests > 0:
            self.run_all_tests("test_task")
        else:
            self.set_info("Build OK")
        if self.Context.problem_rules is not NotExists and len(self.Context.problem_rules):
            raise TaskFailure("Begemot reducer failed")
