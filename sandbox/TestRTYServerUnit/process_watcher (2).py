
from sandbox.sandboxsdk.process import run_process, start_process_profiler
from sandbox.sandboxsdk.paths import get_unique_file_name
import logging
import threading
import time
import os


class FakeProcess:

    def poll(self):
        try:
            os.kill(self.pid, 0)
            return None
        except OSError:
            return self.poll_result
        except Exception as e:
            logging.error('in poll: %s' % e)
            return self.poll_result

    def __init__(self, pid, bin_path, poll_result=13):
        self.pid = int(pid)
        self.saved_cmd = bin_path + ' xxx'
        self.poll_result = poll_result


bin_names = ['rtyserver_test', 'rtyserver', 'searchproxy', 'indexerproxy', 'deploy_manager']


class processesProfiler(threading.Thread):
    pids = set()
    outputs = []

    parent_proc = None
    bin_path = ''
    log_path = ''
    sleep_time = 10
    find_sleep_time = 15
    sys_metrics_path = ''
    metrics_output_path = ''

    def proc_list(self, delete_after=True):
        p = run_process(['ps', 'wxfl'], outputs_to_one_file=True, log_prefix='wxf')
        fn = p.stdout_path
        with open(fn, 'r') as f:
            procs = f.readlines()
        if delete_after:
            os.unlink(fn)
        return procs

    def find_procs(self):
        procs = self.proc_list()
        logging.info('all procs: %s' % procs)
        pp = [p.strip() for p in procs if self.bin_path in p and ('-P' in p or '-t' in p or '-x' in p)]
        logging.info('with binpath: %s' % len(pp))
        pp = [p for p in pp if not p.split()[2] in self.pids]
        logging.info('new processes found: %s' % pp)
        return pp

    def find_parent_proc(self):
        procs = self.proc_list()
        pp = [p for p in procs if os.path.join(self.bin_path, 'rtyserver_test') in p and ('-t' in p or '-x' in p)]
        try:
            ppid = pp[0].strip().split()[2]
            int(ppid)
            self.parent_proc = FakeProcess(ppid, os.path.join(self.bin_path, 'rtyserver_test'))
            return True
        except:
            return None

    def newPids(self):
        procs = []
        np = self.find_procs()
        for p in np:
            pid = p.split()[2]
            try:
                int(pid)
            except:
                continue
            try:
                exe_path = [s for s in p.split() if s.startswith(self.bin_path)][0]
                if not os.path.basename(exe_path) in bin_names:
                    continue
            except:
                continue
            logging.info('new process found: %s' % p)
            self.pids.add(pid)
            fproc = FakeProcess(pid, exe_path)
            procs.append(fproc)
        return procs

    def renew(self):
        new_procs = self.newPids()
        for p in new_procs:
            bin_name = os.path.basename(p.saved_cmd.split()[0])
            prof_path = get_unique_file_name(self.log_path, 'proc.' +
                                             bin_name + '.' + str(p.pid))
            self.outputs.append(prof_path)
            start_process_profiler(p, ['%cpu', '%mem', 'vsz', 'rss', 'dsiz'], prof_path, 10)
            if self.sys_metrics_path:
                sysmetr_scr_path = os.path.join(self.sys_metrics_path, 'run_system_metrics.sh')
                cmd = [sysmetr_scr_path, str(p.pid), str(p.pid), bin_name]
                logging.info('%s' % cmd)
                run_process(cmd, wait=False, check=False,
                            work_dir=self.metrics_output_path or os.path.join(self.log_path, 'sys_metrics'),
                            log_prefix='sysmetr')

    def run(self):
        for i in range(5):
            time.sleep(2)
            if self.find_parent_proc():
                break
        logging.info('watcher started, process %s, bin_path %s' % (self.parent_proc, self.bin_path))
        if not self.log_path or not self.bin_path:
            logging.error('some paths not set: l=%s, b=%s' % (self.log_path, self.bin_path))
        while self.parent_proc and self.parent_proc.poll() is None:
            try:
                self.renew()
            except Exception as e:
                logging.warning('exception in process_watcher, %s' % e)
            time.sleep(self.find_sleep_time)

    def write_plot_data(self):
        scr = os.path.join(self.sys_metrics_path, 'plotstat.sh')
        if not os.path.isfile(scr):
            logging.error('plotstat file %s does not exist' % scr)
            return
        for pid in self.pids:
            try:
                cmd = [scr, pid]
                stat_path = os.path.join(self.log_path, 'sys_metrics')
                run_process(cmd, wait=True, work_dir=stat_path, log_prefix='sysplots_data')
            except Exception as e:
                logging.error('cannot produce plot data for dolb stat, error %s' % e)
