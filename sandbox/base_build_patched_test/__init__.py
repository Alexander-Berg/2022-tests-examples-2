import logging
import os
import re
import requests

from sandbox import sdk2
from sandbox.sdk2.helpers import subprocess

import sandbox.common.types.task as ctt

from sandbox.projects.common.yappy.github import BuildWithGithubTask


class BuildPatchedTest(BuildWithGithubTask):

    class Requirements(BuildWithGithubTask.Requirements):
        disk_space = 10 * 1024

    class Context(BuildWithGithubTask.Context):
        ya = None
        svn_git_diff = None
        svn_dir = None
        arcadia_dir = None
        run_tests = True
        ya_make_task_type = 'YA_MAKE'

    @property
    def github_context(self):
        raise NotImplementedError

    @property
    def bundle_resource_type(self):
        return None

    @property
    def bundle_description(self):
        return None

    @property
    def bundle_info(self):
        return {}

    @property
    def static_resources(self):
        # paths from root
        return {}

    @property
    def additional_binaries(self):
        return {}

    @property
    def arcadia_project_path(self):
        return self.Parameters.arcadia_path

    def install(self):
        raise NotImplementedError

    def on_execute(self):
        with self.memoize_stage.prepare_and_run_yamake(max_runs=1):
            self.github_statuses.report_self_status(description='Running')
            self.Context.sources_path = self.checkout()
            self.before_install()
            self.install()
            self.after_install()
            self.before_build()
            self.build()

        with self.memoize_stage.collect_binaries:
            self.after_build()

    def build(self):
        with self.info_section('<build> creating YA_MAKE task'):
            with sdk2.helpers.ProcessLog(self, 'build'):

                # convert bundle_info keys to format required by
                # argument "arts" of task

                def get_path_from_project_dir(path_from_src):
                    cut_binary_name = os.path.split(path_from_src)[0]
                    if cut_binary_name[-3:] == 'bin':
                        cut_binary_name = os.path.split(cut_binary_name)[0]
                    return os.path.join(self.arcadia_project_path, 'src', cut_binary_name)

                build_arts = ';'.join(
                    map(
                        get_path_from_project_dir,
                        list(self.bundle_info.keys()) + list(self.additional_binaries.keys())
                    )
                )

                task = sdk2.Task[self.Context.ya_make_task_type](
                    self,
                    description='Ya make task for yappy\n{}'.format(self.Parameters.description.encode('utf-8')),
                    owner=self.owner,
                    targets=self.arcadia_project_path,
                    build_type='release',
                    checkout_mode='auto',
                    arts=build_arts,
                    checkout_arcadia_from_url='arcadia:/arc/trunk/arcadia',
                    arcadia_patch=self.Context.svn_git_diff,
                    test=self.Context.run_tests
                    )
                task.enqueue()

                raise sdk2.WaitTask(task, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)

    def before_install(self):
        with sdk2.helpers.ProcessLog(self, 'before_install') as plog:
            proc_pipes = {'stdout': plog.stdout, 'stderr': plog.stderr}

            with self.info_section('<setup> publish static resources'):
                for path, resource_type in self.static_resources.items():
                    sdk2.ResourceData(
                        resource_type(self, description=path, path=os.path.join(self.Context.sources_path, path))
                        ).ready()

            with self.info_section('<setup> checkout arcadia'):
                self.Context.ya = sdk2.svn.Arcadia.export('arcadia:/arc/trunk/arcadia/ya', 'ya')

                self.Context.arcadia_dir = str(self.path('arcadia_dir'))
                subprocess.check_call([self.Context.ya, 'clone', self.Context.arcadia_dir])

                self.Context.svn_dir = os.path.join(self.Context.arcadia_dir, self.arcadia_project_path)

                # svn up all parent dirs of project
                splitted = self.arcadia_project_path.split('/')
                for i in range(1, len(splitted)):
                    logging.info('>>> --set-depth empty %s', os.path.join(*splitted[:i]))
                    subprocess.check_call([self.Context.ya, 'tool', 'svn', 'up', '--set-depth', 'empty', os.path.join(*splitted[:i])],
                                          cwd=self.Context.arcadia_dir, **proc_pipes)

                logging.info('>>> --set-depth infinity %s', self.arcadia_project_path)
                subprocess.check_call([self.Context.ya, 'tool', 'svn', 'up', '--set-depth', 'infinity', self.arcadia_project_path],
                                      cwd=self.Context.arcadia_dir, **proc_pipes)

            with self.info_section('<prepare> move .git'):
                subprocess.check_call(['mv', os.path.join(
                    self.Context.sources_path, '.git'), self.Context.svn_dir], **proc_pipes)

            with self.info_section('<setup> git reset --hard HEAD'):
                subprocess.check_call(
                    ['git', 'reset', '--hard', 'HEAD'], cwd=self.Context.svn_dir, **proc_pipes)

            with self.info_section('<setup> svn diff'):
                subprocess.check_call(
                    [self.Context.ya, 'tool', 'svn', 'add', '--force', '.'], cwd=self.Context.svn_dir, **proc_pipes)
                try:
                    self.Context.svn_git_diff = subprocess.check_output(
                        [self.Context.ya, 'svn', 'diff', '--notice-ancestry'], cwd=self.Context.svn_dir)
                except subprocess.CalledProcessError as error:
                    self.Context.svn_git_diff = error.output

                # patch should have paths from root of arcadia
                def add_prefix_to_diff_line(diff_line, normalized_prefix):
                    if diff_line[:4] in ('+++ ', '--- '):
                        return '{}{}/{}'.format(diff_line[:4], normalized_prefix, diff_line[4:])
                    elif diff_line[:7] == 'Index: ':
                        return '{}{}/{}'.format(diff_line[:7], normalized_prefix, diff_line[7:])
                    return diff_line

                normalized_prefix = self.arcadia_project_path.strip('/')
                process_one_line = lambda diff_line: add_prefix_to_diff_line(diff_line, normalized_prefix)
                diff_text = '\n'.join(map(process_one_line, self.Context.svn_git_diff.split('\n')))
                if diff_text:
                    diff_r = requests.post('https://paste.yandex-team.ru/', data={'syntax': 'diff', 'text': diff_text})
                    paste_id = re.search('a href="/([0-9]*)/html">HTML', diff_r.text).group(1)
                    self.Context.svn_git_diff = 'https://paste.yandex-team.ru/{}/text'.format(paste_id)
