# -*- coding: utf-8 -*-

import logging
import urllib

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.parameters import ResourceSelector
from sandbox.sandboxsdk.parameters import SandboxIntegerParameter
from sandbox.sandboxsdk.channel import channel

from sandbox.projects.common.dynamic_models.utils import compare_dicts
from sandbox.projects.common.dynamic_models.archiver import get_matrixnets_md5
from sandbox.projects.common.dynamic_models.basesearch import get_basesearch_models

from sandbox.projects import resource_types
from sandbox.projects.common.base_search_quality import basesearch_response_parser
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import file_utils as fu
from sandbox.projects.common import link_builder as lb
from sandbox.projects.common import utils
from sandbox.projects.common import apihelpers


class ModelsArchiveParameter(ResourceSelector):
    name = 'models_archive_resource_id'
    description = 'Models archive'
    resource_type = ['DYNAMIC_MODELS_ARCHIVE', 'DYNAMIC_MODELS_ARCHIVE_BASE']
    required = True


class MemoryLimit(SandboxIntegerParameter):
    name = 'memory_limit'
    description = 'Memory limit for models (kB)'
    default_value = 204800


class TestDynamicModelsArchive(SandboxTask):
    """
        Проверяет что базовый поиск корректно работает с dynamic models archive (архив с формулами):
        Находит archiver, достает из архива имена формул
        Находит базовый, достает из него имена формул
        Формирует параметры &fml на основе имен моделей и тестирует их,
        запуская дочерний таск TEST_BASESEARCH_EXPERIMENT
    """

    type = 'TEST_DYNAMIC_MODELS_ARCHIVE'
    input_parameters = [ModelsArchiveParameter, MemoryLimit]

    @property
    def footer(self):
        head1 = [
            {"key": "memory", "title": "Archive</br>resident pages"},
            {"key": "task_id", "title": "TEST_BASESEARCH<br>task"},
        ]
        head2 = [
            {"key": "formulas", "title": "Formulas"},
            {"key": "model_ids", "title": "Model ids"},
        ]
        return [
            {
                'helperName': '',
                'content': {
                    "<h4>Info</h4>": {
                        "header": head1,
                        "body": {
                            "memory": [self.ctx.get("model_archive_resident", "-")],
                            "task_id": [lb.task_link(self.get_test_basesearch_task_id()) or "-"]
                        },
                    }
                }
            },
            {
                'helperName': '',
                'content': {
                    "<h4>Formulas info</h4>": {
                        "header": head2,
                        "body": {
                            "formulas": sorted(self.ctx.get("formulas", [])),
                            "model_ids": sorted(self.ctx.get("model_ids", [])),
                        },
                    }
                }
            }
        ]

    def on_execute(self):
        if 'child_task_ids' not in self.ctx:
            models_archive_resource_id = self.ctx[ModelsArchiveParameter.name]

            model_ids = self._get_model_ids(models_archive_resource_id)
            new_cgi_params = ["&" + urllib.urlencode({"relev": "fml=:@{0}".format(id)}) for id in model_ids]
            self.ctx['model_ids'] = model_ids

            test_basesearch_exp_task_id = self._test_basesearch_experiment(
                models_archive_resource_id, new_cgi_params
            )

            (get_basesearch_responses_task_id, responses_resource_id) = self._get_basesearch_responses(
                models_archive_resource_id, new_cgi_params
            )

            self.ctx['test_basesearch_exp_task_id'] = test_basesearch_exp_task_id
            self.ctx['responses_resource_id'] = responses_resource_id

            self.ctx['child_task_ids'] = [test_basesearch_exp_task_id,
                                          get_basesearch_responses_task_id]

        utils.check_subtasks_fails(stop_on_broken_children=True)

        test_basesearch_exp_task = channel.sandbox.get_task(self.ctx['test_basesearch_exp_task_id'])
        if 'pmap_RSS_for_models' in test_basesearch_exp_task.ctx:
            archive_resident_kb = test_basesearch_exp_task.ctx['pmap_RSS_for_models']
            self.ctx['model_archive_resident'] = archive_resident_kb
            limit = self.ctx.get(MemoryLimit.name, MemoryLimit.default_value)
            eh.ensure(
                archive_resident_kb <= limit,
                "models archive resident memory is too large:"
                "{}KB > {}KB".format(archive_resident_kb, limit)
            )

        responses = basesearch_response_parser.parse_responses(
            self.sync_resource(self.ctx['responses_resource_id']),
            remove_unstable_props=True,
            use_processes=False,
            c_pickle_dump=False
        )
        eh.verify(len(self.ctx['model_ids']) == len(responses), "diff in amount of model_ids and responses")

        for model_id, response in zip(self.ctx['model_ids'], responses):
            ranking_mn = _get_ranking_mn_searcher_prop(response)
            if model_id != ranking_mn and model_id != ranking_mn.partition("[")[0]:
                eh.fail("basesearch has chosen wrong model: '{}' != '{}'".format(model_id, ranking_mn))

        self.set_info('%s formulas checked' % len(self.ctx['model_ids']))

    def get_test_basesearch_task_id(self):
        if 'test_basesearch_exp_task_id' not in self.ctx:
            return None
        test_basesearch_exp_task = channel.sandbox.get_task(self.ctx['test_basesearch_exp_task_id'])
        return test_basesearch_exp_task.ctx.get('test_basesearch_task_id')

    @staticmethod
    def _compare_models(arch, base):
        if arch != base:
            diff = compare_dicts(arch, base)
            del diff['same']

            def ignore(name):
                pos = name.find('_')
                if pos >= 0:
                    name = name[:pos]
                return name.endswith("FreshExtRelev")

            diff = {key: [v for v in value if not ignore(v)] for key, value in diff.items()}
            if any(diff.values()):
                eh.check_failed("Ranking models in archive and in basesearch are different: {}".format(diff))

    def _get_model_ids(self, models_archive_resource_id):
        archive_models = self._get_models_from_archive(models_archive_resource_id)

        logging.info("formulas from archive: %s", archive_models)
        self.ctx['formulas'] = sorted(archive_models)

        basesearch_models, ids = self._get_models_from_basesearch(models_archive_resource_id)
        logging.info("formulas from basesearch: %s", basesearch_models)

        self._compare_models(archive_models, basesearch_models)

        logging.info("model ids: %s", ids)
        return ids

    def _get_archiver(self):
        archiver = apihelpers.get_resources_with_attribute(
            resource_types.ARCHIVER_TOOL_EXECUTABLE,
            "build_dynamic_models", "24",
            limit=1,
            arch=self.arch
        )
        eh.ensure(archiver, 'Can not get archiver executable')
        return self.sync_resource(archiver[0])

    def _get_models_from_archive(self, models_archive_resource_id):
        archiver = self._get_archiver()
        models_archive = self.sync_resource(models_archive_resource_id)
        return get_matrixnets_md5(archiver, models_archive)

    def _get_stable_basesearch(self):
        stable_basesearch_resource = apihelpers.get_last_released_resource(
            'BASESEARCH_EXECUTABLE',
            arch=self.arch
        )
        eh.ensure(stable_basesearch_resource, 'cannot find stable basesearch')
        return self.sync_resource(stable_basesearch_resource.id)

    def _get_models_from_basesearch(self, models_archive_resource_id):
        stable_basesearch = self._get_stable_basesearch()
        models_archive = self.sync_resource(models_archive_resource_id)

        all_models = get_basesearch_models(
            stable_basesearch, models_archive,
            search_type="",
            tmp_path=self.abs_path("rankingmodels.txt")
        )
        all_models_memory = get_basesearch_models(
            stable_basesearch, models_archive,
            search_type="memory",
            tmp_path=self.abs_path("rankingmodels_memory.txt")
        )
        eh.ensure(all_models == all_models_memory, "ranking models for web basesearch and realsearch are different")

        models = dict(
            (m["matrixnet_name"], m["matrixnet_md5"]) for m in all_models if m["matrixnet_memory_source"] == "dynamic"
        )
        ids = set(m["matrixnet_id"] for m in all_models if m["matrixnet_memory_source"] == "dynamic")

        return models, sorted(ids)

    def _test_basesearch_experiment(self, models_archive_resource_id, new_cgi_params):
        sub_ctx = {
            'use_pmap': True,
            'new_cgi_param': ";".join(new_cgi_params),
            'models_archive_resource_id': models_archive_resource_id
        }
        return self.create_subtask(
            task_type='TEST_BASESEARCH_EXPERIMENT',
            arch=self.arch,
            input_parameters=sub_ctx,
            description=self.descr
        ).id

    def _get_basesearch_responses(self, models_archive_resource_id, new_cgi_params):
        r = self.create_resource(self.descr, "responses.txt", resource_types.PLAIN_TEXT_QUERIES)
        fu.write_lines(r.path, ["?text=test&ms=proto" + param for param in new_cgi_params])
        self.mark_resource_ready(r)

        sub_ctx = {
            'executable_resource_id': apihelpers.get_last_released_resource(
                resource_type=resource_types.BASESEARCH_EXECUTABLE,
                arch=self.arch,
            ).id,
            'config_resource_id': apihelpers.get_last_resource_with_attribute(
                resource_type=resource_types.SEARCH_CONFIG,
                attribute_name='TE_web_base_prod_resources_PlatinumTier0',
            ).id,
            'search_database_resource_id': apihelpers.get_last_resource_with_attribute(
                resource_type=resource_types.SEARCH_DATABASE,
                attribute_name='TE_web_base_prod_resources_PlatinumTier0',
            ).id,
            'models_archive_resource_id': models_archive_resource_id,
            'queries_resource_id': r.id
        }
        task = self.create_subtask(
            task_type='GET_BASESEARCH_RESPONSES',
            arch=self.arch,
            input_parameters=sub_ctx,
            description=self.descr
        )
        return task.id, task.ctx['out_resource_id']


def _get_ranking_mn_searcher_prop(response):
    searcher_props = response._nodes.get("SearcherProp")
    eh.ensure(searcher_props, "search response doesn't have SearcherProp")
    for sp in searcher_props:
        if sp.GetPropValue("Key") == "RankingMn":
            return sp.GetPropValue("Value")
    eh.check_failed("cannot find RankingMn search property in response")


__Task__ = TestDynamicModelsArchive
