# -*- coding: utf-8 -*-

import logging
import os.path
import json
import tempfile

from sandbox.projects import resource_types
from sandbox.projects.common import apihelpers
import sandbox.projects.yane.common as yane
from quality import split_pool, calc_splits_qualities, quality
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.parameters import LastReleasedResource, SandboxIntegerParameter, \
    SandboxFloatParameter, SandboxBoolParameter, SandboxStringParameter, SandboxRadioParameter
from sandbox.sandboxsdk.paths import make_folder, copy_path, remove_path
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk import environments


NUMBER_OF_SPLITS_DEFAULT = 10


class YaneTestTask(yane.YaneLearnTaskBase):
    """
        Calculate quality of entity extraction
    """
    type = 'YANE_TEST_TASK'

    environment = (environments.PipEnvironment('xlwt'),)

    execution_space = 60 * 1024

    class YaneData(LastReleasedResource):
        name = 'data'
        description = 'Yane data (leave blank to get from SVN)'
        resource_type = resource_types.YANE_DATA
        required = False
        do_not_copy = True

    class MatrixnetBinary(LastReleasedResource):
        name = 'matrixnet'
        description = 'Matrixnet binary'
        resource_type = resource_types.MATRIXNET_EXECUTABLE
        required = False

    class NumberOfSplits(SandboxIntegerParameter):
        name = 'splits'
        description = 'Number of splits (min. 2)'
        default_value = NUMBER_OF_SPLITS_DEFAULT
        required = True

        @classmethod
        def cast(cls, value):
            value = super(YaneTestTask.NumberOfSplits, cls).cast(value)
            if value is not None and value < 2:
                raise ValueError("Value {!r} less than 2".format(value))
            return value

    class Threshold(SandboxFloatParameter):
        name = 'threshold'
        description = 'Threshold'
        default_value = 0.0
        required = True

    class CreateFeaturesResource(SandboxBoolParameter):
        name = 'features_resource'
        description = 'Create features resource'
        default_value = True

    class LearnModel(SandboxBoolParameter):
        name = 'learn_model'
        description = 'Learn model on pool'
        default_value = True

    class CreatePoolResource(SandboxBoolParameter):
        name = 'pool_resource'
        description = 'Create pool resource'
        default_value = True
        sub_fields = {'true': ['learn_model']}

    class LearnSignificaneModel(SandboxBoolParameter):
        name = 'learn_significance_model'
        description = 'Learn significance model'
        default_value = False
        sub_fields = {
            'true': ['significance_iters', 'significance_threshold']
        }

    class SignificanceNumberOfIterations(SandboxIntegerParameter):
        name = 'significance_iters'
        description = 'Number of iterations for significance model'
        default_value = 5000
        required = True

        @classmethod
        def cast(cls, value):
            value = super(YaneTestTask.SignificanceNumberOfIterations, cls).cast(value)
            if value is not None and value < 0:
                raise ValueError("Negative value {!r}".format(value))
            return value

    class SignificanceThreshold(SandboxFloatParameter):
        name = 'significance_threshold'
        description = 'Significance Threshold'
        default_value = 0.5
        required = True

    class UseFormula(SandboxRadioParameter):
        name = 'formula'
        description = 'Use formula type'
        default_value = 'text'
        choices = [('Text', 'text'), ('Query', 'query'), ('Video', 'video'), ('Music', 'music'), ('Yobject', 'yobject')]
        per_line = 2
        sub_fields = {
            'text': ['extraction_languages'],
            'query': ['extraction_languages'],
            'video': ['extraction_languages'],
        }

    class DisableFeatures(SandboxStringParameter):
        name = 'disable_features'
        description = 'Disable features by their ordinal numbers (comma-separated, 0-based).'
        required = False

        @classmethod
        def cast(cls, value):
            value = super(YaneTestTask.DisableFeatures, cls).cast(value)
            if value and len([elem for elem in value.split(',') if not elem.isdigit()]) != 0:
                raise ValueError
            return value

    class ExtractionLanguages(SandboxStringParameter):
        name = 'extraction_languages'
        description = 'Extraction languages (not for music and yobject formulas)'
        default_value = 'ru'
        required = True

        languages = ('ru', 'tr', 'ru, tr')
        choices = [(lang, lang) for lang in languages]

    class FeaturesPool(LastReleasedResource):
        name = 'features_pool'
        description = 'Custom features pool'
        resource_type = [resource_types.YANE_TSV, resource_types.YANE_POOL]
        required = False

    class FilterStep(SandboxBoolParameter):
        name = 'filter_hypos'
        description = 'Learn light formula and filter hypos'
        default_value = False
        sub_fields = {'true': ['filter_threshold', 'filter_matrixnet_options']}

    class FilterThreshold(SandboxFloatParameter):
        name = 'filter_threshold'
        description = 'Threshold for fast hypo filtering'
        required = False

    class FilterMXOptions(SandboxStringParameter):
        name = 'filter_matrixnet_options'
        description = 'Matrixnet options for fast hypo filtering'
        required = False

    class WithBorsches(SandboxBoolParameter):
        name = 'with_borsches'
        description = 'Learn model with borsches'
        default_value = False

    input_parameters = (
        [YaneData, ExtractionLanguages, UseFormula] +
        yane.get_base_params().params +
        [MatrixnetBinary] +
        yane.get_text_params('Pools (optional)', False).params +
        [
            yane.YaneLearnTaskBase.NumberOfIterations,
            NumberOfSplits,
            Threshold,
            yane.YaneLearnTaskBase.NumberOfCPU,
            CreateFeaturesResource,
            CreatePoolResource,
            LearnModel,
            LearnSignificaneModel,
            SignificanceNumberOfIterations,
            SignificanceThreshold,
            DisableFeatures,
            WithBorsches,
            yane.YaneLearnTaskBase.AdditionalMXOptions,
            FeaturesPool,
            FilterStep,
            FilterThreshold,
            FilterMXOptions
        ]
    )

    def __init__(self, task_id=0):
        yane.YaneTaskBase.__init__(self, task_id)
        self.ctx['kill_timeout'] = 6 * 60 * 60

    @property
    def footer(self):
        def interval_string(val, interval):
            return "%f .. %f" % (val - interval, val + interval)

        if not self.is_finished():
            return None
        else:
            footer_dict = {
                'markup_errors_in_test': '<b><a href="{}">markup_diff.xls</a></b>'.format(self.ctx.get('markup_errors_url', '')),
                'precision': self.ctx['precision'],
                'precision_interval': interval_string(self.ctx['precision'], self.ctx.get('precision_interval', 0.0)),
                'recall': self.ctx['recall'],
                'recall_interval': interval_string(self.ctx['recall'], self.ctx.get('recall_interval', 0.0)),
                'fmeasure': self.ctx['fmeasure'],
                'fmeasure_interval': interval_string(self.ctx['fmeasure'], self.ctx.get('fmeasure_interval', 0.0)),
            }
            if self.ctx.get('learn_significance_model'):
                footer_dict['significance_precision'] = self.ctx.get('significance_precision', 0.0)
                footer_dict['significance_recall'] = self.ctx.get('significance_recall', 0.0)
                footer_dict['significance_fmeasure'] = self.ctx.get('significance_fmeasure', 0.0)
            return footer_dict

    def __learn_model(self, matrixnet_res, pool_res, iter_num, task_name):
        params = {
            'kill_timeout': max(6 * 60 * 60, self.ctx['kill_timeout'] - 60 * 60),
            'matrixnet': self.ctx['matrixnet'],
            'pool': pool_res.id,
            'iters': iter_num,
            'min_ncpu': self.ctx['min_ncpu'],
            'matrixnet_options': self.ctx['matrixnet_options'],
            'notify_via': '',
            'notify_if_finished': '',
            'notify_if_failed': self.author,
            'data': self.ctx.get('data')
        }
        if self.ctx['filter_hypos'] or self.ctx['learn_significance_model']:
            params['tools'] = self.ctx['tools']
            params['svn_url'] = self.ctx['svn_url']
            params['extraction_languages'] = self.ctx.get('extraction_languages')
            params['formula'] = self.ctx['formula']
            params['disabled_features'] = self.ctx.get('disabled_features')
            params['with_borsches'] = self.ctx.get('with_borsches')
            if self.ctx['filter_hypos']:
                params['filter_hypos'] = True
                params['filter_threshold'] = self.ctx['filter_threshold']
                params['filter_matrixnet_options'] = self.ctx.get('filter_matrixnet_options')
            if self.ctx['learn_significance_model']:
                params['learn_significance_model'] = True
                params['significance_iters'] = self.ctx['significance_iters']
        subtask = self.create_subtask('YANE_LEARN_MODEL',
                                      task_name,
                                      input_parameters=params,
                                      arch=matrixnet_res.arch)
        return subtask

    def __run_objectsextractor(self):
        if 'mn_tasks' in self.ctx:  # проснулись после ожидания mn_tasks
            if (self.ctx.get('learn_pool_task')):  # copy learnt model to self:
                resource_id = apihelpers.get_task_resource_id(self.ctx['learn_pool_task'], resource_types.YANE_MODEL)
                mn_dir = make_folder('model')
                model_tgz_path = os.path.join(mn_dir, 'model.tgz')
                res_path = self.sync_resource(resource_id)
                copy_path(res_path, model_tgz_path)  # иначе нельзя создать ресурс, т.к. путь в другой задаче
                res = self._create_resource(
                    'model: ' + self.descr,
                    resource_path=model_tgz_path,
                    resource_type=resource_types.YANE_MODEL,
                )
                self.mark_resource_ready(res.id)
            return

        extractor_cmd = self.get_extractor_cmd()
        logging.debug("extractor_cmd: %s", extractor_cmd)

        texts_path = self.get_text_pool(self.ctx['dir_suffix'])
        markup_path = self.get_markup(self.ctx['dir_suffix'])

        mn_dir = make_folder('mn')
        features = os.path.join(mn_dir, 'features.txt')

        if self.is_resource_selected('features_pool'):
            pool = self.sync_resource(self.ctx['features_pool'])

            if pool.endswith('.tgz'):
                run_process(['tar', '-zxf', pool, '--strip-components=1', 'pool/learn.tsv'],
                             log_prefix='extract_pool')
                pool = 'learn.tsv'
        else:
            pool = os.path.join(mn_dir, 'pool.txt')
            if self.ctx['filter_hypos']:
                extractor_cmd.append('--print-fast-features')
            else:
                extractor_cmd.append('-F')
            logging.debug("extractor_cmd: %s", extractor_cmd)
            run_process(extractor_cmd,
                        log_prefix='objectsextractor',
                        wait=True,
                        stdin=open(texts_path, 'r'),
                        stdout=open(features, 'w'),
                        outputs_to_one_file=False)

            with self.current_action('Creating pool from features'):
                create_pool_cmd = [self.get_tool('pooltools'), '-m', markup_path, '-f', features, '-t', self.get_ids_trie(self.ctx['dir_suffix'])]
                run_process(
                    create_pool_cmd,
                    log_prefix='pooltools',
                    wait=True,
                    stdout=open(pool, 'w'),
                    outputs_to_one_file=False
                )

            if self.ctx.get('features_resource', False):
                run_process(['gzip', features], log_prefix='gzip')
                copy_path(features + '.gz', self.abs_path('features.txt.gz'))
                remove_path(features + '.gz')
                res = self.create_resource(
                    self.descr + '(features)',
                    resource_path='features.txt.gz',
                    resource_type=resource_types.OTHER_RESOURCE,
                    arch='any'
                )
                self.mark_resource_ready(res.id)
            else:
                remove_path(features)

        number_of_splits = self.ctx.get('splits', NUMBER_OF_SPLITS_DEFAULT)

        pool_prefix = 'filter_' if self.ctx['filter_hypos'] else ''
        with self.current_action('Splitting pool to %s number of splits' % number_of_splits):
            split_pool(pool, number_of_splits, mn_dir, pool_prefix)

        # Get arch of the matrixnet binary
        matrixnet_res = channel.sandbox.get_resource(self.ctx['matrixnet'])

        learn_pool_task = None
        if self.ctx.get('pool_resource', False):
            pool_dir = os.path.join(mn_dir, "pool")
            if not os.path.exists(pool_dir):
                os.mkdir(pool_dir)
                copy_path(pool, os.path.join(pool_dir, pool_prefix + "learn.tsv"))
                run_process(['tar', '-C', mn_dir, '-czf', "pool.tgz", "pool"], log_prefix='tar',
                            work_dir=self.abs_path())
            res = self.create_resource(
                self.descr + ' (pool)',
                resource_path='pool.tgz',
                resource_type=resource_types.YANE_POOL,
                arch='any'
            )
            self.mark_resource_ready(res.id)

            if self.ctx.get('learn_model', False):
                learn_pool_task = self.__learn_model(matrixnet_res, res, self.ctx['iters'], 'Learn model for pool').id
                self.ctx['learn_pool_task'] = learn_pool_task

        mn_tasks = []
        for i in xrange(number_of_splits):
            run_process(['tar', '-C', mn_dir, '-czf', 'split%s.tgz' % i, 'split%s' % i], log_prefix='tar',
                        work_dir=self.abs_path())
            res = self.create_resource(
                self.descr + '(split%s)' % i,
                resource_path='split%s.tgz' % i,
                resource_type=resource_types.YANE_POOL,
                arch='any'
            )
            self.mark_resource_ready(res.id)
            subtask = self.__learn_model(matrixnet_res, res, self.ctx['iters'], 'Learn model for split%s' % i)
            mn_tasks.append(subtask.id)

        self.ctx['mn_tasks'] = mn_tasks  # чтобы не запускать все повторно после wait subtasks

        all_subtasks = []
        if(learn_pool_task is not None):
            all_subtasks.append(learn_pool_task)
        all_subtasks = all_subtasks + mn_tasks

        self.wait_tasks(all_subtasks, tuple(self.Status.Group.FINISH), True)

    def __calc_quality(self, names_prefix, predict_threshold, markup_threshold):
        MARKUP_ERRORS_OUTPUT_FILE = 'markup.xls'

        mn_tasks = self.check_tasks('mn_tasks', 'Learn model')
        test_dir = make_folder('test')

        for task_id in mn_tasks:
            mn_path = self.sync_resource(apihelpers.get_task_resource_id(task_id, resource_types.YANE_MODEL))
            target = make_folder(os.path.join(test_dir, repr(task_id)))
            to_extract = ['model/' + names_prefix + 'test.tsv.test.matrixnet']
            if self.ctx['filter_hypos']:
                to_extract.append('model/' + names_prefix + 'filter_test.tsv')
            run_process(['tar', '-C', target, '-zxf', mn_path, '--strip-components=1'] + to_extract,
                        log_prefix='extract_mn')

        texts_path = self.get_text_pool(self.ctx['dir_suffix'])
        with self.current_action('Calculating quality'):
            precisions, recalls, fmeasures =\
                calc_splits_qualities(predict_threshold, test_dir, texts_path, MARKUP_ERRORS_OUTPUT_FILE, markup_threshold=markup_threshold, prefix=names_prefix)
            precision, recall, fmeasure, p_interval, r_interval, f_interval = quality(precisions, recalls, fmeasures)
        markup_errors_resource = self._create_resource('NER markup errors (in test set)', MARKUP_ERRORS_OUTPUT_FILE, resource_types.YANE_MARKUP_DIFF_XLS)
        markup_errors_resource.mark_ready()
        self.ctx['markup_errors_url'] = markup_errors_resource.proxy_url

        self.ctx[names_prefix + 'splits_precision'] = precisions
        self.ctx[names_prefix + 'splits_recall'] = recalls
        self.ctx[names_prefix + 'splits_fmeasure'] = fmeasures

        self.ctx[names_prefix + 'precision'] = precision
        self.ctx[names_prefix + 'precision_interval'] = p_interval
        self.ctx[names_prefix + 'recall'] = recall
        self.ctx[names_prefix + 'recall_interval'] = r_interval
        self.ctx[names_prefix + 'fmeasure'] = fmeasure
        self.ctx[names_prefix + 'fmeasure_interval'] = f_interval

    def __calc_quality_extraction(self):
        self.__calc_quality('', self.ctx['threshold'], 0.5)

    def __calc_quality_significance(self):
        self.__calc_quality('significance_', self.ctx['significance_threshold'], 0.5)
        self.__calc_quality('significance_ukr_', self.ctx['significance_threshold'], 0.5)

    def __run_profiling_binary(self, model_file_name, filter_model_file_name, force_trunk_data):
        extractor_cmd = self.get_extractor_cmd(force_trunk_data)
        extractor_cmd.append('-O')

        if model_file_name:
            extractor_cmd.extend(['-m', model_file_name])
            if self.ctx['filter_hypos'] and filter_model_file_name:
                extractor_cmd.extend(['--filter-model', filter_model_file_name])
                extractor_cmd.extend(['--filter-threshold', repr(self.ctx['filter_threshold'])])

        logging.debug("extractor_cmd: %s", extractor_cmd)

        texts_path = self.get_text_pool(self.ctx['dir_suffix'])
        profile_out = 'profile_out.txt'
        profile_err = tempfile.NamedTemporaryFile(delete=False).name

        run_process(extractor_cmd,
                    log_prefix='objectsextractor',
                    wait=True,
                    stdin=open(texts_path, 'r'),
                    stdout=open(profile_out, 'w'),
                    stderr=open(profile_err, 'w'),
                    outputs_to_one_file=False)

        # objectsextractor пишет profile в stderr
        profile_str = open(self.abs_path(profile_err)).read()
        logging.debug(profile_str)
        json_obj = json.load(open(self.abs_path(profile_err)))
        if json_obj.get('timers'):
            main_time = json_obj['timers'][0]['time']
            self.ctx['profile_title'] = main_time
        else:
            logging.debug("profile_out has no timers: %s", json_obj)

        return profile_str

    def __profile_extraction(self):
        if not self.ctx.get('learn_pool_task'):
            return

        with self.current_action('Profiling'):
            model_id = apihelpers.get_task_resource_id(self.ctx['learn_pool_task'], resource_types.YANE_MODEL)
            temp_folder = make_folder('temp')
            run_process(['tar', '-C', temp_folder, '-zxf', self.sync_resource(model_id), '--strip-components=1'], log_prefix='extract_pool')
            model_file_name = os.path.join(temp_folder, 'yane.info')
            filter_model_file_name = os.path.join(temp_folder, 'filter_yane.info')

            self.ctx['profile_results'] = self.__run_profiling_binary(model_file_name, filter_model_file_name, False)
            self.ctx['profile_trunk_results'] = self.__run_profiling_binary(None, None, True)

    def do_execute(self):
        if self.ctx.get('formula') == 'music' or self.ctx.get('formula') == 'yobject':
            self.ctx['extraction_languages'] = 'ru'

        self.build_matrixnet()
        self.__run_objectsextractor()
        self.__calc_quality_extraction()

        if self.ctx.get('learn_significance_model', False):
            self.__calc_quality_significance()

        self.__profile_extraction()


__Task__ = YaneTestTask
