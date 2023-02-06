# -*- coding: utf-8 -*-

import logging
import os
import time
import urllib2
import copy
import json
import signal
import traceback

from datetime import datetime
from string import Template

from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.process import run_process, start_process_profiler
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.paths import get_unique_file_name
from sandbox.sandboxsdk.paths import copy_path, chmod
from sandbox.sandboxsdk.paths import make_folder
from sandbox.sandboxsdk.paths import remove_path
from sandbox.sandboxsdk.errors import SandboxTaskFailureError, SandboxTaskUnknownError
from sandbox.sandboxsdk.environments import SvnEnvironment
from sandbox.sandboxsdk.network import is_port_free

from sandbox.projects import resource_types

from sandbox.projects.common import apihelpers

from sandbox.projects.TestRTYServerTask.resources import ResourceManager
from sandbox.projects.TestRTYServerTask.parser import Parser


def get_comp_type(comp):
    return comp[0].split()[-1]


class Services:
    was_service = False
    last_service = ''
    services = {}
    serv_names = {}
    serv_with_auth = []
    shards = {}
    serv_url_hash = []

    def process_line(self, line):
        if line.strip() == '':
            self.last_service = ''
            return
        if line.split()[-1] == 'SERVICE':
            self.last_service = line.split()[0]
            self.services[self.last_service] = []
            self.shards[self.last_service] = ''
        elif self.last_service != '' and line.split()[0] == 'Rty':
            self.services[self.last_service].append(line.split()[-1])
        elif self.last_service != '' and line.split()[0] == 'Name' and self.last_service not in self.serv_names:
            self.serv_names[self.last_service] = line.split()[-1]
        elif self.last_service != '' and line.split()[0] == 'RequireAuth' and line.split()[-1].lower() in ('true', '1', 'yes', 'da'):
            self.serv_with_auth.append(self.last_service)
        elif self.last_service != '' and line.split()[0] == 'ShardBy' and line.split()[-1].lower() == 'url_hash':
            self.serv_url_hash.append(self.last_service)
        elif self.last_service != '' and line.split()[0].lower() == 'shards':
            self.shards[self.last_service] = line.replace('Shards', '').strip()
        elif line.split()[-1] in ('SYSTEM', 'ACTION', 'CONTR', 'QUERY', 'MAIN'):
            self.last_service = ''


class Patcher:
    def __init__(self, own, is_backend=True):
        self.own = own
        self.is_be = is_backend
        self.patch_lines = {}
        self.patch_text = ''

    def add_patch_line(self, field, value):
        self.patch_lines[field] = value
        logging.info('line added to patch: %s' % value)

    def get_patch(self):
        if not self.patch_lines:
            return False
        self.patch_text = json.dumps(self.patch_lines, indent=4)
        return self.patch_text

    def patch_it(self, cfg_text):
        p_text = self.get_patch()
        patcher_path = self.own.preprocess_scriptline('${RTYSERVER_UTILS_CONFIG_PATCHER:branch:trunk}')
        in_fn = get_unique_file_name(self.own.log_path_, 'cfg_to_patch.cfg')
        out_fn = get_unique_file_name(self.own.log_path_, 'cfg_after_patch.cfg')
        p_fn = get_unique_file_name(self.own.log_path_, 'cfg_patch.diff')
        with open(in_fn, 'w') as in_f:
            in_f.write(cfg_text)
        with open(p_fn, 'w') as p_f:
            p_f.write(str(p_text))
        patcher_cmd = [patcher_path, in_fn, p_fn, out_fn]
        if not self.is_be:
            patcher_cmd.append('--ignore-prefix')
        run_process(patcher_cmd, log_prefix='patch_cfg')
        with open(out_fn, 'r') as out_f:
            res = out_f.read()
        self.patch_lines = {}
        self.patch_text = ''
        return res


class RtyInfrastructureRunner:
    component_configs = {
        'RTYSERVER': {
            'running port': 'BACKEND_SEARCH_PORT',
            'ports': {
                'BACKEND_CONTROLLER_PORT': 15023,
                'BACKEND_SEARCH_PORT': 15020,
                'BACKEND_DISK_PORT': 17020,
                'BACKEND_MEMORY_PORT': 19000,
                'BACKEND_INDEXER_PORT': 15022,
                'BACKEND_BASESEARCH_PORT': 15021,
            },
            'paths': {
                'LOG_PATH': 'logs',
                'BACKEND_RUN_PATH': 'locks',
                'INDEX_PATH': 'index',
                'DETACH_PATH': 'synchr'
            },
            'count': 1,
        },
        'SPROXY': {
            'running port': 'SEARCH_PROXY_PORT',
            'ports': {
                'SEARCH_PROXY_PORT': 13020,
                'SEARCH_PROXY_CONTROLLER_PORT': 13023,
            },
            'paths': {
                'LOG_PATH': 'logs',
            },
            'count': 1,
        },
        'IPROXY': {
            'running port': 'INDEXER_PROXY_PORT',
            'ports': {
                'INDEXER_PROXY_PORT': 10020,
                'INDEXER_PROXY_NEH_PORT': 10021,
                'INDEXER_PROXY_CONTROLLER_PORT': 10023,
            },
            'paths': {
                'LOG_PATH': 'logs',
            },
            'count': 1,
        },
        'RTYEMULATOR': {
            'running port': 'BACKEND_SEARCH_PORT',
            'ports': {
                'BACKEND_SEARCH_PORT': 15020,
                'BACKEND_INDEXER_PORT': 19020,
                'BACKEND_CONTROLLER_PORT': 11020,
                'BACKEND_CONTROLLER_PORT_OLD': 18020,
            },
            'paths': {
                'LOG_PATH': 'logs',
            }
        },
    }
    _task = None
    _busy_ports = []
    _busy_sports = []
    _cfdata = {
        'launched_comps': {},
        'disp_pres': False,
        'smap_done': False
    }
    replacements = [{'field': 'FactorsInfo'}]

    services = Services()
    resources = ResourceManager()

    abs_path_ = ''
    log_path_ = ''
    config_dir = ''
    prof_tools_path = ''
    sys_metrics_path = ''
    ctx = {}
    PROCESSES = []
    proc_names = {}
    bin_paths = {}
    dict_path = False
    scr_vars = {}
    parse_files = []
    save_files = []

    def preparePath(self, pathName, compType, compName):
        if 'LOG' in pathName:
            par_dir = self.log_path_
        else:
            par_dir = self.abs_path_
        npath = os.path.join(par_dir, compType + compName + pathName[:-5].lower())
        make_folder(npath)
        self.component_configs[compType]['paths'][pathName] = npath
        return npath

    def findFreePort(self, port):
        while port in self._busy_ports or not is_port_free(port):
            port += 1
        self._busy_ports.append(port)
        return port

    def backend_ports(self, port):
        PORTS_NUM = 6
        port_beg = port

        while True:
            p_free = 0
            while p_free < PORTS_NUM:
                if not (port_beg + p_free) in self._busy_ports and is_port_free(port_beg + p_free):
                    p_free += 1
                else:
                    port_beg += p_free + 1
                    break
            if p_free >= PORTS_NUM:
                break
        self._busy_ports.extend([(port_beg + i) for i in range(6)])
        ports = {
            'BACKEND_CONTROLLER_PORT': port_beg + 3,
            'BACKEND_SEARCH_PORT': port_beg,
            'BACKEND_DISK_PORT': port_beg + 2,
            'BACKEND_MEMORY_PORT': port_beg + 2,
            'BACKEND_INDEXER_PORT': port_beg + 2,
            'BACKEND_BASESEARCH_PORT': port_beg + 1,
        }
        return ports

    def abs_path(self):
        return self.abs_path_

    def createSearchMap(self):
        if self._cfdata['smap_done']:
            return
        services = self.services.services  # O_O no fantasy!
        serv_names = self.services.serv_names
        serv_auth = self.services.serv_with_auth
        serv_uhash = self.services.serv_url_hash

        smpath = os.path.join(self.config_dir, 'searchmap.tpl')
        if os.path.exists(smpath):
            os.chmod(smpath, 0o777)

        shards_total = 65533
        used_rtys = []
        smap = {}
        serv_map_templ = {
            'storage_type': 'kiwi',
            'replicas': {}
        }

        def get_shards(rty_sh):
            rty_shards = {}
            reps = [r.strip('() ,') for r in rty_sh.split(')') if len(r.strip('() ,')) > 0]
            for replicas_rty in reps:
                rty_repl = [r.strip() for r in replicas_rty.replace(',', ' ').split() if len(r.strip()) > 0]
                parts_num = len(rty_repl)
                for i, rty_1be in enumerate(rty_repl):
                    min_sh = i*(shards_total / parts_num)
                    max_sh = (i+1)*(shards_total / parts_num) - 1 if i+1 != parts_num else shards_total
                    rty_shards[rty_1be] = (min_sh, max_sh)
            return rty_shards

        for serv in services:
            rtys = services[serv]
            rty_shards = get_shards(self.services.shards.get(serv, ''))
            if len(rtys) == 0:
                continue
            serv_name = serv_names.get(serv, serv)
            serv_map = copy.deepcopy(serv_map_templ)
            serv_map['replicas']['default0'] = []
            if serv in serv_auth:
                serv_map['require_auth'] = True
            if serv in serv_uhash:
                serv_map['shard_by'] = 'url_hash'
            slots = {}
            for i, rty in enumerate(rtys):
                if rty not in self._cfdata['launched_comps']:
                    logging.warning(
                        'cannot find server %s for service %s, configuration is probably incorrect!' % (rty, serv))
                    continue
                if rty in rty_shards:
                    start_shard = rty_shards[rty][0]
                    end_shard = rty_shards[rty][1]
                else:
                    start_shard = 0
                    end_shard = shards_total
                used_rtys.append(rty)
                try:
                    rep = {'host': 'localhost', 'shard_min': start_shard, 'shard_max': end_shard}
                    rep['search_port'] = self._cfdata['launched_comps'][rty]['ports']['BACKEND_SEARCH_PORT']
                    rep['indexer_port'] = self._cfdata['launched_comps'][rty]['ports']['BACKEND_INDEXER_PORT']
                    serv_map['search_port'] = self._cfdata['launched_comps'][rty]['ports']['BACKEND_SEARCH_PORT']
                    serv_map['indexer_port'] = self._cfdata['launched_comps'][rty]['ports']['BACKEND_INDEXER_PORT']
                    slots[rty] = rep
                except:
                    pass
            nrep = len([s for s in slots if slots[s]['shard_min'] == 0])
            for i in range(nrep):
                serv_map['replicas']['default' + str(i)] = []
                cmax = 0
                while True:
                    sls = [s for s in slots if slots[s]['shard_min'] == cmax]
                    if len(sls) == 0:
                        break
                    next_sl = sls[0]
                    cmax = slots[next_sl]['shard_max'] + 1
                    serv_map['replicas']['default' + str(i)].append(slots[next_sl].copy())
                    del slots[next_sl]

            smap[serv_name] = serv_map

        for rty in self._cfdata['launched_comps']:
            if rty not in used_rtys:
                try:
                    serv_map = copy.deepcopy(serv_map_templ)
                    serv_map['search_port'] = self._cfdata['launched_comps'][rty]['ports']['BACKEND_SEARCH_PORT']
                    serv_map['indexer_port'] = self._cfdata['launched_comps'][rty]['ports']['BACKEND_INDEXER_PORT']
                    serv_map['replicas']['default0'] = [
                        {'host': 'localhost', 'shards_min': 0, 'shards_max': shards_total,
                         'search_port': self._cfdata['launched_comps'][rty]['ports']['BACKEND_SEARCH_PORT'],
                         'indexer_port': self._cfdata['launched_comps'][rty]['ports']['BACKEND_INDEXER_PORT']}]
                    smap[rty] = serv_map
                except:
                    pass

        with open(smpath, 'w') as smd:
            smd.write(json.dumps(smap))

        copy_path(smpath, os.path.join(self.config_dir, 'searchmap'))
        os.chmod(os.path.join(self.config_dir, 'searchmap'), 0o755)
        copy_path(smpath, os.path.join(self.config_dir, 'searchmap.json'))
        os.chmod(os.path.join(self.config_dir, 'searchmap.json'), 0o755)
        self._cfdata['smap_done'] = True

    def getEnvironForProfiler(self, binary):
        env = dict(os.environ)
        env['LD_LIBRARY_PATH'] = os.environ['GPERFTOOLS_PATH']
        comp_prof_path = os.path.join(os.environ['PROFILES_PATH'], binary, binary)  # do bin unique!
        make_folder(comp_prof_path)
        env['CPUPROFILE'] = os.path.join(comp_prof_path, 'cpu.profile')
        env['PROFILEFREQUENCY'] = str(self.ctx.get('gprof_frequency', 100))
        env['LD_PRELOAD'] = 'libprofiler.so'
        env['CPUPROFILESIGNAL'] = '12'
        return env

    def run_prog(self, binary, cfg, check=True, cmd_env=()):

        # get binary file
        binary_res_path = self.bin_paths.get(self.ctx['%s_resource_id' % binary])
        if not binary_res_path:
            channel.task.sync_resource(self.ctx['%s_resource_id' % binary])
            binary_res = channel.sandbox.get_resource(self.ctx['%s_resource_id' % binary])

            if not self.ctx.get('deploy_manager_task'):
                binary_res_path = binary_res.path
                self.bin_paths[self.ctx['%s_resource_id' % binary]] = binary_res_path
            else:
                binary_res_init_path = binary_res.path
                bin_folder = get_unique_file_name(self.abs_path_, 'rtyserver_binary')
                binary_res_path = os.path.join(bin_folder, 'rtyserver')
                copy_path(binary_res_init_path, binary_res_path)
                new_cfg_folder = os.path.join(bin_folder, 'configs')
                copy_path(os.path.dirname(cfg), new_cfg_folder)
                new_cfg = os.path.join(new_cfg_folder, 'rtyserver.conf-common')
                copy_path(cfg, new_cfg)
                cfg = new_cfg

        if not os.path.exists(binary_res_path):
            raise SandboxTaskFailureError("Binary doesn't exist %s" % binary_res_path)

        cmd = [binary_res_path, cfg]
        env = dict(os.environ)

        if self.ctx.get('use_perftools', False) and (
                'proxy' in binary or ('rtyserver' in binary and self.ctx.get('profile_rtyserver', False))):
            env = self.getEnvironForProfiler(binary)
            env['%s_BIN' % binary.upper()] = binary_res_path
            os.environ['%s_BIN' % binary.upper()] = binary_res_path

        if cmd_env:
            extra_env = dict(cmd_env)
            logging.info('added environment from m-script %s' % extra_env)
            env.update(extra_env)

        if self.ctx.get('deploy_manager_task'):
            env.update(dict([(i[0], str(i[1])) for i in self.component_configs['RTYSERVER']['ports'].items()]))
            env.update(dict([(i[0], str(i[1])) for i in self.component_configs['RTYSERVER']['paths'].items()]))

        logging.info(cmd)
        logging.info('subprocess environment : %s' % env)

        binary_proc = run_process(cmd, log_prefix='run_%s' % binary, wait=False, check=check, environment=env)

        self.check_process(binary_proc, binary)

        self.PROCESSES.append(binary_proc)
        self.proc_names[str(binary_proc.pid)] = binary
        return binary_proc

    def check_process(self, proc, desc=''):
        try:
            if proc.poll():
                raise SandboxTaskFailureError('process "%s" terminated, code %s' % (str(desc), str(proc.returncode)))
        except Exception as e:
            raise SandboxTaskFailureError('process "%s", exception %s' % (str(desc), e))

    def checkProgStatus(self, name, port, proc=None, ch_back=False):
        timeout = 8
        if ch_back:
            timeout = int(self.ctx.get('mtester_timeout', 900)) / 60
            if timeout < 1:
                timeout = 15
        start_time = int(time.time())
        self.ctx['deploy_timed_out'] = False

        def get_url(port):
            if ch_back:
                # return 'http://localhost:%s/?info_server=yes' % port
                return 'http://localhost:%s/?command=get_info_server' % port
            else:
                return 'http://localhost:%s/ping' % port

        url = get_url(port)
        logging.info('Checking status %s %s....' % (name, url))

        while True:
            end_time = int(time.time())
            if (end_time - start_time) / 60 > timeout:
                self.ctx['deploy_timed_out'] = True
                break
            if proc:
                self.check_process(proc, name)
            try:
                resp = urllib2.urlopen(url, timeout=15)
                if resp.getcode() == 200:
                    if not ch_back:
                        logging.info('%s answered (%s)' % (name, url))
                        break
                    else:
                        rtext = resp.read()
                        if '"server_status":"Active"' in rtext.replace('\n', '').replace(' ', '').replace('\t', ''):
                            logging.info('%s answered (%s)' % (name, url))
                            logging.info('result: %s' % rtext)
                            break
                        else:
                            logging.info('waiting for server...')
                            logging.debug(rtext.replace(':\n', ':').replace(': \n', ''))
                            time.sleep(8)
            except urllib2.HTTPError as e:
                if e.code == 400:
                    logging.info('400 received')
                    pass
                raise SandboxTaskFailureError('HTTPError in getting %s code %s' % (url, e))
            except urllib2.URLError:
                pass
            except Exception as e:
                raise SandboxTaskFailureError(e)
            time.sleep(1)
        if self.ctx['deploy_timed_out']:
            if proc and not proc.poll():
                try:
                    proc.send_signal(signal.SIGABRT)
                except Exception as e:
                    logging.error('while terminate process %s, error %s' % (proc.pid, e))
            raise SandboxTaskFailureError("Deploy timed out")

    def send_signal_prof(self):
        for binname in ('rtyserver', 'searchproxy', 'indexerproxy'):
            if binname == 'rtyserver' and not self.ctx.get('profile_rtyserver'):
                continue
            try:
                run_process(['killall', '-12', binname], log_prefix='kill_12_' + binname)
            except Exception as e:
                logging.error('while send -12, error: %s' % e)

    def run_profilers(self):
        run_process(['ps', 'x'], check=False, log_prefix='ps_x')
        try:
            run_process(['dstat', '15'], wait=False, log_prefix='dstat')
            run_process(['iostat', '-mx', '15'], wait=False, log_prefix='iostat')
            run_process(['vmstat', '15'], wait=False, log_prefix='vmstat')
        except Exception:
            pass

        for proc in self.PROCESSES:
            if 'emul' in self.proc_names[str(proc.pid)]:
                continue
            start_process_profiler(
                proc,
                ['%cpu', '%mem', 'vsz', 'rss', 'dsiz'],
                get_unique_file_name(
                    self.log_path_,
                    'proc%s%s' % (proc.pid, self.proc_names[str(proc.pid)])
                )
            )

    def get_resource_to_task_dir(self, resType, attrName, attrValue, downTo=None):
        if not downTo:
            downTo = get_unique_file_name(self.abs_path_, str(resType) + '_res')
        res = self.resources.get_or_download_resource(self._task or self, resType, attrName, attrValue, downTo)
        if res.path == downTo:
            logging.info("warning: resource for copy is already here %s" % downTo)
            return downTo
        logging.info("copying to path %s" % downTo)
        if os.path.exists(downTo):
            remove_path(downTo)
        if not res.path.endswith(self.resources.tarExt):
            copy_path(res.path, downTo)
        else:
            downTo = self.resources.unpackTar(res.path, downTo)

        try:
            chmod(downTo, 0o777)
        except:
            pass
        os.chmod(downTo, 0o777)
        return downTo

    def replaceLineValue(self, line, prop, new_value):
        cur_value = line.strip().split()[-1]
        if cur_value not in (prop, ':'):
            return line.replace(cur_value, new_value)
        else:
            return line

    def copyDictData(self, cfg_text):
        """
        if recognizeLibrary set in config, copies it to appropriate path,
        changes lines in config
        :param cfg_text:
        :return:
        """

        def create_rlf():
            if self.dict_path:
                return self.dict_path
            rec_file_name = os.path.join(self.ctx.get('rtyserver_test_data_dict_path') or
                                         'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia_tests_data/recognize',
                                         'dict.dict')
            try:
                self.dict_path = self.get_resource_to_task_dir(resource_types.RTYSERVER_DICT, 'from_path',
                                                               rec_file_name,
                                                               os.path.join(self.abs_path_, 'dict.dict'))
            except Exception as e:
                logging.info(traceback.format_exc())
                logging.error("fail to handle data dict for rty %s exception %s" % (rec_file_name, e))
                raise SandboxTaskFailureError(e)

            return self.dict_path

        def check_recfile_name(rfname):
            return rfname not in ('NOTSET', ':', '', 'RecognizeLibraryFile')

        cfg_lines = cfg_text.split('\n')
        for i, line in enumerate(cfg_lines):
            if line.strip().startswith('RecognizeLibraryFile'):
                rec_file_name = line.split()[-1]
                if check_recfile_name(rec_file_name):
                    rec_file_name = create_rlf()
                    cfg_lines[i] = self.replaceLineValue(line, 'RecognizeLibraryFile', rec_file_name)
        return '\n'.join(cfg_lines)

    def copyIndexDir(self, in_path, out_path):
        if in_path in ('EMPTY', 'NOTSET', ''):
            return out_path
        if ':' not in in_path:
            last_ex_res = self.get_resource_to_task_dir(resource_types.RTYSERVER_INDEX_DIR, 'key', in_path, out_path)
        else:
            last_ex_res = self.get_resource_to_task_dir(resource_types.RTYSERVER_INDEX_DIR, 'from_path',
                                                        in_path, out_path)
        return last_ex_res

    def findValue(self, cfg_lines, vName):
        value = ''
        for i, line in enumerate(cfg_lines):
            if line.strip().startswith(vName):
                value = line.strip().split()[-1]
                if value in ('NOTSET', ':', ''):
                    value = ''
        return value

    def replValueInText(self, cfg_text, vName, vValue):
        cfg_lines = cfg_text.split('\n')
        for i, line in enumerate(cfg_lines):
            if line.strip().startswith(vName):
                cfg_lines[i] = self.replaceLineValue(cfg_lines[i], vName, vValue)
        return '\n'.join(cfg_lines)

    def replValueInFile(self, vName, vValue, fIn, fOut=None):
        with open(fIn, 'r') as f:
            f_text = f.read()
        f_text = self.replValueInText(f_text, vName, vValue)
        if not fOut:
            fOut = fIn
        with open(fOut, 'w') as o:
            o.write(f_text)

    def processInclFile(self, inc_file):
        """
        extracts separated information about components from file
        """
        last_comp = []
        components = []

        if not os.path.isfile(inc_file):
            raise SandboxTaskFailureError('include file %s does not exist' % inc_file)
        cfg = open(inc_file, 'r')
        for nline in cfg.readlines():
            line = nline.strip()
            if line == '':
                continue
            if (line.split()[-1]) in self.component_configs and len(last_comp) > 0:
                components.append(last_comp)
                last_comp = []
            last_comp.append(line)
            logging.info(line)
        if len(last_comp) > 0:
            components.append(last_comp)

        cfg.close()
        return components

    def process_nested_replacements(self, cfg_text):
        for rep in self.replacements:
            if not rep['field'] in cfg_text:
                continue
            addr = self.findValue(cfg_text.split('\n'), rep['field'])
            if addr == '':
                continue
            nf_name = os.path.basename(addr)
            nf_path = os.path.join(self.config_dir, nf_name)
            if not os.path.exists(nf_path):
                raise SandboxTaskFailureError('nested files replacements: path %s does not exist' % nf_path)
            with open(nf_path, 'r') as nf:
                nf_text = nf.read()
            nf_text = '\n'.join([self.preprocess_scriptline(lin) for lin in nf_text.split('\n')])
            with open(nf_path, 'w') as nf:
                nf.write(nf_text)
        return

    def configureComponent(self, comp):
        """
        makes concrete configs and launches component
        :param comp: component config description
        :return: ready part of main_cfg file
        """
        if comp == ['']:
            return comp

        comp_type = comp[0].split()[-1]
        comp_name = comp[0].split()[0]

        for pathname in self.component_configs[comp_type]['paths']:
            self.preparePath(pathname, comp_type, comp_name)

        if comp_type == 'RTYSERVER':
            cport = self.component_configs[comp_type]['ports']['BACKEND_SEARCH_PORT']
            self.component_configs[comp_type]['ports'] = self.backend_ports(cport)
        else:
            for portname in self.component_configs[comp_type]['ports']:
                cport = self.component_configs[comp_type]['ports'][portname]
                self.component_configs[comp_type]['ports'][portname] = self.findFreePort(cport)

        # for use self-variables in replace: and environ:
        self._cfdata['launched_comps'][comp_name] = copy.deepcopy(self.component_configs[comp_type])

        # create single cfg
        cfg = os.path.join(self.config_dir, comp_type + comp_name + '.cfg')
        cfgin = ''
        add_env = []
        rep_values = {}
        patch = Patcher(self, comp_type == 'RTYSERVER')
        for line in comp[1:]:
            if line.lower().startswith('config'):
                cfgin = line.split()[-1]
            elif line.lower().startswith(('index ', 'index:')):
                ipath = self.component_configs[comp_type]['paths']['INDEX_PATH']
                i_in_path = line.split()[-1]
                res_path = self.copyIndexDir(i_in_path, ipath)
                if not res_path == ipath:
                    self.component_configs[comp_type]['paths']['INDEX_PATH'] = res_path
                add_env.append(('IndexDir', res_path))
            elif line.lower().startswith('environ'):
                # run component with this environment variables
                if len(line.split()) > 1:
                    env_param = self.preprocess_scriptline(' '.join(line.split()[2:]))
                    cmd_params = (line.split()[1].strip('${}'), env_param)
                    add_env.append(cmd_params)
            elif line.lower().startswith('field'):
                # add/edit fields in config
                if len(line.split()) == 1:
                    continue
                field = line.split()[1]
                value = ''
                if len(line.split()) > 2:
                    value = self.preprocess_scriptline(' '.join(line.split()[2:]))
                patch.add_patch_line(field, value)

            elif line.lower().startswith('replace'):
                # replace text in config
                parts = line.split()
                if len(parts) == 1:
                    continue
                elif len(parts) < 3:
                    logging.warning('fail to process line "%s", must be "replace value_to_repl value_repl_by"' % line)
                var = parts[-2]
                val = self.preprocess_scriptline(parts[-1])
                rep_values[var] = val

        if ':' not in cfgin:
            cfgin = os.path.join(self.config_dir, cfgin)
            cfgin = os.path.normpath(cfgin)
        else:
            cfgin = self.resolveValue('RTY_RELATED:from_path:%s' % cfgin)
        if not os.path.isfile(cfgin):
            raise SandboxTaskFailureError("Config file %s does not exist or isn't a file" % cfgin)
        with open(cfgin, 'r') as cfgfilein:
            cfg_text = cfgfilein.read()

        for var, val in rep_values.items():
            cfg_text = cfg_text.replace(var, val)

        start_server = False
        # change cfg-$ depending on type...
        if comp_type == 'RTYSERVER':
            cfg_text = self.copyDictData(cfg_text)
            cfg_text = self.replValueInText(cfg_text, 'IndexDir',
                                            self.component_configs['RTYSERVER']['paths']['INDEX_PATH'])
            start_server = not ('StartServer : 0' in [l.strip() for l in cfg_text.split('\n')])
            if '${FUSION_BIN_PATH}' in cfg_text:
                f_b_p = self.resolveValue('TEAMCITY_RESOURCE:resource_name:fusion:branch:trunk')
                cfg_text = cfg_text.replace('${FUSION_BIN_PATH}', f_b_p + '/bin')
        elif comp_type == 'RTYEMULATOR' and not self.ctx.get('rtyemulator_resource_id', 0):
            self.ctx['rtyemulator_resource_id'] = apihelpers.get_last_resource_with_attribute(
                resource_types.RTYSERVER_UTILS_RTYSERVER_EMULATOR, 'branch', 'trunk').id

        elif comp_type == 'IPROXY':
            pass

        self._cfdata['launched_comps'][comp_name] = copy.deepcopy(self.component_configs[comp_type])
        cfg_text = cfg_text.replace('./log', self.component_configs[comp_type]['paths']['LOG_PATH'])
        cfg_text = cfg_text.replace(' ./', ' ' + self.config_dir + '/')
        cfg_text = Template(cfg_text).safe_substitute({'CONF_PATH': self.config_dir})
        cfg_text = Template(cfg_text).safe_substitute(self.component_configs[comp_type]['ports'])
        cfg_text = Template(cfg_text).safe_substitute(self.component_configs[comp_type]['paths'])
        self.process_nested_replacements(cfg_text)

        if patch.get_patch():
            cfg_text = patch.patch_it(cfg_text)
            # logging.warning('setting fields is not implemented yet, patch ignored')

        with open(cfg, 'w') as cfgfile:
            cfgfile.write(cfg_text)

        # run component
        proc = self.run_prog(comp_type.lower(), cfg, cmd_env=tuple(add_env))
        self._cfdata['launched_comps'][comp_name]['pid'] = proc.pid
        running_port_t = self.component_configs[comp_type]['running port']
        checking_port_t = running_port_t
        if comp_type == 'RTYSERVER':
            checking_port_t = 'BACKEND_CONTROLLER_PORT'
        running_port = self.component_configs[comp_type]['ports'][running_port_t]
        checking_port = self.component_configs[comp_type]['ports'][checking_port_t]
        self.checkProgStatus(comp_type.lower() + comp_name, checking_port, proc, False)
        if comp_type == 'RTYSERVER' and start_server:
            self.checkProgStatus(comp_type.lower() + comp_name, checking_port, proc, True)
            # change text in comp...
        changed_comp = [comp[0]]
        for line in comp[1:]:
            if line.startswith(('Port', 'port')):
                changed_comp.append('Port %s' % str(running_port))
            elif line.startswith('Cport'):
                changed_comp.append(
                    'Cport %s' % str(self.component_configs[comp_type]['ports']['BACKEND_CONTROLLER_PORT']))
            elif line.startswith(('Config', 'config')):
                changed_comp.append('Config %s' % cfg)
            elif line.startswith(('SearchMap', 'Searchmap', 'searchmap')):
                changed_comp.append('SearchMap %s' % os.path.join(self.config_dir, 'searchmap.tpl'))
            else:
                changed_comp.append(line)

        return changed_comp

    def get_abs_inc_path(self, ifile, script_file):
        # may be changed depending on rules of 'includes' in the script files
        if os.path.isabs(ifile):
            return ifile
        else:
            return os.path.normpath(os.path.join(os.path.dirname(script_file), ifile))

    def resolveValue(self, var):
        '''
        var format:  smth:smth_else:more_if_need

        return: ready path
        '''
        if ':' not in var:
            # return '${' + var + '}'
            return get_unique_file_name(self.log_path_, var.lower())
        sep = var.find(':')
        fir = var[:sep]

        if fir.lower() in ('file', 'new', 'f'):
            return get_unique_file_name(self.log_path_, var[sep + 1:].lower())

        if fir in self._cfdata['launched_comps']:
            if var[sep + 1:] == 'pid':
                return self._cfdata['launched_comps'][fir]['pid']
            ans = self._cfdata['launched_comps'][fir]['ports'].get(var[sep + 1:], None)
            if ans:
                logging.info('%s resolved as %s (component port)' % (var, str(ans)))
                return ans
            ans = self._cfdata['launched_comps'][fir]['paths'].get(var[sep + 1:], None)
            if ans:
                logging.info('%s resolved as %s (component path)' % (var, str(ans)))
                return ans
            else:
                logging.info("Fail to resolve the expression %s as component's" % var)

        if fir.lower() in ['self', 'pid']:
            ctx_f = var[sep + 1:]
            # now for binaries only
            if not ctx_f.endswith('resource_id'):
                ctx_f += '_resource_id'
            ctx_f = ctx_f.replace('indexerproxy', 'iproxy')\
                .replace('searchproxy', 'sproxy')\
                .replace('search_proxy', 'sproxy')
            if self.ctx.get(ctx_f):
                if fir.lower() == 'self':
                    bres_path = channel.task.sync_resource(self.ctx.get(ctx_f))
                    b_path = bres_path
                    if 'deploy' in ctx_f:
                        b_path = get_unique_file_name(self.abs_path_, ctx_f.replace('_resource_id', ''))
                        copy_path(bres_path, b_path)
                    return b_path
                else:
                    logging.info('not implemented pid')
                    pass
            else:
                logging.error('fail to find %s binary in task context' % ctx_f)
                return

        if var.startswith('RESOURCE:'):
            var = ':'.join(var.split(':')[1:])

        r_type = var.split(':')[0]
        if r_type not in channel.sandbox.list_resource_types():
            logging.error("%s is not resource type" % r_type)
            return
        if len(var.split(':')) == 1:
            res = apihelpers.get_last_resource(r_type)
            if not res:
                logging.error('fail to download resource of type %s' % r_type)
            channel.task.sync_resource(res.id)
            res = channel.sandbox.get_resource(res.id)
            return res.path

        r_attr_1, a_value_1 = None, None
        if len(var.split(':')) == 2:
            r_attr = 'key'
            a_value = var.split(':')[1]
        else:
            r_attr = var.split(':')[1]
            a_value = ':'.join(var.split(':')[2:])
            if 'path' not in r_attr and 'url' not in r_attr and ':' in a_value:
                vp = var.split(':')
                a_value = vp[2]
                r_attr_1 = vp[3]
                if len(vp) < 4:
                    a_value_1 = None
                else:
                    a_value_1 = vp[4]

        res_path, res = None, None
        if not r_attr_1:
            try:
                res_path = self.get_resource_to_task_dir(r_type, r_attr, a_value,
                                                         downTo=get_unique_file_name(self.abs_path_, r_type))
            except Exception as e:
                logging.info(traceback.format_exc())
                raise SandboxTaskUnknownError("cannot find or download %s, error %s" % (var, e))
        else:
            logging.info('getting resource with two attributes %s:%s, %s:%s' % (r_attr, a_value, r_attr_1, a_value_1))
            try:
                res = self.resources.get_resource_with_two_attrs(r_type, r_attr, a_value, r_attr_1, a_value_1)
                if not res:
                    raise SandboxTaskFailureError('cannot find resource')
            except:
                raise SandboxTaskUnknownError("cannot find or download %s" % var)

        if res_path:
            return res_path
        return res.path

    def preprocess_scriptline(self, line):
        """
        substitutes ${variables} in script
        return: line with ready paths
        """
        to_subst = []
        e = 0
        while '${' in line[e:]:
            beg = e + line[e:].find('${')
            e = beg + line[beg:].find('}')
            to_subst.append(line[beg + 2:e])

        for var in to_subst:
            if var not in self.scr_vars:
                self.scr_vars[var] = self.resolveValue(var)

        for old in self.scr_vars:
            line = line.replace('${' + old + '}', str(self.scr_vars[old]))

        return line

    def Configure(self, scriptfile):
        """
        substitutes variables in template cfg file by concrete values,
        writes it to file main_config,
        runs processes and ports,
        creates necessary folders,
        adds 'informative' files to info_paths
        :param scriptfile: config template
        :return:
        """
        cfgout_path = os.path.join(self.log_path_, 'main_multi.rtytsconf')
        cfgout = open(cfgout_path, 'w')
        scriptout_path = os.path.join(self.log_path_, 'main_multi.rtyts')
        scrout = open(scriptout_path, 'w')
        scrout.write('INCLUDE %s\n' % cfgout_path)
        scrout_text = []

        components = []
        scr = open(scriptfile, 'r')
        try:
            for line in scr.readlines():
                if line.strip().startswith('INCLUDE') and line.strip().endswith('.rtytsconf'):
                    # line == 'INCLUDE somefile.rtytsconf', need 'somefile.rtytsconf'
                    line = line.strip().split()[-1]
                    line = self.get_abs_inc_path(line, scriptfile)
                    components.extend(self.processInclFile(line))
                elif line.strip().startswith('INCLUDE'):
                    # shell scripts: line == 'INCLUDE somefile.sh', need 'somefile.sh'
                    line = line.strip().split()[-1]
                    absfile = self.get_abs_inc_path(line, scriptfile)
                    copy_path(absfile, os.path.join(self.log_path_, line))
                    os.chmod(os.path.join(self.log_path_, line), 0o777)
                elif line.strip().startswith('PARSE'):
                    self.parse_files.append(line)
                elif line.strip().startswith('SAVE'):
                    self.save_files.append(line)
                else:
                    self.services.process_line(line)
                    scrout_text.append(line)

            for comp in components:
                if get_comp_type(comp) in ('RTYSERVER', 'RTYEMULATOR'):
                    cfgout.write('\n'.join(self.configureComponent(comp)))
                    cfgout.write('\n\n')
            self.createSearchMap()
            # s&i-proxy depend on rty, they must be configured after
            for comp in components:
                if get_comp_type(comp) in ['IPROXY', 'SPROXY']:
                    cfgout.write('\n'.join(self.configureComponent(comp)))
                    cfgout.write('\n\n')

            for line in scrout_text:
                line = self.preprocess_scriptline(line)
                scrout.write(line)

        finally:
            scr.close()
            cfgout.close()
            scrout.close()
        return scriptout_path

    dummy = ''


class TestRTYServerTask(SandboxTask):
    type = 'TEST_RTYSERVER_TASK_OLD'

    environment = [SvnEnvironment(), ]

    execution_space = 12000

    info_paths = []
    PROCESSES = []

    parser = Parser()

    default_root = 'svn+ssh://arcadia.yandex.ru/arc/trunk'

    def initCtx(self):
        self.ctx['start_rty_tests_time_stamp'] = ''
        self.ctx['finish_rty_tests_time_stamp'] = ''
        self.ctx['rty_tests_work_time'] = ''
        self.ctx['rty_tests_work_time_seconds'] = ''
        self.ctx['task_result_type'] = ''

        self.ctx['test_results'] = []
        self.ctx['test_result'] = ''

    def kill_processes(self):
        # kill all processes if any
        for proc in self.PROCESSES:
            proc.terminate()

    def on_failure(self):
        SandboxTask.on_failure(self)
        core_dumps = apihelpers.list_task_resources(task_id=self.id, resource_type=resource_types.CORE_DUMP)
        for _ in core_dumps:
            self.ctx['task_result_type'] += ' CD'

    def calcTime(self, start_time):
        finish_time = datetime.now()
        self.ctx['finish_rty_tests_time_stamp'] = str(finish_time)
        dur = finish_time - start_time
        self.ctx['rty_tests_work_time'] = str(dur)
        secs = (dur.microseconds + (dur.seconds + dur.days * 24 * 3600) * 10 ** 6) / 10 ** 6
        self.ctx['rty_tests_work_time_seconds'] = secs

    def saveLogs(self):
        try:
            logs_path = get_unique_file_name(self.log_path(), 'info')
            for path in self.info_paths:
                copy_path(os.path.join(self.abs_path(), path), logs_path)
        except OSError as error:
            logging.error(error)

    def parseGetToCtx(self, filename, to_get, ctx_field, must_exist=False, must_not_empty=False):
        result = self.parser.parseFileGet(filename, to_get, must_exist, must_not_empty)
        self.parser.writeContext(ctx_field, result, self.ctx)

    def parseDolbiloToCtx(self, filename, ctx_pref='', must_exist=False, must_not_empty=False):
        result = self.parser.parseDolbiloResults(filename, must_exist, must_not_empty)
        logging.info(result)
        if ctx_pref and ctx_pref[-1] != '_':
            ctx_pref += '_'
        if not ctx_pref:
            ctx_pref = ''
        for field in result:
            self.parser.writeContext(ctx_pref + field, result[field], self.ctx)
        try:
            perc_empty = 100*float(result['result_empty'][0])/(float(result['result_empty'][0]) + float(result['requests_ok'][0]))
            self.parser.writeContext('result_empty_perc', [str(perc_empty), ], self.ctx)
        except Exception as e:
            logging.error('while empty percents: %s' % e)

    def toParser(self, line, scr_vars):
        ways = ['ew:', 'get:', 'dolb:']
        line = line.strip()
        if len(line) < 3:
            return
        line, must_exs, must_nempty = self.parser.getMusts(line)
        line, var = self.parser.getFName(line, scr_vars)
        if not var:
            logging.warning('cannot find variable file name in %s' % line)
            return

        line, field = self.parser.getCtxField(line)
        way, params = self.parser.getWayToParse(line, ways)

        if not way:
            logging.warning('cannot find how to parse %s in %s. Methods available are %s' % (var, line, ways))
            return

        params_in = None
        if params != '':
            try:
                params_in = eval(params)
                logging.info('evaluated %s as %s, type %s' % (params, params_in, type(params_in)))
            except:
                logging.error(
                    "failed to eval %s in %s. Use Python syntax. Examples: 'str1', ['p1', 'p2'], None" % (params, line))
                return

        if way == 'ew:':
            self.parser.parseFileEW(scr_vars[var], params_in, must_exs, must_nempty)
            return
        elif way == 'get:':
            self.parseGetToCtx(scr_vars[var], params_in, field, must_exs, must_nempty)
            return
        elif way == 'dolb:':
            self.parseDolbiloToCtx(scr_vars[var], field, must_exs, must_nempty)
            return

        logging.info('not found existing filename in line %s' % line)

    def ParseCustom(self, lines, scr_vars):
        for line in lines:
            logging.info('line to parser: %s' % line)
            entries = line.strip().split('PARSE')
            for ent in entries:
                self.toParser(ent, scr_vars)

    def toSave(self, line, scr_vars):
        # ${file_name}:resource_type[:attrnm:attrv]
        logging.info('trying to save %s' % line)
        line = line.strip().strip(':')
        if len(line) < 3:
            return

        line, fname = self.parser.getFName(line, scr_vars)
        fname = scr_vars[fname]

        if not line.startswith(':'):
            fname = fname + line.split(':')[0]
            line = ':'.join(line.split(':')[1:])
        if not fname:
            raise SandboxTaskFailureError('Error in script, cannot find var in SAVE line %s' % line)
        line, mex, mne = self.parser.getMusts(line)

        params = line.strip(':').split(':')
        res_type = 'RTY_RELATED'
        attrn, attrv = None, None
        if len(params) == 1:
            res_type = params[0]
        elif len(params) == 2:
            attrn = params[0]
            attrv = params[1]
        elif len(params) == 3:
            res_type = params[0]
            attrn = params[1]
            attrv = params[2]
        else:
            logging.error('cannot process params %s' % params)
        if res_type not in channel.sandbox.list_resource_types():
            raise SandboxTaskFailureError('%s in %s is not a resource type' % (res_type, str(params)))

        res_path = fname
        if self.log_path() in res_path:
            res_name = os.path.basename(res_path)
            res_path_new = get_unique_file_name(self.abs_path(), res_name)
            copy_path(res_path, res_path_new)
            res_path = res_path_new

        self._create_resource(self.descr, res_path, res_type, complete=True, attrs={attrn: attrv})

    def SaveCustom(self, lines, scr_vars):
        for line in lines:
            logging.info('line to save: %s' % line)
            entries = line.strip().split('SAVE')
            for ent in entries:
                self.toSave(ent, scr_vars)

    def check_memory_threshold_dep(self, logfile, mem_thr):
        max_mem = 0.0
        try:
            with open(logfile, 'r') as logf:
                for line in logf.readlines():
                    cmem = float(json.loads(line)['%mem'])
                    max_mem = max(max_mem, cmem)
        except Exception as e:
            logging.warning('fail to analyze log %s, error %s' % (logfile, e))
        self.ctx['max_memory_gb'] = self.ctx.get('max_memory_gb', 0.0) + (float(self.client_info['physmem'])/100000000000) * max_mem
        return max_mem < mem_thr

    def process_memory_usage(self):
        self.ctx['max_memory_gb'] = 0.0
        for lfile in os.listdir(self.log_path()):
            if lfile.startswith('proc') and lfile.endswith('rtyserver'):
                self.check_memory_threshold_dep(self.log_path(lfile), 20)
        self.ctx['max_memory_gb'] = round(self.ctx.get('max_memory_gb', 0), 2)

    dummy = ''


__Task__ = TestRTYServerTask
