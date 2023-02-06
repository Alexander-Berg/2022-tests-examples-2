# -*- coding: utf-8 -*-

import os
import logging
import signal
from datetime import datetime
import time
import json
import traceback
import stat
import urllib2

from sandbox.common.types.client import Tag

import sandbox.sdk2 as sdk2

from sandbox.projects import resource_types
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.process import run_process, kill_process
from sandbox.sandboxsdk.paths import make_folder, copy_path, remove_path, chmod
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.errors import SandboxTaskFailureError, SandboxSvnError, SandboxTaskUnknownError
from sandbox.sandboxsdk.environments import SvnEnvironment
from sandbox.projects.common.environments import ValgrindEnvironment, PipEnvironment
from sandbox.sandboxsdk.svn import ArcadiaTestData, Arcadia
from sandbox.sandboxsdk.network import is_port_free

from sandbox.projects.common import apihelpers
from sandbox.projects.TestRTYServerUnit.process_watcher import processesProfiler
from sandbox.projects.TestRTYServerUnit.rty_utils import prepare_gperftools, get_gperftolls_environ
from sandbox.projects.TestRTYServerUnit.rty_utils import do_tar
from sandbox.projects.TestRTYServerUnit.rty_utils import extract_rss, MemLogStorage
from sandbox.projects.TestRTYServerTask.resources import ResourceManager
from sandbox.projects.TestRTYServerTask.parser import Parser
from sandbox.projects.TestRTYServerTask.plots import Plotter


class TestMainParameters(sdk2.Parameters):
    rtyserver_test_resource_id = sdk2.parameters.Resource(
        'RTYServer tests binary', required=True, resource_type=[resource_types.RTYSERVER_TEST])
    rtyserver_test_parameter = sdk2.parameters.String('RTYServer tests')
    rtyserver_test_parameter_type = sdk2.parameters.String('RTYServer test letter: -t or -x', default='-t')
    rtyserver_other_parameter = sdk2.parameters.String('RTYServer tests other parameters')
    tester_timeout = sdk2.parameters.Integer('Timeout for tester', default=1200)


class TestClusterParameters(sdk2.Parameters):
    rtyserver_configs_resource_id = sdk2.parameters.Resource(
        'Configs for tester', required=False, resource_type=[resource_types.RTYSERVER_CONFIGS])
    rtyserver_resource_id = sdk2.parameters.Resource(
        'Rtyserver binary', required=False, resource_type=[resource_types.RTYSERVER])
    searchproxy_resource_id = sdk2.parameters.Resource(
        'Searchproxy binary', required=False, resource_type=[resource_types.RTYSERVER_SEARCHPROXY])
    indexerproxy_resource_id = sdk2.parameters.Resource(
        'Indexerproxy binary', required=False, resource_type=[resource_types.RTYSERVER_INDEXER_PROXY])
    deploy_manager_resource_id = sdk2.parameters.Resource(
        'Deploy manager binary', required=False, resource_type=[resource_types.RTYSERVER_UTILS_DEPLOY_MANAGER])
    monolith_resource_id = sdk2.parameters.Resource(
        'Distributor monolith binary', required=False, resource_type=[resource_types.DISTRIBUTOR])
    rtyemulator_resource_id = sdk2.parameters.Resource(
        'Rtyserver emulator binary', required=False, resource_type=[resource_types.RTYSERVER_UTILS_RTYSERVER_EMULATOR])


class TestDataParameters(sdk2.Parameters):
    rtyserver_test_data_path = sdk2.parameters.String('Path to svn with test data')
    rtyserver_test_data_dict_path = sdk2.parameters.String('Path to svn with dictionary data for parameter -o')
    external_test_data = sdk2.parameters.String('Attribute to search test_data')


class SpecialParameters(sdk2.Parameters):
    use_valgrind = sdk2.parameters.Bool('Use valgrind', default=False)
    use_perftools = sdk2.parameters.Bool('Use gperftools', default=False)
    with use_perftools.value[True]:
        gprof_frequency = sdk2.parameters.Integer('Gperftools frequency', default=100)
    use_distributor = sdk2.parameters.Bool('Use distributor', default=False)
    save_responses = sdk2.parameters.Bool('save responses(oxygen)', default=False)
    queries_resource_id = sdk2.parameters.Resource(
        'Search requests', required=False, resource_type=[resource_types.PLAIN_TEXT_QUERIES])
    cluster_cfg_text = sdk2.parameters.String('cluster.cfg text', multiline=True)
    save_dolb = sdk2.parameters.Bool('Save smth to context', default=False)
    with save_dolb.value[True]:
        parser_rules = sdk2.parameters.String('rules for parsing files', multiline=True)
    system_stat_attr = sdk2.parameters.String('Sys stat scripts attr')
    save_root = sdk2.parameters.Bool('Save root folder', default=False)
    save_index = sdk2.parameters.Bool('Save index dir', default=False)
    use_multislot = sdk2.parameters.Bool('multislot', default=False)


class TestRTYServerUnit(SandboxTask):
    type = 'TEST_RTYSERVER_UNIT'
    client_tags = Tag.LINUX_PRECISE
    input_parameters = list(TestMainParameters) + list(TestClusterParameters) +\
                       list(TestDataParameters) + list(SpecialParameters)

    execution_space = 30000

    UNITTEST_OUTLOG = ''
    UNITTEST_ERRLOG = ''
    t_process_pids = []
    t_processes = []
    cluster_test = False
    oxy_data_path = ''
    mem_usage_test_data_path = ''
    test_data_path = ''
    configs_path = ''
    prof_tools_path = ''
    binaries_used = {}

    external_data = {}

    responses_path = ''
    queries_path = ''
    index_dir_path = []

    @property
    def environment(self):
        return (
            (SvnEnvironment(),) +
            (ValgrindEnvironment(),) if self.ctx.get('use_valgrind') else () +
            (PipEnvironment('matplotlib', '1.4', use_wheel=True),) if self.ctx.get('system_stat_attr') else ()
        )

    def initCtx(self):
        self.ctx['start_rty_tests_time_stamp'] = ''
        self.ctx['finish_rty_tests_time_stamp'] = ''
        self.ctx['rty_tests_work_time'] = ''
        self.ctx['rty_tests_work_time_seconds'] = ''
        self.ctx['task_result_type'] = ''

        self.ctx['test_results'] = []
        self.ctx['test_result'] = ''

    def on_enqueue(self):
        SandboxTask.on_enqueue(self)
        if 'MemoryUsage' in self.ctx.get('rtyserver_test_parameter'):
            self.execution_space = 60000
        elif 'Oxy' in self.ctx.get('rtyserver_test_parameter') and 'oxy_25000' in self.ctx.get('external_test_data', ''):
            self.execution_space = 70000
        elif 'Oxy' in self.ctx.get('rtyserver_test_parameter'):
            self.execution_space = 40000
        if self.ctx.get('use_multislot'):
            self.cores = 8
            self.ram = 32000
        dprio = 0
        try:
            dprio = int(self.ctx.get('dprio', 0))
        except:
            pass
        self.score = dprio

    def on_failure(self):
        SandboxTask.on_failure(self)
        core_dumps = apihelpers.list_task_resources(task_id=self.id, resource_type=resource_types.CORE_DUMP)
        for _ in core_dumps:
            self.ctx['task_result_type'] += ' CD'
        core_traces = [f for f in os.listdir(self.log_path()) if f.endswith('.gdb.out.txt')]
        if len(core_traces) == 0:
            return
        ts = int(time.time())
        test_aka_serv = self.ctx.get('rtyserver_test_parameter')
        host = self.host
        kps = '53252'
        task_id = self.id
        addr = 'http://saas-cores.n.yandex-team.ru/corecomes?kps=' + kps + \
               '&service=' + test_aka_serv + '&server=' + host + '&time=' + str(ts) + '&task_id=' + str(task_id)
        for f in core_traces:
            bin_aka_ctype = f.split('.')[0]
            ctext = open(self.log_path(f), 'r').read()
            c_addr = addr + '&ctype=' + bin_aka_ctype
            logging.info('will send file=%s size=%s addr=%s' % (f, len(ctext), c_addr))
            try:
                urllib2.urlopen(c_addr, data=ctext, timeout=15)
            except Exception as e:
                logging.error('while sending core: %s' % e)

    def mem_stat_string(self, s):
        pre_str = 'Memory usage info:'
        res = {}
        try:
            infs = s[s.find(pre_str)+len(pre_str):].strip()
            inf = json.loads(infs)
            for por in inf:
                p_name = por["Processor"]
                for stage, val in por.items():
                    if stage != "Processor" and isinstance(val, dict):
                        res[p_name + '_' + stage] = max(
                            res.get(p_name + '_' + stage, 0),
                            val.get("Peak", 0)/float(1000000))
        except Exception as e:
            logging.error('while memory_usage process: error %s, string %s' % (e, s))
        self.ctx['processors_mem_usage'] = res

    def docs_found_by_time(self, logfile):
        doc_lines = []
        for l in open(logfile, 'r').readlines():
            if 'DSTAffxZ' in l:
                doc_lines.append(l)
        if len(doc_lines) == 0:
            return
        plot_data = []
        last_time = 1000000
        for l in doc_lines:
            md = l.strip().split()[-1]
            sec, docs = md.split('/', 1)
            sec = int(sec)
            docs = float(docs)
            if sec < last_time:
                plot_data.append({'data': []})
            plot_data[-1]['data'].append([sec, docs])
            last_time = sec
        for i in range(len(plot_data)):
            plot_data[i]['x'] = 'seconds'
            plot_data[i]['y'] = 'docs_percent'
            plot_data[i]['name'] = str(i)
        levels = [25, 50, 75, 88, 99]
        times = []
        for i in range(len(plot_data)):
            times.append({})
            left = plot_data[i]['data']
            pts = len(left)
            for lev in levels:
                t = -1
                try:
                    left = [d for d in left[:] if d[1] >= lev]
                    ind = pts - len(left)
                    t1 = plot_data[i]['data'][max(ind-1, 0)][0]
                    p1 = plot_data[i]['data'][max(ind-1, 0)][1]
                    t2 = plot_data[i]['data'][min(ind, pts-1)][0]
                    p2 = plot_data[i]['data'][min(ind, pts-1)][1]
                    t = t1 + (t2 - t1)/(p2 - p1)
                except Exception as e:
                    logging.error('%s' % e)
                times[-1][str(lev)] = t
        logging.info('times: %s' % times)
        logging.info('plot_data: %s' % plot_data)
        self.ctx['plots_values'] = plot_data
        self.ctx['plots_data'] = json.dumps(plot_data)
        self.ctx['docs_times'] = times

    def mem_before_dolb(self, entry, lastEntries):
        logging.info(entry)
        rst = extract_rss(entry)
        if rst:
            self.ctx['start_rss_gb'] = round(rst / 1000, 2)
        rst = lastEntries.getMax()
        if rst:
            self.ctx['start_rss_while_gb'] = round(rst / 1000, 2)

    def parseLogfile(self, logFile=None):
        pre_test_results = dict()
        test_times = {}

        do_memusage = 'MemoryUsage' in self.ctx['rtyserver_test_parameter']
        do_docs_plot = False
        do_mem_at_start_dolb = ''
        tfailed_str = ''
        prev_line = ''
        memLines = MemLogStorage()

        if not logFile:
            logFile = self.UNITTEST_OUTLOG

        fpath = os.path.join(self.log_path(), logFile)

        if not os.path.exists(fpath):
            logging.info('WARNING: Parsing log file %s does not exist', fpath)
            return

        if os.stat(fpath)[stat.ST_SIZE] > 5000000000:
            logging.info('WARNING: Parsing log file %s cancelled as it is too big', fpath)
            return

        logging.info('Parsing log file %s' % fpath)

        f = open(fpath, 'r')
        try:
            testlist = f.readlines()
            for test in testlist:
                if test.find('Test') == 0:
                    try:
                        unit_test_name, other = test.split('... ')
                        status, _ = other.split(':')

                        if status == 'OK' and pre_test_results.get(unit_test_name, 'OK') == 'FAILED':
                            status = 'FAILED'

                        pre_test_results.update({unit_test_name: status})
                    except:
                        pass

                if test.find('test=') == 0:
                    parts = test.split(';')
                    try:
                        _, status_value = parts[1].split('=')
                        self.ctx['test_result'] = status_value
                    except:
                        pass

                if test.find('status=') == 0:
                    try:
                        _, status_value = test.split('=')
                        self.ctx['test_result'] = status_value.replace(';', '')
                    except:
                        pass

                if test.find('FAIL: Incorrect usage UnRegisterMessageProcessor') == 0:
                    self.ctx['task_result_type'] += ' UnRegisterMessageProcessor'

                if test.find('SKY FAIL:') != -1:
                    self.ctx['task_result_type'] += ' INFR'
                    self.set_info('<font color="darkred">BAD ENVIRONMENT</font>', do_escape=False)

                if 'Failed test' in test:
                    tfailed_str = prev_line + '\n' + test

                if do_memusage and 'Memory usage info:' in test:
                    self.mem_stat_string(test)

                if 'DSTAffxZ' in test:
                    do_docs_plot = True

                if 'rss=' in test and not do_mem_at_start_dolb:
                    memLines.newLine(test)

                if 'mem_before_dolb_start' in test:
                    do_mem_at_start_dolb = test

                prev_line = test

                if ';full_time=' in test:
                    times = test.split(';')
                    time_marks = ('full_time', 'init_cluster_time', 'stop_cluster_time', 'clear_time')
                    for t in times:
                        for tm in time_marks:
                            try:
                                if t.startswith(tm + '='):
                                    t_time = float(t.split('=')[1].strip('s'))
                                    test_times[tm] = test_times.get(tm, 0) + t_time
                                    break
                            except:
                                pass

            for key, value in pre_test_results.items():
                self.ctx['test_results'].append({'testname': key,
                                                  'status': value})
            if test_times:
                self.ctx['rty_tests_times'] = test_times
        finally:
            f.close()

        if tfailed_str:
            self.set_info(tfailed_str)

        if do_docs_plot:
            self.docs_found_by_time(fpath)

        if do_mem_at_start_dolb:
            self.mem_before_dolb(do_mem_at_start_dolb, memLines)

    def saveResponses(self, ignore_fails):
        if not self.responses_path:
            return
        if os.path.exists(self.responses_path):
            resp_path = self.responses_path
        else:
            pref_path = self.responses_path + '_k_on'
            npref_path = self.responses_path + '_k_off'
            resp_path = pref_path if os.path.exists(pref_path) else npref_path
        if not os.path.exists(resp_path):
            raise SandboxTaskFailureError('path does not exist: ' + resp_path + ', nothing to save')
        try:
            self._create_resource(
                'responses ' + self.descr, resp_path, resource_types.BASESEARCH_HR_RESPONSES,
                complete=True
            )
        except Exception as e:
            logging.info(traceback.format_exc())
            if not ignore_fails:
                raise e

    def checkEnvErrors(self, logfile):
        try:
            with open(logfile, 'r') as lf:
                for line in lf.readlines():
                    if 'SKY FAIL:' in line:
                        self.ctx['task_result_type'] += ' INFR'
                        self.set_info('<font color="darkred">BAD ENVIRONMENT</font>', do_escape=False)
                        break
        except Exception as e:
            logging.error('while parsing log %s, error %s' % (logfile, e))

    def check_memory_threshold(self, logfile, mem_thr):
        max_mem = 0.0
        max_cpu = 0.0
        try:
            with open(logfile, 'r') as logf:
                for line in logf.readlines():
                    ldict = json.loads(line)
                    cmem = float(ldict['%mem'])
                    max_mem = max(max_mem, cmem)
                    ccpu = float(ldict['%cpu'])
                    max_cpu = max(max_cpu, ccpu)
        except:
            logging.warning('fail to analyze log %s' % logfile)
        logging.info('mem-and-cpu in file %s: mem=%s, cpu=%s' % (logfile, max_mem, max_cpu))
        self.ctx['max_memory_gb'] = self.ctx.get('max_memory_gb', 0.0) + (float(self.client_info['physmem'])/100000000000) * max_mem
        self.ctx['max_cpu_perc'] = self.ctx.get('max_cpu_perc', 0.0) + max_cpu / 100
        return max_mem < mem_thr

    def calcTime(self, start_time):
        finish_time = datetime.now()
        self.ctx['finish_rty_tests_time_stamp'] = str(finish_time)
        dur = finish_time - start_time
        self.ctx['rty_tests_work_time'] = str(dur)
        secs = (dur.microseconds + (dur.seconds + dur.days * 24 * 3600) * 10**6) / 10**6
        self.ctx['rty_tests_work_time_seconds'] = secs

    def doPlots(self, plots_path):
        plotter = Plotter()
        pdatas = [p for p in os.listdir(plots_path)
                  if 'plot' in p and p.endswith('.txt') and '.meta.txt' not in p]
        for pd in pdatas:
            plot_data_file = os.path.join(plots_path, pd)
            try:
                plotter.DoPlot(plot_data_file, plot_data_file.replace('.txt', '.png'))
            except Exception as e:
                logging.error('cannot do plot for %s, error: %s' % (plot_data_file, e))

    def doDolbStat(self, dumps_path, dest_path=None):
        scr_d = os.path.join(self.sys_metrics_path, 'dolb_plotstat.sh')
        pl_avg = os.path.join(self.sys_metrics_path, 'avg.pl')
        dolb_stats = [f for f in os.listdir(dumps_path) if f.startswith('dolb_stat_full')]
        for ds in dolb_stats:
            try:
                cmd = [scr_d, ds]
                run_process(cmd, wait=True, environment={'PL_AVG': pl_avg}, work_dir=dumps_path, log_prefix='dolb_plots')
            except Exception as e:
                logging.error('cannot produce plot data for dolb stat, error %s' % e)
            if dest_path:
                plot_data_file = os.path.join(dumps_path, 'plot.' + ds + '.txt')
                if not os.path.exists(plot_data_file):
                    logging.error('cannot find plot data %s' % plot_data_file)
                    continue
                copy_path(plot_data_file, os.path.join(dest_path, 'plot.' + ds + '.txt'))

    def parseFilesCustom(self, filePref, entries):
        dfs = [f for f in os.listdir(self.log_path()) if f.startswith(filePref)]
        parser = Parser()
        result = {}
        for f in dfs:
            if not entries:
                result_file = parser.parseDolbiloResults(self.log_path(f))
                logging.info('parsed file %s, dolb result: %s' % (f, result))
            else:
                result_file = {}
                for ent, ctxf in entries.items():
                    result_file[ctxf] = parser.parseFileGet(self.log_path(f), ent)
            if result_file:
                result.update(result_file)
        return result

    def find_processes_by_cores(self):
        # [{'saved_cmd': '<binary> <...>', 'pid': 123456}, ]
        if not os.path.exists(self.coredump_dir):
            return []
        procs = []
        b_names = ('rtyserver', 'searchproxy', 'indexerproxy', 'deploy_manager', 'monolith')
        bin_names = [nm for nm in b_names
                     if self.ctx.get('test_timeouted', False) or nm not in str(self.ctx.get('no_cores'))]
        existing_pids = [p.pid for p in self._subproc_list]
        cores_count = 0

        class fake_proc:
            def poll(self):
                return 13

            def __init__(self, pid, bin_path):
                self.pid = pid
                self.saved_cmd = bin_path + ' xxx'

        for core_file in os.listdir(self.coredump_dir):
            try:
                cf_parts = core_file.split('.')
                binary_name = cf_parts[0]
                pid = cf_parts[-2] if len(cf_parts) > 1 and cf_parts[-2].isdigit() else cf_parts[-1]

                if binary_name not in bin_names:
                    continue
                pid = int(pid)
                if pid in existing_pids:
                    continue
                core_stat = os.stat(os.path.join(self.coredump_dir, core_file))
                logging.info('core_stat %s, start %s' % (core_stat[stat.ST_MTIME], self.timestamp_start))
                if core_stat[stat.ST_MTIME] > self.timestamp_start:
                    procs.append(fake_proc(pid, os.path.join(self.abs_path(), 'binaries', binary_name)))
                    cores_count += 1
                    if core_stat[stat.ST_SIZE] > 10000000000:  # 10GB
                        self.save_gdb_coredump_files = False
                        logging.info('Size of core dump %s is %d -- greater than 10GB, don\'t save any core dumps', core_file, core_stat[stat.ST_SIZE])
                        if core_stat[stat.ST_SIZE] > 80000000000:  # 80GB
                            logging.info('Size of core dump %s is %d -- greater than 80GB, skip the process %d', core_file, core_stat[stat.ST_SIZE], pid)
                            del procs[-1]
                    if cores_count > 20:
                        logging.info('too many coredumps found, stop processing')
                        break
            except Exception as e:
                logging.error('cannot process core %s, error %s' % (core_file, e))
        return procs

    def postprocess(self):
        beg = time.time()
        if self.test_data_path:
            oxy_spec_names = ['oxy_data', 'mem_usage']
            for fold in oxy_spec_names:
                p = os.path.join(self.test_data_path, fold)
                if os.path.exists(p):
                    chmod(p, 0o777)
                    remove_path(p)
        if self.cluster_test:
            try:
                self._subproc_list.extend(self.find_processes_by_cores())
                logging.info('Subprocesses: %s' % [pr.pid for pr in self._subproc_list])
                logging.info('Subprocesses bins: %s' %
                             [os.path.split(pr.saved_cmd.split(' ')[0])[-1] for pr in self._subproc_list])
            except Exception as e:
                logging.error('cannot process cores, error %s' % e)
        SandboxTask.postprocess(self)
        en = time.time()
        self.ctx['postproc_time'] = int(en - beg)
        self.ctx['queue_time_min'] = round((self.timestamp_start - self.timestamp)/60, 1)

    def rewriteTestSpecificConfigs(self, conf_file, conf_names):
        if not os.path.exists(conf_file):
            raise SandboxTaskFailureError('config %s does not exist' % conf_file)

        with open(conf_file, 'r') as cf:
            conf_text = cf.read()
        new_conf = json.loads(conf_text)
        conf_dir = os.path.dirname(conf_file)
        for nm in conf_names:
            np = os.path.join(conf_dir, nm)
            if not os.path.exists(np):
                raise SandboxTaskUnknownError("internal error: file %s does not exist" % np)
            bin_name = nm.split('.')[0]
            for comp in new_conf:
                if isinstance(comp, dict) and comp.get('product') == bin_name:
                    comp['config'] = nm
        # new_conf_path = os.path.join(conf_dir, os.path.basename(conf_file).replace('.c', test_name + '.c'))
        with open(conf_file, 'w') as cf:
            cf.write(json.dumps(new_conf, indent=4))
        return conf_file

    def checkTestSpecificConfigs(self, conf_dir, test_name):
        paths = []
        bin_names = ['rtyserver', 'searchproxy', 'indexerproxy']
        for bn in bin_names:
            cn = bn + '.' + test_name + '.conf'
            if cn in os.listdir(conf_dir):
                paths.append(cn)
        return paths

    def rewriteInOut(self, conf_file):
        if not os.path.exists(conf_file):
            raise SandboxTaskFailureError('config %s does not exist' % conf_file)
        with open(conf_file, 'r') as cf:
            conf_text = cf.read()
        new_conf = json.loads(conf_text)

        if self.ctx.get('queries_resource_id'):
            self.queries_path = self.sync_resource(self.ctx.get('queries_resource_id'))
        self.responses_path = self.abs_path('responses')

        for b in new_conf:
            if b.get('name') == 'get_responses':
                b['vars']['OUT_PATH'] = self.responses_path
                if self.queries_path:
                    b['vars']['REQUESTS_PATH'] = self.queries_path
            if b['product'] == 'deploy_manager':
                nan_token = self.get_vault_data('RTYSERVER-ROBOT', 'nanny_token')
                b['vars'] = b.get('vars', {})
                b['vars']['OAUTH_NANNY'] = nan_token
                os.environ['OAUTH_NANNY'] = nan_token
            if not b.get('vars', {}) or not isinstance(b.get('vars'), dict):
                continue
            for var, vdescr in b['vars'].items():
                if var == 'JUGGLER_TOKEN':
                    jug_token = self.get_vault_data('RTYSERVER-ROBOT', 'JUGGLER_TOKEN')
                    b['vars'][var] = jug_token
                if isinstance(vdescr, dict) and 'resource' in vdescr:
                    resdescr = vdescr['resource']
                    if isinstance(vdescr, dict) and 'type' in resdescr:
                        rtype = resdescr.get('type')
                        r_attrs = resdescr.get('attrs')
                        logging.info('will be getting %s with %s here' % (rtype, r_attrs))
                        if r_attrs and 'id' in r_attrs:
                            channel.task.sync_resource(r_attrs['id'])
                            res = channel.sandbox.get_resource(r_attrs['id'])
                            b['vars'][var] = res.path
                            del vdescr['resource']
                        elif r_attrs:
                            attr, attrv = r_attrs.items()[0]
                            res_path = ResourceManager().get_resource_to_task_dir(self, rtype, attr, attrv)
                            b['vars'][var] = res_path
                            del vdescr['resource']
                        else:
                            res = apihelpers.get_last_resource(rtype)
                            if not res:
                                logging.error('fail to download resource of type %s' % rtype)
                            channel.task.sync_resource(res.id)
                            res = channel.sandbox.get_resource(res.id)
                            b['vars'][var] = res.path
                            del vdescr['resource']
                        if rtype == 'RTYSERVER_INDEX_DIR' and self.ctx.get('save_index'):
                            self.index_dir_path.append(b['vars'][var])

        with open(conf_file, 'w') as cf:
            cf.write(json.dumps(new_conf, indent=4))

    def extract_used_binaries(self, conf_file):
        with open(conf_file, 'r') as f:
            conf_text = f.read()
        nodes = json.loads(conf_text)
        bin_used = set([nd.get('product', '') for nd in nodes])
        if 'distributor' in bin_used:
            bin_used.add('monolith')
        if 'indexerproxy' in bin_used:
            bin_used.add('indexerproxy')
        logging.info('used binaries: %s' % bin_used)
        self.binaries_used = bin_used

    def ensure_good_json(self, res_id, conf_file):
        with open(conf_file, 'r') as f:
            ftxt = f.read()
        try:
            json.loads(ftxt)
        except:
            if self.ctx.get('restarts_was', 0) < 5:
                self.ctx['restarts_was'] = self.ctx.get('restarts_was', 0) + 1
                self.remove_resource_files(res_id)
                raise SandboxTaskUnknownError('cluster conf is not json: %s' % conf_file)
            else:
                raise SandboxTaskFailureError('cluster conf is not json: %s' % conf_file)

    def prepareConfigs(self):
        if self.configs_path:
            return self.configs_path
        conf_id = self.ctx.get('rtyserver_configs_resource_id')
        if not conf_id:
            raise SandboxTaskFailureError('configs must be set when "-g" is used')
        conf_res_path = self.sync_resource(conf_id)
        conf_path = os.path.join(self.log_path(), 'configs_u')
        copy_path(conf_res_path, conf_path)
        chmod(conf_path, 0o777)

        pars = self.ctx.get('rtyserver_other_parameter')
        pars = pars.split('-g ')[-1].strip()
        conf_file = pars.split()[0].replace('$CONF_PATH', conf_path)
        if self.ctx.get('cluster_cfg_text', '').strip() != '':
            logging.debug('using custom cluster_cfg_text, write to file %s' % conf_file)
            with open(conf_file, 'w') as f:
                f.write(self.ctx.get('cluster_cfg_text'))
        if not os.path.exists(conf_file):
            raise SandboxTaskFailureError("cluster conf file does not exist: %s" % conf_file)
        conf_dir = os.path.dirname(conf_file)
        self.ensure_good_json(conf_id, conf_file)

        unit_test = self.ctx.get('rtyserver_test_parameter', '').split()[0]
        spec_confs = self.checkTestSpecificConfigs(conf_dir, unit_test)
        if spec_confs:
            self.rewriteTestSpecificConfigs(conf_file, spec_confs)
        if self.ctx.get('use_distributor'):
            self.prep_distributor(conf_file)
        self.rewriteInOut(conf_file)
        self.extract_used_binaries(conf_file)
        self.configs_path = conf_path
        return conf_path

    def getExternalTestData(self, test_data_attr, symlink_path, src_subfold=None):
        external_data_path = ResourceManager().get_resource_to_task_dir(
            self, 'RTY_RELATED',
            'rtyserver_test_data', test_data_attr,
            self.abs_path(test_data_attr)
        )
        if src_subfold:
            if os.path.exists(os.path.join(external_data_path, src_subfold)):
                external_data_path = os.path.join(external_data_path, src_subfold)

        if os.path.exists(symlink_path):
            chmod(symlink_path, 0o777)
            remove_path(symlink_path)
        try:
            os.symlink(external_data_path, symlink_path)
        except Exception as e:
            chmod(symlink_path, 0o777)
            remove_path(symlink_path)
            raise e
        chmod(symlink_path, 0o777)
        return symlink_path

    def getOxyData(self, test_data_path):
        syml_path = os.path.join(test_data_path, 'oxy_data')
        cat_path = self.getExternalTestData('oxygen', syml_path, src_subfold='catalog')
        self.oxy_data_path = cat_path
        os.environ['RES_PATH'] = test_data_path

    def getMemUsageTestData(self, test_data_path):
        symlink_path = os.path.join(test_data_path, 'mem_usage')
        cat_path = self.getExternalTestData('mem_usage', symlink_path)
        self.mem_usage_test_data_path = cat_path
        os.environ['RES_PATH'] = test_data_path
        os.environ['DA_OPTS'] = '1'

    def getOxyHugeData(self, test_data_path):
        syml_path = os.path.join(test_data_path, 'oxy', '25000')
        cat_path = self.getExternalTestData('oxy_25000', syml_path)
        os.environ['RES_PATH'] = test_data_path
        self.external_data['oxy_25000'] = cat_path

    def prep_distributor(self, conf_file):
        r_type = 'FUSIONSTORE_PACKAGE'
        conf_svn_path = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/yweb/crawlrank/config/rtyserver_func.cfg'
        distr_dir = ResourceManager().get_resource_to_task_dir(self, r_type, 'resource_name', 'fusionstore')
        distr_conf = ResourceManager().get_resource_to_task_dir(self, 'RTY_RELATED',
                                                                'from_path', conf_svn_path)
        with open(conf_file, 'r') as f:
            cfg = json.loads(f.read())
        for ex in cfg:
            if 'distr' in ex.get('name', ''):
                for var, val in ex['vars'].items():
                    if isinstance(val, dict) and val.get('resource').get('keyword') == 'distributor':
                        ex['vars'][var] = distr_dir
                    elif isinstance(val, dict) and 'CONFIG_PATH' in var:
                        ex['vars'][var] = distr_conf
                for var, val in ex['patch'].items():
                    try:
                        ex['patch'][var] = val.replace('distrib;', self.log_path('distr_dir') + ';')
                    except:
                        pass
        with open(conf_file, 'w') as f:
            new_cfg = json.dumps(cfg, indent=4)
            f.write(new_cfg)

        for port in (8100, 20000, 20100, 20006, 34543):
            for i in range(5):
                distr_cport_free = is_port_free(port)
                logging.info('check_distr_port %s, is_free: %s' % (port, distr_cport_free))
                if distr_cport_free:
                    break
                time.sleep(2)
        run_process(['netstat', '-a'], wait=True, check=False, log_prefix='ports_before_distr')

    def clear_distr_logs(self):
        ddir_path = self.log_path('distr_dir')
        try:
            for fl in os.listdir(ddir_path):
                if fl != 'logs':
                    remove_path(os.path.join(ddir_path, fl))
                else:
                    logdir = os.path.join(ddir_path, fl)
                    logging.info('distr logdir: %s' % os.listdir(logdir))
                    for l in os.listdir(logdir):
                        if os.path.islink(os.path.join(logdir, l)):
                            remove_path(os.path.join(logdir, l))
        except Exception as e:
            logging.info('error while clearing logs: %s' % e)

    def prepareParams(self):
        other_parameters = self.ctx.get('rtyserver_other_parameter').strip()
        if self.type == 'TEST_RTYSERVER_FUNC':
            other_parameters = other_parameters.replace('$TEST_ROOT', self.log_path())
        else:
            other_parameters = other_parameters.replace('$TEST_ROOT', self.abs_path())
        other_parameters = other_parameters.replace('$LOG_PATH', self.log_path())

        # make dir for cache
        cache_dir = os.path.join(self.abs_path(), 'cache')
        make_folder(cache_dir)
        other_parameters = other_parameters.replace('$CACHE_DIR', cache_dir)

        if '-g' in other_parameters and (self.type == 'TEST_RTYSERVER_UNIT' or self.type == 'TEST_RTYSERVER_DOLBILOM'):
            conf_path = self.prepareConfigs()
            other_parameters = other_parameters.replace('$CONF_PATH', conf_path)

        other_parameters = other_parameters.split(' ')

        if self.ctx.get('rtyserver_test_data_path'):
            try:
                if not self.test_data_path:
                    if self.ctx.get('revision'):
                        rev_str = '@' + str(self.ctx['revision'])
                    else:
                        rev_str = ''
                    test_data_path = ArcadiaTestData.get_arcadia_test_data(self, self.ctx.get('rtyserver_test_data_path') + rev_str)
                    try:
                        Arcadia.info(test_data_path)
                    except:
                        ArcadiaTestData.cleanup_arcadia_test_data_folder(self, test_data_path)
                        test_data_path = ArcadiaTestData.get_arcadia_test_data(self, self.ctx.get('rtyserver_test_data_path'))
                    if not os.path.exists(test_data_path):
                        raise SandboxTaskUnknownError('path %s does not exist after getting svn' % test_data_path)
                else:
                    test_data_path = self.test_data_path
            except SandboxSvnError as e:
                err = traceback.format_exc()
                logging.error(traceback.format_exc())
                if '/place/sandbox-data/testdata/trunk/rtyserver/test_data' in err:
                    chmod('/place/sandbox-data/testdata/trunk/rtyserver/test_data', 0o777)
                    ArcadiaTestData.cleanup_arcadia_test_data_folder(self, '/place/sandbox-data/testdata/trunk')
                    test_data_path = ArcadiaTestData.get_arcadia_test_data(self, self.ctx.get('rtyserver_test_data_path'))
                else:
                    raise e
            except OSError as e:
                err = traceback.format_exc()
                logging.error(traceback.format_exc())
                if '/place/sandbox-data/testdata/trunk/rtyserver/test_data' in err:
                    chmod('/place/sandbox-data/testdata/trunk/rtyserver/test_data', 0o777)
                    ArcadiaTestData.cleanup_arcadia_test_data_folder(self, '/place/sandbox-data/testdata/trunk')
                    test_data_path = ArcadiaTestData.get_arcadia_test_data(self, self.ctx.get('rtyserver_test_data_path'))
                else:
                    raise e
            DATAROOT_MARK = '/rtyserver/test_data'
            logging.info('test_data dir content: %s' % os.listdir(test_data_path))
            if DATAROOT_MARK + '/' in test_data_path:
                test_data_path = test_data_path.split(DATAROOT_MARK)[0] + DATAROOT_MARK
            if test_data_path:
                if (
                    (
                        'Oxy' in self.ctx.get('rtyserver_test_parameter')
                        or self.ctx.get('external_test_data', '') == 'oxygen'
                    ) and
                    not self.oxy_data_path
                ):
                    self.getOxyData(test_data_path)

                if (
                    'Oxy' in self.ctx.get('rtyserver_test_parameter') and
                    'Mem' in self.ctx.get('rtyserver_test_parameter') and
                    not self.mem_usage_test_data_path
                ):
                    self.getMemUsageTestData(test_data_path)
                if 'oxy_25000' in self.ctx.get('external_test_data', '') and 'oxy_25000' not in self.external_data:
                    self.getOxyHugeData(test_data_path)
                other_parameters = ['-d', test_data_path] + other_parameters

        test_data_dict_url = self.ctx.get('rtyserver_test_data_dict_path')
        if test_data_dict_url:
            if self.ctx.get('revision'):
                rev_str = '@' + str(self.ctx['revision'])
            else:
                rev_str = ''
            test_data_dict_path = ArcadiaTestData.get_arcadia_test_data(self, test_data_dict_url + rev_str)
            other_parameters = ['-o', test_data_dict_path] + other_parameters

        return other_parameters

    def on_execute(self):
        beg = time.time()
        server_test = self._read_resource(self.ctx['rtyserver_test_resource_id'])
        if server_test.arch != self.arch:
            raise SandboxTaskFailureError('Incorrect server resource #%s arch "%s" on host with arch "%s".'
                                          % (server_test.id, server_test.arch, self.arch))

        profiler = processesProfiler()
        if self.ctx.get('system_stat_attr', False):
            self.sys_metrics_path = ResourceManager().get_resource_to_task_dir(
                self, resource_types.RTY_RELATED, 'type', self.ctx['system_stat_attr']
            )
            profiler.sys_metrics_path = self.sys_metrics_path
            profiler.metrics_output_path = self.log_path('sys_metrics')
            make_folder(profiler.metrics_output_path)

        server_test_path = server_test.abs_path()
        if '-g' in self.ctx.get('rtyserver_other_parameter'):
            self.cluster_test = True
            self.prepareConfigs()
            bin_dir = os.path.join(self.abs_path(), 'binaries')
            make_folder(bin_dir)
            copy_path(server_test_path, os.path.join(bin_dir, 'rtyserver_test'))
            server_test_path = os.path.join(bin_dir, 'rtyserver_test')
            for b_name in ('rtyserver', 'searchproxy', 'indexerproxy', 'deploy_manager', 'monolith'):
                if b_name not in self.binaries_used:
                    continue
                b_id = self.ctx.get(b_name + '_resource_id')
                if not b_id:
                    logging.warning('%s resource not set' % b_name)
                    continue
                b_path = self.sync_resource(b_id)
                copy_path(b_path, os.path.join(bin_dir, b_name))
            if 'emulator' in self.binaries_used:
                emul_id = self.ctx.get('rtyemulator_resource_id')
                if emul_id:
                    emul_path = self.sync_resource(emul_id)
                    copy_path(emul_path, os.path.join(bin_dir, 'rtyserver_emulator'))
                else:
                    ResourceManager().get_resource_to_task_dir(
                        self,
                        resource_types.RTYSERVER_UTILS_RTYSERVER_EMULATOR,
                        'branch', 'trunk',
                        os.path.join(bin_dir, 'rtyserver_emulator')
                    )
        en = time.time()
        self.ctx['download_time'] = int(en - beg)
        beg = en

        profiler.bin_path = os.path.dirname(server_test_path)
        profiler.log_path = self.log_path()
        unit_tests = None

        valgrind_opts = '--leak-check=full --undef-value-errors=yes --num-callers=100'
        if ' valgrind' in self.ctx.get('rtyserver_test_parameter'):
            self.ctx['rtyserver_test_parameter'], valgrind_opts = \
                self.ctx['rtyserver_test_parameter'].split(' valgrind')[0],\
                self.ctx['rtyserver_test_parameter'].split(' valgrind')[1].strip()
        tests_parameters = self.ctx.get('rtyserver_test_parameter')
        if tests_parameters:
            unit_tests = tests_parameters.split(',')

        other_parameters = self.prepareParams()
        en = time.time()
        self.ctx['test_conf_time'] = int(en - beg)
        beg = en

        def on_timeout(process):
            self.ctx['test_timeouted'] = True
            if self.cluster_test:
                for binary in ['deploy_manager', 'searchproxy', 'indexerproxy', 'indexerproxy', 'rtyserver']:
                    run_process(['killall', '-6', binary], wait=True, check=False)
            process.send_signal(signal.SIGABRT)
            for i in range(25):
                if process.poll():
                    break
                time.sleep(5)
            kill_process(process.pid)

            self.ctx['task_result_type'] = 'timeout'

        try:
            run_process(['dstat', '5'], wait=False, log_prefix='dstat')
        except Exception:
            pass

        if unit_tests:

            test_results = []

            for unit_test in unit_tests:
                unit_test_name = unit_test.strip()
                cmd = [server_test_path, self.ctx.get('rtyserver_test_parameter_type'), unit_test_name] + other_parameters
                start_time = datetime.now()
                self.ctx['start_rty_tests_time_stamp'] = str(start_time)

                log_prefix = 'unittest_%s_execution' % unit_test
                self.UNITTEST_OUTLOG = log_prefix + '.out.txt'
                self.UNITTEST_ERRLOG = log_prefix + '.err.txt'
                tester_timeout = self.ctx.get('tester_timeout', 1200)
                try:
                    # env_custom = {'LOG_PATH': self.log_path()}
                    env_special = dict(os.environ)
                    env_special.update({'LOG_PATH': self.log_path()})
                    if self.ctx.get('use_valgrind'):
                        cmd = ['valgrind'] + [op for op in valgrind_opts.split() if len(op) > 0] + cmd

                    if self.ctx.get('use_perftools'):
                        self.prof_tools_path = prepare_gperftools(self)
                        env_special.update(get_gperftolls_environ(self))
                        logging.info('profiler with environ: %s' % env_special)
                        bins_dir = os.path.dirname(server_test_path)
                        os.environ['IPROXY_BIN'] = os.path.join(bins_dir, 'indexerproxy')
                        os.environ['SPROXY_BIN'] = os.path.join(bins_dir, 'searchproxy')
                        os.environ['RTYSERVER_BIN'] = os.path.join(bins_dir, 'rtyserver')
                    try:
                        run_process(["netstat", "-ap"], log_prefix='ports_before_test', check=True, wait=True, shell=True)
                        profiler.start()
                    except MemoryError as e:
                        self.set_info("exception:  %s" % e)
                    # with CustomOsEnviron(env_custom):
                    p = run_process(
                        cmd,
                        timeout=tester_timeout,
                        log_prefix=log_prefix,
                        on_timeout=on_timeout,
                        check=False,
                        outputs_to_one_file=False,
                        close_fds=True,
                        environment=env_special
                    )
                    #   logging.info('before starting profile...')
                    #   profiler.start()
                    if self.ctx.get('save_responses'):
                        self.saveResponses(p.returncode)
                    if self.ctx.get('save_dolb'):
                        parser = Parser()
                        custom_fields = {}
                        if self.ctx.get('parser_rules', '').strip():
                            for line in self.ctx.get('parser_rules').strip().split('\n'):
                                line = line.strip()
                                if not line or '>' not in line:
                                    continue
                                parts = [lp.strip() for lp in line.split('>')]
                                if len(parts) != 3:
                                    logging.warning('invalid parser rule %s, '
                                                    'must be "filepref > entry > ctx_field"' % line)
                                    continue
                                res = self.parseFilesCustom(parts[0], {parts[1]: parts[2]})
                                custom_fields.update(res)
                                for field in res:
                                    parser.writeContext(field, res[field], self.ctx)

                        dfs = [f for f in os.listdir(self.log_path()) if f.startswith('dolb_results')]
                        for f in dfs:
                            result = parser.parseDolbiloResults(self.log_path(f))
                            logging.info('parsed file %s, dolb result: %s' % (f, result))
                            for field in result:
                                if field not in custom_fields:
                                    parser.writeContext(field, result[field], self.ctx)
                    if self.ctx.get('use_perftools'):
                        try:
                            run_process([os.path.join(self.prof_tools_path, 'convert-profiles.sh'), ], log_prefix='profconvert', timeout=7200, wait=True)
                        except Exception as e:
                            logging.info('cannot convert profiles, error %s' % e)
                finally:
                    try:
                        run_process(["netstat", "-ap"], log_prefix='ports_after_test', check=True, wait=True, shell=True)
                    except Exception as e:
                        self.set_info("exception:  %s" % e)
                    self.parseLogfile()
                    self.parseLogfile(self.UNITTEST_ERRLOG)
                    try:
                        self.ctx['log_size_mb'] = round(os.stat(self.log_path(self.UNITTEST_ERRLOG))[stat.ST_SIZE] / 1000000.0, 1)
                    except Exception as e:
                        logging.warning('cannot save log size: %s' % e)
                    for logfile in os.listdir(self.log_path()):
                        if not os.path.isfile(self.log_path(logfile)):
                            continue
                        if logfile.endswith('.log') and logfile != self.UNITTEST_ERRLOG:
                            self.checkEnvErrors(self.log_path(logfile))
                        if '-z' in other_parameters and ('std.err' in logfile or 'std.out' in logfile):
                            self.parseLogfile(self.log_path(logfile))

                    if self.ctx.get('save_root'):
                        copy_path(self.path('root'), self.log_path('root'))

                    if self.ctx.get('save_index') and self.index_dir_path:
                        for i, index_dir in enumerate(self.index_dir_path):
                            packed_index_dir = do_tar(index_dir)
                            self._create_resource(self.descr + ' unpacked_' + str(i), index_dir, 'RTYSERVER_INDEX_DIR', complete=True)
                            self._create_resource(self.descr + ' - ' + str(i), packed_index_dir, 'RTYSERVER_INDEX_DIR', complete=True)

                    for logfile in profiler.outputs:
                        self.check_memory_threshold(logfile, 12.0)
                    self.ctx['max_memory_gb'] = round(self.ctx.get('max_memory_gb', 0), 2)
                    self.ctx['max_cpu_perc'] = round(self.ctx.get('max_cpu_perc', 0), 1)
                    profiler.write_plot_data()
                    if self.ctx.get('system_stat_attr'):
                        self.doDolbStat(self.log_path(), self.log_path('sys_metrics'))
                        self.doPlots(profiler.metrics_output_path)

                    if self.test_data_path:
                        logging.info('test_data dir content: %s' % os.listdir(self.test_data_path))
                    if self.ctx.get('use_distributor'):
                        self.clear_distr_logs()

                self.calcTime(start_time)

                if self.ctx.get('rtyserver_test_parameter_type') in ('-t', '-x'):
                    if p.returncode:
                        status = 'FAILED'
                        self.ctx['task_result_type'] += ' S' + str(p.returncode)
                    else:
                        status = 'OK'

                    test_results.append({'testname': unit_test_name,
                                         'status': status,
                                         'proc': p})

            if test_results:
                excep_str = ''
                for test_result in test_results:
                    if test_result['status'] == 'FAILED':
                        excep_str += 'process "%s" died with exit code %s \n' % (test_result['proc'].saved_cmd, test_result['proc'].returncode)

                self.ctx['test_results'] = [dict([(key, t_r[key]) for key in ('testname', 'status')]) for t_r in test_results]

                if excep_str:
                    raise SandboxTaskFailureError(excep_str)

        else:
            cmd = [server_test_path] + other_parameters

            logging.error('task %s' % on_timeout)
            run_process(cmd,
                        timeout=10800,
                        log_prefix='unittest_all_execution',
                        on_timeout=on_timeout)

        self.set_info('Done')


__Task__ = TestRTYServerUnit
