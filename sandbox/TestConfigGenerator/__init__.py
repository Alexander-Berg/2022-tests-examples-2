import re
import os

from sandbox.sandboxsdk.channel import channel
import sandbox.sandboxsdk.parameters as parameters
import sandbox.common.types.client as client
import sandbox.projects.common.gencfg.task as gencfg_task

from sandbox.projects.common.gencfg.utils import ERepoType, clone_gencfg_all


class LastCommit(parameters.SandboxStringParameter):
    name = 'last_commit'
    description = 'Commit to test'
    default_value = ''


class DryRun(parameters.SandboxBoolParameter):
    name = 'dry_run'
    description = 'Run as much as possible but do not change anything'
    default_value = False


class TestConfigGenerator(gencfg_task.IGencfgBuildTask):
    type = 'TEST_CONFIG_GENERATOR'

    client_tags = client.Tag.CUSTOM_GENCFG_BUILD

    input_parameters = [
        DryRun,
        LastCommit,
    ]

    @property
    def dry_run(self):
        return self.ctx[DryRun.name]

    def get_skips(self):
        skips = {'mongo': False, 'clickhouse': False, 'hbf': False}
        commit = gencfg_task.normalize_commit(self.ctx['last_commit'])
        for record in gencfg_task.get_topology_mongo()['commits'].find({'commit': commit, 'skip': {'$exists': True}}).limit(1):
            skips.update(record['skip'])

        return skips

    def on_enqueue(self):
        self.ctx['build_status'] = "SCHEDULED"
        self.ctx['build_broken_goals'] = []
        self.ctx['diff_builder_result'] = ""

    def on_execute(self):
        author = None

        skip = self.get_skips()
        self.ctx['skip'] = skip

        try:
            commit = self.ctx['last_commit']
            self.clone_and_install_generator(commit=commit, precalc_caches=True, create_resource=False, create_cache_resource=True, load_cache_resource=True)
            author = self.get_last_commit_author(os.path.join(self.get_gencfg_path(), 'db'))

            # add generate diff in background
            prev_commit_path = os.path.join(self.ramdrive.path, 'gencfg_prev_commit')
            clone_gencfg_all(prev_commit_path, ERepoType.FULL, revision=int(commit)-1)
            generate_diff_cmd = ['./tools/diffbuilder/main.py', '-q', '-o', prev_commit_path, '-n', self.get_gencfg_path()]
            self.add_background_command(generate_diff_cmd, 'diffbuilder')

            if not self.dry_run:
                # add export to clickhouse in background
                # if not skip['clickhouse']:
                    # import_to_clickhouse_cmd = ['./utils/common/import_to_clickhouse.py', '-a', 'update']
                    # self.add_background_command(import_to_clickhouse_cmd, 'import_to_clickhouse')

                # add export to hbf in background
                if not skip['hbf']:
                    import_to_hbf_cmd = ['./utils/common/manipulate_hbf.py', '-a', 'update', '-v']
                    self.add_background_command(import_to_hbf_cmd, 'import_to_hbf')

                # add export to gencfg_trunk in background
                if not skip['mongo']:
                    import_to_gencfg_trunk_cmd = ['./utils/mongo/populate_gencfg_trunk.py']
                    self.add_background_command(import_to_gencfg_trunk_cmd, 'import_to_gencfg_trunk')

                    # leave last 100 commits in gencfg_trunk
                    self.clean_gencfg_trunk(commit)

            try:
                self.build_generator(create_resources=False, run_only_checks=True, skip_cache=False)
                self._set_test_status(skip, commit, success=True, author=author)
            except Exception, e:
                self.ctx['build_exception'] = str(e)
                # Mark diffbuilder error like false positive
                if './tools/diffbuilder/main.py' in str(e):
                    self._set_test_status(skip, commit, success=True, author=author)
                else:
                    self.ctx['build_broken_goals'] = re.findall('^make: \*\*\* \[(.*)\] Error .*$', open(self.log_path('generator.out.txt')).read(), flags=re.MULTILINE)
                    self._set_test_status(skip, commit, success=False, author=author)

            self.ctx['diff_builder_result'] = open(self.log_path('diffbuilder.out.txt')).read()

        except Exception, e:  # GENCFG-1693
            self.ctx['build_broken_goals'] = []
            self.ctx['build_exception'] = str(e)
            self._set_test_status(skip, commit, success=False, author=author)

        for resource in self.list_resources():
            if resource.type.name != 'TASK_LOGS':
                channel.sandbox.set_resource_attribute(resource.id, 'tag', "trunk-r%s" % self.ctx['last_commit'])

    def _set_test_status(self, skip, commit, success, author):
        self.ctx['build_status'] = 'SUCCESS' if success else 'FAILURE'

        if not self.dry_run and not skip['mongo']:
            self.set_test_status(commit, success=success, author=author)


__Task__ = TestConfigGenerator
