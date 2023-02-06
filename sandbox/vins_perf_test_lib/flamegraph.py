import logging
import shutil
import subprocess

import os


def make_flamegraph(flamegraph_scripts_path, path_to_stacks_dir, version, description, log_prefix, num_of_run, log_dir):
    stacks = []
    for s in os.listdir(path_to_stacks_dir):
        stacks.append(os.path.join(path_to_stacks_dir, s))
    merged_stacks_path = os.path.join(log_dir, '{}_{}_merged_stacks_{}.txt'.format(log_prefix, version, num_of_run))
    flamegraph_svg_path = os.path.join(log_dir, '{}_{}_flamegraph_{}.svg'.format(log_prefix, version, num_of_run))

    with open(merged_stacks_path, 'w+') as merged_out:
        merge_cmd = [os.path.join(flamegraph_scripts_path, 'merge_stacks.py')] + stacks
        logging.info('Merge cmd: {}'.format(' '.join(merge_cmd)))
        subprocess.call([os.path.join(flamegraph_scripts_path, 'merge_stacks.py')] + stacks, stdout=merged_out,
                        stderr=subprocess.STDOUT)

    with open(flamegraph_svg_path, 'wb+') as flamegraph_svg:
        subprocess.call(
            [os.path.join(flamegraph_scripts_path, 'flamegraph.pl'), merged_stacks_path, '--title', description],
            stdout=flamegraph_svg)

    shutil.move(path_to_stacks_dir, path_to_stacks_dir + '_{}_{}'.format(version, num_of_run))
