import os

from sandbox.projects.TestRTYServerTask.resources import ResourceManager
from sandbox.projects import resource_types
from sandbox.sandboxsdk.process import run_process


def prepare_gperftools(task):
    gpt_path = ResourceManager().get_resource_to_task_dir(task, resource_types.RTY_RELATED, 'type', 'google_perftools')
    os.environ['GPERFTOOLS_PATH'] = os.path.join(gpt_path, '.libs')
    os.environ['CONVERTER'] = os.path.join(gpt_path, 'src', 'pprof')
    os.environ['PROFILES_PATH'] = os.path.join(task.log_path(), 'PROFILES')
    return gpt_path


def get_gperftolls_environ(task):
    env = dict()
    env['LD_LIBRARY_PATH'] = os.environ['GPERFTOOLS_PATH']
    env['PROFILEFREQUENCY'] = str(task.ctx.get('gprof_frequency', 100))
    env['LD_PRELOAD'] = 'libprofiler.so'
    env['CPUPROFILESIGNAL'] = '12'
    env['PROFILES_PATH'] = os.environ['PROFILES_PATH']
    return env


def do_tar(path_to_pack):
    if path_to_pack.endswith('/'):
        path_to_pack = path_to_pack[:-1]
    os.chdir(os.path.dirname(path_to_pack))
    fold_name = os.path.basename(path_to_pack)
    run_process(['tar', 'czvf',  fold_name + '.tar.gz', fold_name], log_prefix='pack_tar')
    return path_to_pack + '.tar.gz'


def extract_rss(entry):
    rst = [r for r in entry.split() if r.startswith('rss=')]
    if len(rst) == 0:
        return 0
    rst = rst[0]
    rst = rst.split('Mb')[0]
    rst = rst.replace('rss=', '')
    try:
        rst = float(rst)
        return rst
    except:
        return 0


class MemLogStorage:
    lines = []
    linesLimit = 200

    def newLine(self, line):
        self.lines.append(line)

        if len(self.lines) > self.linesLimit:
            self.lines = self.lines[self.linesLimit/3:]

    def getMax(self):
        max_mem = 0
        for line in self.lines:
            try:
                max_mem = max(max_mem, extract_rss(line))
            except:
                pass
        return max_mem
