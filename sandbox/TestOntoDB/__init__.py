# -*- coding: utf-8 -*-

import copy
from sandbox.projects import resource_types
import sandbox.projects.yane.common as yane

import sandbox.common.types.client as ctc
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.parameters import SandboxStringParameter, SandboxBoolParameter, LastReleasedResource
from sandbox.sandboxsdk.paths import make_folder, copy_path


GROUP_MR_CORPUS = 'MapReduce corpus'
GROUP_MARKUP = 'Markup'


class YaneTestOntoDB(yane.YaneTaskBase):
    """
        Test OntoDB quality
    """

    type = 'YANE_TEST_ONTODB'

    # Arcadia - 16Gb, tools - 5Gb, resource - 3Gb
    execution_space = 25 * 1024

    class BaseType(SandboxStringParameter):
        name = 'base_type'
        description = 'Base type'
        required = True
        group = yane.GROUP_IN
        default_value = 'main'
        choices = [
            ('main', 'main'),
            ('music', 'music')
        ]

    class Config(LastReleasedResource):
        name = 'config'
        description = 'Config'
        resource_type = resource_types.YANE_CONFIG
        group = yane.GROUP_IN

    class SourceTable(SandboxStringParameter):
        name = 'source_ontodb'
        description = 'Source table'
        default_value = 'home/dict/ontodb/ver/main/production/all_cards_final'
        group = yane.GROUP_IN
        required = True

    class PredefinedIds(LastReleasedResource):
        name = 'predefined_ids'
        description = 'Predefined external ids'
        group = yane.GROUP_IN
        resource_type = resource_types.YANE_TSV
        required = False

    class SendTo(SandboxStringParameter):
        name = 'send_to'
        description = 'Send results to (comma-separated list)'

    class UseMRCorpus(SandboxBoolParameter):
        name = 'use_mr_corpus'
        description = 'Test with MapReduce corpus'
        group = GROUP_MR_CORPUS
        default_value = False
        sub_fields = {'true': ['mr_corpus_table', 'mr_object_diff_table', 'mr_doc_diff_table']}

    class MRCorpusTable(SandboxStringParameter):
        name = 'mr_corpus_table'
        group = GROUP_MR_CORPUS
        description = 'MR corpus table for testing'
        default_value = 'home/dict/yane/external.data/corpus/short'
        required = True

    class MRObjectDiffTable(SandboxStringParameter):
        name = 'mr_object_diff_table'
        group = GROUP_MR_CORPUS
        description = 'MR table for output object diff (optional)'
        required = False

    class MRDocDiffTable(SandboxStringParameter):
        name = 'mr_doc_diff_table'
        group = GROUP_MR_CORPUS
        description = 'MR table for output document diff (optional)'
        required = False

    input_parameters = \
        yane.get_base_params().params + \
        [BaseType, Config, SourceTable, PredefinedIds, SendTo] + \
        yane.get_text_params(GROUP_MARKUP).params + \
        [UseMRCorpus] + \
        yane.get_mr_params(GROUP_MR_CORPUS).params + \
        [MRCorpusTable, MRObjectDiffTable, MRDocDiffTable]

    # All MR-clusters are linux-only
    client_tags = ctc.Tag.LINUX_PRECISE

    def __init__(self, task_id=0):
        yane.YaneTaskBase.__init__(self, task_id)
        self.ctx['kill_timeout'] = 3 * 60 * 60

    @property
    def footer(self):
        if self.is_finished():
            return self.ctx['result_html']
        else:
            return {}

    def make_sub_ctx(self, copy_params):
        params = copy.deepcopy(self.ctx)
        for p in copy_params:
            if p in self.ctx:
                params[p] = self.ctx[p]
        return params

    def _parse_ontodb(self):
        if 'parse_task_id' in self.ctx:
            return

        params = self.make_sub_ctx(['base_type', 'config', 'source_ontodb'])
        params['light_data'] = True
        subtask = self.create_subtask('YANE_PARSE_ONTODB',
                                      self.ctx['source_ontodb'],
                                      input_parameters=params,
                                      arch=self.arch)
        self.ctx['ner_resources'] = [subtask.ctx[x] for x in ['gazetteer_id', 'object_data_id', 'synonym_data_id']]
        self.ctx['parse_task_id'] = subtask.id
        self.wait_all_tasks_stop_executing([subtask.id])

    def _run_test(self):
        if 'test_task_id' in self.ctx:
            return

        self.check_tasks('parse_task_id', 'Parse OntoDB')
        make_folder('ner_data', True)
        for res_id in self.ctx['ner_resources']:
            copy_path(self.sync_resource(res_id), 'ner_data')
        ner_data_res = self._create_resource(
            'Light data for {}'.format(self.ctx['source_ontodb']),
            'ner_data',
            resource_types.YANE_DATA,
            arch='any'
        )
        ner_data_res.mark_ready()

        params = self.make_sub_ctx(['config', 'use_mr_corpus', 'mr_corpus_table', 'mr_object_diff_table',
                                    'mr_doc_diff_table', 'texts', 'markup'])
        params['tools_testing'] = self.ctx['tools']
        params['data_testing'] = ner_data_res.id

        subtask = self.create_subtask('YANE_EXTRACTION_DIFF',
                                      'Test data (%s)' % self.ctx['source_ontodb'],
                                      input_parameters=params,
                                      arch=self.arch)
        self.ctx['test_task_id'] = subtask.id
        self.wait_all_tasks_stop_executing([subtask.id])

    def _publish_result(self):
        self.check_tasks('test_task_id', 'Test data')
        subtask = channel.sandbox.get_task(self.ctx['test_task_id'])
        result_html = subtask.ctx['result_html']
        self.ctx['result_html'] = result_html
        if 'send_to' in self.ctx and len(self.ctx['send_to']):
            channel.sandbox.send_email([x.strip() + "@yandex-team.ru" for x in self.ctx['send_to'].split(',') if x.strip()],
                                       None,
                                       "Test results for " + self.ctx['source_ontodb'],
                                       result_html,
                                       'text/html',
                                       'utf-8')

    def do_execute(self):
        self._parse_ontodb()
        self._run_test()
        self._publish_result()


__Task__ = YaneTestOntoDB
