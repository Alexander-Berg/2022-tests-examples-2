import subprocess
import os
import shutil


def run_pyflame(pyflame_bin_path, duration, rate, log_dir):
    vins_pids = subprocess.check_output(['pidof', '-x', 'pa'])
    stacks_output_path = os.path.join(log_dir, 'pyflame_stacks')
    if os.path.exists(stacks_output_path):
        shutil.rmtree(stacks_output_path)
    os.mkdir(stacks_output_path)
    for p in vins_pids.split():
        with open(os.path.join(stacks_output_path, '{}_stack.txt'.format(p)), 'w+') as logfile:
            subprocess.Popen(['sudo', pyflame_bin_path, '-s', str(duration), '-r', str(rate), '-p', p], stdout=logfile,
                             stderr=subprocess.STDOUT)
    return stacks_output_path
