# -*- coding: utf-8 -*-

import logging
import os
import math
import json
import signal

from sandbox import common
import sandbox.common.types.client as ctc

from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.paths import make_folder
from sandbox.sandboxsdk.paths import copy_path
from sandbox.sandboxsdk.paths import remove_path
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk.errors import SandboxTaskFailureError, SandboxSubprocessTimeoutError
from sandbox.projects.common.search.components import DefaultUpperSearchParams
from sandbox.projects import resource_types
from sandbox.projects import TestReportUnit as TRU
from sandbox.projects.common import apihelpers
import sandbox.projects.report.common as report_common
import sandbox.projects.sandbox


class ArcadiaUrl(TRU.ArcadiaUrl):
    pass


class Threshold(sp.SandboxIntegerParameter):
    """
    Минимально допустимое число строк в препарате лога для обстрела
    """
    name = 'threshold'
    description = 'Minimum permissible of a prepared log (0 - use children default):'
    default_value = 0


class LogsLimit(sp.SandboxIntegerParameter):
    name = 'logs_limit'
    description = 'Limit of a prepared log (0 - no limit)'
    default_value = 0


class ShootLog(sp.ResourceSelector):
    required = True
    name = 'prepared_log'  # store access_log_parsed in root dir
    description = 'ShootLogPrepare:'
    resource_type = resource_types.SHOOT_LOG_PREPARE

    @common.utils.classproperty
    def default_value(cls):
        return next(
            iter(channel.sandbox.server.last_resources(resource_types.SHOOT_LOG_PREPARE.name)),
            {'id': None}
        )['id']


class DataRuntime(sp.ResourceSelector):
    required = True
    name = 'data_runtime'
    description = 'DataRuntime:'
    resource_type = resource_types.REPORT_DATA_RUNTIME


class Number(sp.SandboxIntegerParameter):
    name = 'number'
    description = 'perform *number of each req'
    default_value = 1


class NClients(sp.SandboxIntegerParameter):
    name = 'n_clients'
    description = 'number of search shoot clients(0 - depend on cpu)'
    default_value = 5


class NClientsForFetchingStage(sp.SandboxIntegerParameter):
    name = 'n_clients_for_fetching'
    description = 'number of search shoot clients for fetching stage'
    default_value = 20


class ExtraParams(sp.SandboxStringParameter):
    name = 'searchpl_param'
    description = 'Additional parameters for search.pl:'
    default_value = ""


class ArchParam(sp.SandboxStringParameter):
    name = 'arch_param'
    description = 'Target machine arch (e5620/e5645 etc)'
    default_value = "e5645"


class AdditionalFlags(sp.SandboxStringParameter):
    name = 'additional_flags'
    description = 'Addition flags, serialized exp_params. e.g. &srcparams=WEB=snip=exps=add_extended=1'
    default_value = ""


class Selector(TRU.Selector):
    choices = [('svn', 'svn'), ('package', 'package')]
    sub_fields = {'svn': [ArcadiaUrl.name], 'package': [DefaultUpperSearchParams.ReportCoreParameter.name]}
    default_value = choices[0][1]


class TemplatesPath(sp.SandboxStringParameter):
    name = 'templates_path'
    description = 'Path to templates:'
    default_value = ''


class CompareCtxWithPrev(sp.ResourceSelector):
    name = 'cmp_ctx_prev_shoot_result'  # store access_log_parsed in root dir
    description = 'PrevResToCompareCtxWith:'
    resource_type = resource_types.TEST_REPORT_PERFORMANCE


class SmallProfile(sp.SandboxBoolParameter):
    name = 'small_profile'
    description = 'use stmts=0 for decrease size of profile'
    default_value = False


class Percentile(sp.SandboxIntegerParameter):
    name = 'percentile'
    description = 'Calculate percentile'
    default_value = 0


class Target95Percentile(sp.SandboxFloatParameter):
    name = 'target_95percentile'
    description = 'Fail if 95 percentile exceeds target (use 0 to disable that check).'
    default_value = 0


class MaxDiffFraction(sp.SandboxFloatParameter):
    name = 'max_diff_fraction'
    description = (
        'Maximum allowed difference between previous performance test '
        'and current one (use 0 to disable that check).'
    )
    default_value = 0


class LogLabel(sp.SandboxStringParameter):
    name = 'log_label'
    description = 'Label to use from profile-log'
    default_value = 'report_time'


class UseProfile(sp.SandboxBoolParameter):
    name = 'use_profile'
    description = 'use NYTProf for profiling'
    default_value = False
    sub_fields = {'true': [SmallProfile.name, Percentile.name]}


class UseTeplatesForFetchingStage(sp.SandboxBoolParameter):
    name = 'use_teplates_for_fetching_stage'
    description = 'Use templates on a fetching stage (--perl)'
    default_value = True


class CreateResultResource(sp.SandboxBoolParameter):
    name = 'create_result_resource'
    description = 'Create the resource with shoots results'
    default_value = True


class CalculateAVG(sp.SandboxBoolParameter):
    name = 'calculate_avg'
    description = 'Calculate average'
    default_value = True


class ContainerLxc(TRU.ContainerLxc):
    @property
    def default_value(self):
        res = apihelpers.get_last_resource_with_attribute(
            sandbox.projects.sandbox.LXC_CONTAINER,
            attribute_name='report',
            attribute_value='2',
        )
        return res.id if res else None


class CustomFlagsJSON(sp.SandboxUrlParameter):
    name = 'flags_json'
    description = 'Copy flags.json from uri, e.g. https://ab.yandex-team.ru/deploying/flags.json/2/content'
    default_value = ""


class ComponentName(sp.SandboxStringParameter):
    """
    Release Machine component name
    """
    name = "component_name"
    description = "Release Machine component name"
    default_value = 'report'


class TestReportPerformance(TRU.TestReportUnit):
    """
        Обстрел репорта продакшн запросами.

        **Описание**

        Тестирование производительности репорта.

        Производится через поднятие **apache+data+templates+report**, создание кеша запросов и обстрела
        локально поднятого репорта этими запросами.
        По умолчанию используются ресурсы из последних релизов.

        Тестирование происходит следующим образом:

            1. Разворачивается report + templates + apache + data + препарат лога запросов
            2. Первый проход поиска по запросам в 20 потоков. Он медленный, тк реально ходим в источники.
                Сохраняет данные в shoot_results
            3. Чистим логи от прелдыдущего прохода
            4. Ищем ещё раз по кешу от первого прохода. Данные и логи позапросно в shoot_results
            5. По profile-логам считаем 95 и 50 и прочие перцентили report_time, кладём в контект.

        **Необходимые ресурсы**

            * REPORT_TEMPLATES_PACKAGE - пакет шаблонов репорта
            * APACHE_BUNDLE - пакет apache
            * DATA_RUNTIME - runtime данные репорта
            * SHOOT_LOG_PREPARE - препарат логов для обстрела
            * (опционально) можно указать TEST_REPORT_PERFORMANCE от предыдущего обстрела для сравнения контекстов.

        **Создаваемые ресурсы**

            * TEST_REPORT_PERFORMANCE - tar.gz архив с результатами обстрелов (логи, requests.store, head, body) -
                разложенные позапросно

        **Параметры**

            * **selector** - брать репорт из svn/пакета
            * **n_clients**  - число клиентов search.pl для второго прохода обстрела
            * **searchpl_param** - параметры для проброса в search.pl (например, --perl - не будет рендерить шаблоны)
            * **threshold** - минимально допустимое число строк в препарате лога для обстрела
            * **logs_limit** - количество строк, которые будут браться из препарата лога для обстрела
    """

    type = 'TEST_REPORT_PERFORMANCE'

    DefaultUpperSearchParams.ReportTemplatesParameter.name = 'report_templates'

    input_parameters = [
        Selector,
        ArcadiaUrl,
        DefaultUpperSearchParams.ReportCoreParameter,
        DefaultUpperSearchParams.ReportTemplatesParameter,
        report_common.ApacheBundleParameter,
        DataRuntime,
        ShootLog,
        NClients,
        NClientsForFetchingStage,
        AdditionalFlags,
        ExtraParams,
        ArchParam,
        LogsLimit,
        Threshold,
        CompareCtxWithPrev,
        Number,
        TemplatesPath,
        TRU.RtccBundle,
        UseProfile,
        SmallProfile,
        Percentile,
        Target95Percentile,
        LogLabel,
        MaxDiffFraction,
        CalculateAVG,
        CreateResultResource,
        UseTeplatesForFetchingStage,
        ContainerLxc,
        CustomFlagsJSON,
        ComponentName,
    ]

    execution_space = 20480
    client_tags = ctc.Tag.LINUX_PRECISE

    res_folder = "shoot_results"
    res_folder_prev = "shoot_results_prev"
    report_path = 'report'
    apache_bundle_path = 'apache_bundle'
    resource_type = resource_types.TEST_REPORT_PERFORMANCE

    def __init__(self, task_id=0):
        TRU.TestReportUnit.__init__(self, task_id)
        self.working_dir = self.abs_path()
        self.report_fullpath = os.path.join(self.working_dir, self.report_path)
        self.access_log_path = None

    def avg_time(self, timefield):
        json_data = []

        metafield = ','.join([
            '.meta->{len_tmpl_json_2}+.meta->{len_tmpl_json_1}'
            if (f == 'len_tmpl_json_') else '.meta->{%s}' % f for f, p in timefield
        ])
        metafield = "(%s)" % metafield
        logging.info(metafield)

        cmd = """bash -c 'COUNTER=%s
        for file in `find %s -name profile_log`; do
            cat $file | y-local-env scripts/dev/parse/parse_profile.pl |
            y-local-env scripts/dev/parse/json_map.pl "%s" >$file.P;
            for (( i=1; i <= COUNTER; i++ )); do
                awk \"{if (length(\$$i)>0 && \$$i != 0) print \$$i}\" $file.P | sort -T . -nr >$file.SRT.$i;
                if [ -s $file.SRT.$i ]; then
                    NSIZE=`wc -l $file.SRT.$i | cut -f1 -d " "`;
                    SKIP=$(( NSIZE/10 ));
                    head -n$((NSIZE-SKIP)) $file.SRT.$i | tail -n$((NSIZE-2*SKIP)) >$file.SRT_TRIM.$i;
                    echo $file.SRT_TRIM.$i;
                    cat $file.SRT_TRIM.$i | y-local-env scripts/dev/perf/avg.pl 0 >$file.AVG.$i;
                    if [ -s $file.AVG.$i ]; then
                        cat $file.AVG.$i >> %s/times.$i;
                    fi
                fi
            done;
        done;'""" % (
            len(timefield), os.path.join(self.working_dir, self.res_folder),
            metafield, os.path.join(self.working_dir, self.res_folder)
        )
        run_process(
            [cmd],
            work_dir=self.report_path,
            timeout=1200, shell=True, check=True, log_prefix='accumulate',
            outputs_to_one_file=True,
        )

        # файлы times.i можно не сортировать, потому что quant.pl сортирует
        run_process([
            """bash -c 'COUNTER=%s
             ARRAY=(%s)
             for (( i=1; i <= COUNTER; i++ )); do
                 if [ -s %s/times.$i ]; then
                     cat %s/times.$i | y-local-env scripts/dev/perf/quant.pl 0 10 |\
                     y-local-env perl -MJSON -e '"'"'$/ = undef; my $json=JSON->new; $json->canonical([1]); print JSON->new->canonical([1])->encode(+{ split /\s+/, <> })'"'"' > ${ARRAY[$i-1]};
                 fi
             done'"""
            % (len(timefield), ' '.join([p for f, p in timefield]), os.path.join(self.working_dir, self.res_folder), os.path.join(self.working_dir, self.res_folder))],
            work_dir=self.report_path, timeout=1200, shell=True, check=True, log_prefix='sorted_json', outputs_to_one_file=False)

        rv = []
        for f, p in timefield:
            if not os.path.exists(p) or not os.path.getsize(p):
                raise SandboxTaskFailureError('Shoot output %s is empty.' % p)

            logging.info("json shoot res file=%s" % p)
            f = open(p, 'r')
            json_data = json.loads(f.read())
            f.close()
            rv.append(json_data)

        return rv

    def get_logs_cmd(self):
        logs_limit = self.ctx[LogsLimit.name]
        return 'head -n %d' % (logs_limit) if logs_limit > 0 else 'cat'

    def on_execute(self):
        self.run_shooting()

        if self.ctx[CalculateAVG.name]:
            self.calculate_avg()

        if self.ctx[CreateResultResource.name]:
            self.make_resource_with_results()

        self.create_profile_log()
        self.create_error_log()
        self.calculate_memory_usage()

        compare_ctx_with_prev_id = self.ctx[CompareCtxWithPrev.name]
        if compare_ctx_with_prev_id:
            self.compare_with_prev_id(compare_ctx_with_prev_id)

        if self.ctx[CreateResultResource.name]:
            self.remove_results()

        target_95_percentile = Target95Percentile.default_value
        if Target95Percentile.name in self.ctx:
            target_95_percentile = self.ctx[Target95Percentile.name]
        if target_95_percentile > 0:
            current = self.get_95_percentile()
            if current > target_95_percentile:
                raise SandboxTaskFailureError('95 percentile = %f exceeds limit = %f' % (current, target_95_percentile))

        max_diff_fraction = MaxDiffFraction.default_value
        if MaxDiffFraction.name in self.ctx:
            max_diff_fraction = self.ctx[MaxDiffFraction.name]
        if max_diff_fraction != 0:
            self.check_diff_with_previous(max_diff_fraction)

    def get_95_percentile(self):
        key = '95'
        if key not in self.ctx:
            self.calculate_avg()
        if key not in self.ctx:
            raise SandboxTaskFailureError('could not obtain 95 percentile info')
        return self.ctx[key]

    def check_diff_with_previous(self, max_diff_fraction):
        previous_tasks = channel.sandbox.list_tasks(
            task_type=TestReportPerformance.type, limit=1, hidden=True, status='FINISHED', descr_mask='ws-report-'
        )
        if not previous_tasks:
            raise SandboxTaskFailureError('could not obtain 95 percentile info from previous task')
        previous_task = previous_tasks[0]

        current_value = self.get_95_percentile()
        if '95' not in previous_task.ctx:
            raise SandboxTaskFailureError('could not obtain 95 percentile info from previous task')
        previous_value = previous_task.ctx['95']

        diff = current_value - previous_value
        if diff > max_diff_fraction * previous_value:
            raise SandboxTaskFailureError(
                '95 percentile differs from previous: previous = %f, current = %f, diff = %f' % (
                    previous_value, current_value, diff
                )
            )

    def fetch_report_data(self):
        def on_timeout(process):
            process.send_signal(signal.SIGABRT)
            process.communicate()
            logging.info('timeout')

        search_fetch_pattern = '%s %s | %s/scripts/dev/search.pl --fetch --clients=%s --Flag \'%s\' %s'

        if self.ctx[UseTeplatesForFetchingStage.name]:
            search_fetch_cmd = search_fetch_pattern
        else:
            search_fetch_cmd = search_fetch_pattern + ' --perl'

        try:
            run_process(
                [
                    search_fetch_cmd % (
                        self.get_logs_cmd(),
                        self.access_log_path,
                        self.report_fullpath,
                        self.ctx[NClientsForFetchingStage.name],
                        self.ctx[AdditionalFlags.name],
                        self.ctx[ExtraParams.name]
                    )
                ],
                work_dir=self.res_folder,
                shell=True,
                check=True,
                timeout=900,
                log_prefix='fetch_search',
                outputs_to_one_file=False,
                on_timeout=on_timeout,
            )
        except SandboxSubprocessTimeoutError:
            logging.info("fetch timeouted")

        self.ctx['_total'] = int(self.run_and_read('find . -maxdepth 1 -type d | wc -l', work_dir=self.res_folder))
        # для fetch стадии
        # не удалось создать запрос к реквестеру
        self.ctx['_err'] = int(self.run_and_read(
            "find . -name error_log ! -size 0b -exec grep -m1 -E '^Requester return \S+ for url: ' {} \; | wc -l",
            work_dir=self.res_folder)
        )
        # реквестер ответил кодом не 200
        self.ctx['_err'] += int(self.run_and_read(
            "find . -name error_log ! -size 0b -exec grep -m1 -E ' failed: bad backend response$' {} \; | wc -l",
            work_dir=self.res_folder)
        )
        run_process(['find . -name logs | xargs rm -rf'],
                    work_dir=self.res_folder, timeout=600, shell=True, check=True, log_prefix='rm_fetch_logs',
                    outputs_to_one_file=False
                    )

    def templates_path(self):
        return self.ctx.get('templates_path') or 'report-templates'

    def sync_templates(self):
        templates_resource_id = self.ctx[DefaultUpperSearchParams.ReportTemplatesParameter.name]

        self.expand_resource(
            res_id=templates_resource_id,
            dest=self.templates_path(),
        )

    def sync_access_log(self):
        shoot_log_resource_id = self.ctx[ShootLog.name]
        res = channel.sandbox.get_resource(shoot_log_resource_id)
        if not res:
            raise SandboxTaskFailureError(
                'Cannot execute task. Can\'t find shoot_log aka access_log_prepared '
                'resource by id %s.' % shoot_log_resource_id)
        path = self.sync_resource(res.id)
        self.access_log_path = path
        if os.path.basename(path) != 'access_log_parsed':
            os.symlink(path, 'access_log_parsed')

        logs_count = run_process('cat %s | wc -l' % path, shell=True, outs_to_pipe=True).communicate()
        logs_count = int(logs_count[0])
        if logs_count < self.ctx['threshold']:
            raise SandboxTaskFailureError(
                'Not enough logs for profiling: %s instead of %s or more as expected!' % (
                    logs_count, self.ctx['threshold']
                ))

        self.ctx['logs_count'] = logs_count

    def sync_apache_bundle(self):
        apache_bundle_resource_id = self.ctx[report_common.ApacheBundleParameter.name]
        self.get_apache(apache_bundle_resource_id, self.apache_bundle_path)

    def sync_data_runtime(self):
        data_runtime_resource_id = self.ctx[DataRuntime.name]
        self.get_data_runtime(data_runtime_resource_id, 'data.runtime')

    def sync_report(self):
        self.get_report(self, self.report_path)

    def sync_upper_config(self):
        self.get_upper_config(self.ctx[TRU.RtccBundle.name])

    def prepare_env(self):
        self.sync_access_log()
        self.sync_templates()
        self.sync_apache_bundle()
        self.sync_data_runtime()
        self.sync_report()
        self.sync_upper_config()

        # подменить файл flags.json
        if self.ctx.get(CustomFlagsJSON.name, "") != "":
            flags_beta_path = os.path.join(self.report_path, "data/flags/experiments/flags.json")
            self.download_file(flags_beta_path, self.ctx[CustomFlagsJSON.name])
            copy_path(flags_beta_path, 'data.runtime/util/experiments/flags.json')

        self.setup_env(self.report_path, self.apache_bundle_path)
        logging.info(os.environ)

        self.ctx['_err'] = 0

    def run_shooting(self):
        self.prepare_env()

        logging.info("self.ctx=%s" % self.ctx)

        self.fetch_report_data()

        number = self.ctx[Number.name]

        nclients = self.ctx[NClients.name]
        if not nclients:
            nclients = (self.client_info['ncpu'] / 2) - 2
            if nclients < 5:
                nclients = 5

        def on_timeout(process):
            process.send_signal(signal.SIGABRT)
            process.communicate()
            logging.info('timeout')

        try:
            timeout = 1900
            profile = ''
            if self.ctx[UseProfile.name]:
                timeout = 2 * timeout
                profile = '-d:NYTProf'

            run_process([
                '%s %s | y-local-env perl %s %s/scripts/dev/search.pl --clients=%d --Flag \'%s\' --number=%d %s' % (
                    self.get_logs_cmd(),
                    self.access_log_path,
                    profile,
                    self.report_fullpath,
                    nclients,
                    self.ctx[AdditionalFlags.name],
                    number, self.ctx[ExtraParams.name]
                )],
                work_dir=self.res_folder,
                shell=True,
                check=True,
                timeout=timeout,
                log_prefix='shoot_cached_search',
                outputs_to_one_file=False,
                on_timeout=on_timeout,
            )
        except SandboxSubprocessTimeoutError:
            logging.info("shoot on cache timeouted")

        # для обстрела
        self.ctx['_err'] += int(self.run_and_read(
            "find . -name error_log ! -size 0b -exec grep -m1 'No response for http://' {} \; | wc -l",
            work_dir=self.res_folder)
        )

        # объединяем статистику
        if self.ctx[UseProfile.name]:
            cmd = "y-local-env %s -v"
            if self.ctx[Percentile.name]:
                cmd += " -p " + str(self.ctx[Percentile.name])

            cmd += " '%s' '%s'"
            run_process(
                [cmd % (
                    os.path.join(self.abs_path(), self.report_path, 'scripts/dev/test/nytprofmerge.pl'),
                    os.path.join(self.abs_path(), self.res_folder, 'nytprof.out.*'),
                    os.path.join(self.abs_path(), self.res_folder, '*/nytprof.out.*')
                )],
                work_dir=self.nytprof_dir,
                timeout=9000,
                shell=True,
                check=True,
                log_prefix='nytprofmerge',
                outputs_to_one_file=False,
            )

            # удалить файлы nytprof.out.*
            run_process(['rm ./nytprof.out.* ./*/nytprof.out.*'],
                        work_dir=self.res_folder, timeout=600, shell=True, check=True, log_prefix='nytprofrm')
            # html
            run_process([
                'y-local-env %s -d -f %s -o nytprof' % (
                    os.path.join(self.abs_path(), self.report_path, 'scripts/dev/test/nytprofhtml.pl'),
                    'nytprof-merged.out'
                )],
                work_dir=self.nytprof_dir,
                timeout=18000,
                shell=True, check=True, log_prefix='nytprofhtml', outputs_to_one_file=False
            )
            self.ctx['nytprof_ready'] = 1

    def calculate_avg(self):
        shoot_res = os.path.join(self.working_dir, 'shoot_res.json')
        shoot_res_ = os.path.join(self.working_dir, 'shoot_res_.json')
        len_tmpl_json = os.path.join(self.working_dir, 'len_tmpl_json_.json')

        logging.info("START AVG")
        log_label = LogLabel.default_value
        if LogLabel.name in self.ctx:
            log_label = self.ctx[LogLabel.name]
        (json_data, json_data_, tmpl_data) = self.avg_time(
            [
                [log_label, shoot_res],
                ['report_time_', shoot_res_],
                ['len_tmpl_json_', len_tmpl_json]
            ]
        )
        logging.info("END AVG")

        copy_path(shoot_res, os.path.join(self.res_folder, 'shoot_res.json'))
        copy_path(shoot_res_, os.path.join(self.res_folder, 'shoot_res_.json'))
        copy_path(len_tmpl_json, os.path.join(self.res_folder, 'len_tmpl_json_.json'))

        if '95' in json_data:
            logging.info("json res to chart_data=%.3f" % float(json_data['95']))
            self.ctx['95'] = float(json_data['95'])
            self.ctx['chart_data'] = json_data
            self.ctx['chart_data_'] = json_data_
            self.ctx['chart_data_tmpl'] = tmpl_data

            sorted_name = 'times.1'
            self.ctx['sorted_times_count'] = int(run_process('wc -l %s | cut -f1 -d" "' % sorted_name, work_dir=self.res_folder, shell=True, outs_to_pipe=True).communicate()[0])
            self.ctx['sorted_times/total'] = float(float(self.ctx['sorted_times_count'])/self.ctx['_total'])

    def create_profile_log(self):
        run_process('cat */logs/profile_log > ../profile_log', work_dir=self.res_folder, shell=True)

        self.ctx['profile_log_files'] = int(run_process('find . -name profile_log -type f ! -size 0 | wc -l', work_dir=self.res_folder, shell=True, outs_to_pipe=True).communicate()[0])

        profile_log_resource = self.create_resource(
            description='profile_log for %s' % self.id,
            resource_path='profile_log',
            resource_type=resource_types.PROFILE_LOG
        )
        self.mark_resource_ready(profile_log_resource)

    def create_error_log(self):
        run_process('cat */logs/error_log > ../error_log', work_dir=self.res_folder, shell=True, check=False)
        self.ctx['errlog_total_lines'] = int(
            run_process(
                'cat ../error_log | grep -v "^ " | grep -v "^REQID:" | grep -Ev "^(Could not parse \'L\': KEY_NOT_FOUND|Bad value of L:)" | wc -l',
                work_dir=self.res_folder, shell=True, outs_to_pipe=True
            ).communicate()[0]
        )
        self.ctx['errlog_total_files'] = int(run_process('find . -name error_log | wc -l', work_dir=self.res_folder, shell=True, outs_to_pipe=True).communicate()[0])
        self.ctx['errlog_per_req'] = float(float(self.ctx['errlog_total_lines'])/self.ctx['errlog_total_files'])

        self.ctx['error_log_files'] = int(run_process('find . -name error_log  -type f ! -size 0 | wc -l', work_dir=self.res_folder, shell=True, outs_to_pipe=True).communicate()[0])

        if self.ctx['number']:
            density = self.ctx['errlog_density'] = float(float(self.ctx['errlog_per_req'])/self.ctx['number'])
            self.ctx['errlog_density_norm'] = float(math.exp(density if density < 1 else 1))
            if self.ctx.get('chart_data'):
                for k in ['errlog_density', 'errlog_density_norm']:
                    self.ctx['chart_data'][k] = self.ctx[k]

        error_log_resource = self.create_resource(
            description='error_log for %s' % self.id,
            resource_path='error_log',
            resource_type=resource_types.ERROR_LOG
        )
        self.mark_resource_ready(error_log_resource)

    def calculate_memory_usage(self):
        prog = "cat profile_log | y-local-env report/scripts/dev/parse/parse_profile.pl "\
               + "| y-local-env perl -MJSON::XS -lne 'BEGIN { our %A; our @B } my @d = @{decode_json($_)->{meta}}{qw/pid ru_maxrss_abs ru_maxrss/};"\
               + "if (exists $A{$d[0]}) { push @B, $d[2] } $A{$d[0]}=$d[1];"\
               + "END { my @C = sort { int($a) <=> int($b) } @B; my $cnt = scalar(@C); my $data={}; $data->{$_} = $C[int(($cnt/100)*$_)-1] for (50..100);"\
               + "print JSON::XS->new->encode($data)};'"
        (stdoutdata, stderrdata) = run_process(prog, shell=True, outs_to_pipe=True).communicate()
        if stderrdata:
            logging.error(stderrdata)
        self.ctx['memory_usage'] = json.loads(stdoutdata)

    def compare_with_prev_id(self, id):
        shoot_res_tarred = self.sync_resource(id)
        run_process('mkdir %s' % (self.res_folder_prev), shell=True)
        run_process(['tar -C %s --strip-components=1 -xzf %s' % (self.res_folder_prev, shoot_res_tarred)], shell=True, log_prefix='untar')
        # find 2.83/ 1.trunk -name requests.store  | cut -d '/' -f2 | sort | uniq -c | grep '     2' | cut -d ' ' -f8
        run_process(['find %s %s -name requests.store | cut -d "/" -f2 | sort | uniq -c | grep "     2" | cut -d " " -f8 >same_ids'
                     % (self.res_folder, self.res_folder_prev)], shell=True, log_prefix='find')
        self.ctx['n_same_ids'] = int(run_process('wc -l same_ids | cut -f1 -d" "', shell=True, outs_to_pipe=True).communicate()[0])
        # /hol/arkanavt//report/scripts/dev/search/diff.pl 'hamster\.yandex\.ru:9080.client_ctx.YABS' \
        # shoot_results/1418411264027492-369313717878878619313053-sas1-5454/requests.store \
        # shoot_results/1418411263891470-338509156320186503512837-sas1-5454/requests.store

        run_process(['for reqid in `cat same_ids`; do echo $reqid; %s/scripts/dev/search/diff.pl "hamster\.yandex\.ru:9080.client_ctx.YABS"\
 \'["test-tag"]\' %s/$reqid/requests.store %s/$reqid/requests.store >>yabs_diff; done;' % (self.report_fullpath, self.res_folder_prev, self.res_folder)],
                    shell=True, check=False, log_prefix='diff_yabs', outputs_to_one_file=False)
        self.ctx['yabs_diff'] = int(run_process('wc -l yabs_diff | cut -f1 -d" "', shell=True, outs_to_pipe=True).communicate()[0])
        if (self.ctx['yabs_diff']):
            run_process('echo "<html><pre>" >yabs_diff.html; cat yabs_diff >>yabs_diff.html; echo "</html>" >>yabs_diff.html', shell=True)
            yabs_diff_resource = self.create_resource(
                description='yabs_diff for %s' % self.id,
                resource_path='yabs_diff',
                resource_type=resource_types.YABS_DIFF)
            self.mark_resource_ready(yabs_diff_resource)
            self.ctx['yabs_diff_resource_id'] = yabs_diff_resource.id

    def remove_results(self):
        remove_path(self.res_folder)

    def setup_env(self, report_path, apache_bundle_path):
        make_folder(self.res_folder, delete_content=True)
        make_folder("conf/report", delete_content=True)
        env = {
            "UPPER_DIR": os.path.join(self.working_dir, apache_bundle_path),
            "REPORT_DIR": os.path.join(self.working_dir, report_path),
            "PREPARED_LOG_DIR": os.path.abspath(self.working_dir),
            "SHOOT_DIR": os.path.join(self.working_dir, self.res_folder),
        }
        if self.ctx[UseProfile.name]:
            self.nytprof_dir = self.log_path("nytprof")
            make_folder(self.nytprof_dir, delete_content=True)
            env["NYTPROF"] = "start=no:addpid=1:blocks=1:sigexit=int,hup,pipe,bus,segv,term"
            if self.ctx[SmallProfile.name]:
                env["NYTPROF"] += ":stmts=0"

        for key, value in env.items():
            if os.environ.get(key):
                os.environ[key] = "%s:%s" % (value, os.environ[key])
            else:
                os.environ[key] = value

    def make_resource_with_results(self):
        tar_name = "%s.tar.gz" % self.res_folder
        remove_path(tar_name)
        # проблем со skynet.copier-ом уже нет, поэтому можно не сжимать.
        # сжимаем директорию чтобы занимать меньше места в сандбоксе. ресурс по факту не мспользуется,
        # нужен только для расследования проблем
        run_process([
            'tar -czf %s %s' % (tar_name, self.res_folder)
        ], shell=True, check=False, log_prefix='run_process_log')
        if not os.path.exists(tar_name) or not os.path.getsize(tar_name):
            raise SandboxTaskFailureError('Archive %s is empty.' % tar_name)

        if not self.ctx.get('bfire_report_resource_id'):
            # создаем ресурс
            unit_resource = self.create_resource(
                description=self.descr,
                resource_path=tar_name,
                resource_type=self.resource_type,
                arch=None,
                attributes={'arch': self.client_info['arch']}
            )
            logging.info('Create resource %s id: %s' % (self.resource_type, unit_resource.id))
            self.ctx['bfire_report_resource_id'] = unit_resource.id

    @property
    def footer(self):
        """
        Ссылка на отчет NYTProf
        """
        if self.ctx[UseProfile.name]:
            if self.ctx.get('nytprof_ready'):
                log_view = self.get_common_log_view()
                return (
                    '<p><a href="%s">nytprof</a>' % os.path.join(
                        os.path.dirname(log_view["url"]), 'nytprof', 'nytprof', 'index.html'
                    )
                )
            else:
                return '<p>Профиль не готов</p>'


__Task__ = TestReportPerformance
