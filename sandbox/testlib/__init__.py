import os
from os.path import join as pjoin
import re

from sandbox.sandboxsdk.paths import make_folder
from sandbox.sandboxsdk.process import run_process


class ImagesTestlibBase():
    pack = None

    tables_dir_name = 'tables_dir'

    config_dir = 'config'
    sysconfig_dir = 'input_files'
    node_chunk_store_quota = None
    yt_nodes_count = None

    def __init__(self, yt_parameters, directories):
        self.yt_executable = yt_parameters['bin']
        self.yt_runner_env = yt_parameters['env']
        self.proxy = yt_parameters['proxy']
        self.bin_dir = directories['binary_dir']
        self.dump_dir = directories['dump_dir']
        self.dump_bin_dir = directories['dump_bin_dir']
        self.config_dir = directories['config_dir']
        self.sysconfig_dir = directories['sysconfig_dir']

    def run_tests(self):
        for stage in self.pack:
            self.run_stage(stage)

    def launcher(self, cmd):
        env = os.environ.copy()
        env['MR_RUNTIME'] = 'YT'
        env['YT_USE_YAMR_STYLE_PREFIX'] = '1'
        env['YT_PREFIX'] = '//'
        env['YT_USE_CLIENT_PROTOBUF'] = '0'

        for k, v in self.yt_runner_env.items():
            if k == 'PATH' and 'PATH' in env:
                env[k] = v + ":" + env[k]
            else:
                env[k] = v

        return run_process(cmd, shell=True, environment=env).returncode

    def run_stage(self, stage):
        pre_stage_exit_code = 0
        stage_exit_code = 0
        post_stage_exit_code = 0
        dumper_exit_code = 0

        bin_dir = self.bin_dir
        program = pjoin(bin_dir, stage.program or stage.desc.split()[0])
        server = self.proxy
        yt = self.yt_executable

        if stage.system_cmd:
            sysconfig_dir = pjoin(stage.files_dir, self.sysconfig_dir)
            cmd = stage.system_cmd.format(mr_server=server,
                                          config_dir=sysconfig_dir,
                                          files_dir=stage.files_dir,
                                          program=program,
                                          dump_dir=self.dump_dir,
                                          bin_dir=self.bin_dir,
                                          yt=yt,
                                          **stage.custom_fields
                                          )
            pre_stage_exit_code = self.launcher(cmd)
            if pre_stage_exit_code != 0:
                return (pre_stage_exit_code, stage_exit_code, post_stage_exit_code,
                        dumper_exit_code)

        if stage.cmd:
            binary = pjoin(bin_dir, stage.desc.split()[0]) if not stage.binary else pjoin(bin_dir, stage.binary)
            config_dir = pjoin(stage.files_dir, self.config_dir)
            cmd = stage.cmd.format(mr_server=server,
                                   config_dir=config_dir,
                                   files_dir=stage.files_dir,
                                   program=binary,
                                   bin_dir=self.bin_dir,
                                   dump_dir=self.dump_dir,
                                   **stage.custom_fields)
            stage_exit_code = self.launcher(" ".join(cmd.split()))
            if stage_exit_code != 0:
                return (pre_stage_exit_code, stage_exit_code, post_stage_exit_code,
                        dumper_exit_code)

        if stage.post_cmd:
            cmd = stage.post_cmd.format(mr_server=server,
                                        config_dir=self.sysconfig_dir,
                                        program=program,
                                        dump_dir=self.dump_dir,
                                        bin_dir=self.bin_dir,
                                        yt=yt,
                                        **stage.custom_fields
                                        )
            post_stage_exit_code = self.launcher(cmd)
            if post_stage_exit_code != 0:
                return (pre_stage_exit_code, stage_exit_code,
                        post_stage_exit_code, dumper_exit_code)

        if self.dump_dir:
            dumper_exit_code = self.dump_results(stage)

        return (pre_stage_exit_code, stage_exit_code, post_stage_exit_code, dumper_exit_code)

    def get_dumper(self, name, custom_suffix_dumper_modes, custom_regex_dumper_modes):
        mode = None
        for (suffix, m) in custom_suffix_dumper_modes:
            if name.endswith(suffix):
                mode = m
                break

        if not mode:
            for (pattern, m) in custom_regex_dumper_modes:
                if re.search(pattern, name):
                    mode = m
                    break
        if not mode:
            mode = '%s -t hex' % (pjoin(self.bin_dir, 'yson_converter'))
        return mode

    def make_dumper_script(self, raw_table, stage):
        yt = self.yt_executable
        proxy = self.proxy
        table = raw_table.format(**stage.custom_fields)
        yson_converter = pjoin(self.bin_dir, 'yson_converter')
        dumper = self.get_dumper(table, stage.suffix_dump_modes, stage.regex_dump_modes)
        dump_dir = self.dump_dir
        name = table.replace('/', ':')

        script = '''
                     set -e -x
                     dumper={yson_converter}
                     {yt} --proxy {proxy} read --format yson {table} 2>/dev/null | {dumper} > {dump_dir}/{name}.txt
                 '''.format(yt=yt,
                            proxy=proxy,
                            table=table,
                            yson_converter=yson_converter,
                            dumper=dumper,
                            dump_dir=dump_dir,
                            name=name)
        return script

    def make_binary_dumper_script(self, raw_table, stage):
        yt = self.yt_executable
        proxy = self.proxy
        table = raw_table.format(**stage.custom_fields)
        dump_dir = self.dump_bin_dir
        table_subdir, table_name = os.path.split(table.replace("//", ""))
        table_dir = pjoin(dump_dir, table_subdir)
        make_folder(table_dir)

        script = '''
                     set -e -x
                     {yt} --proxy {proxy} read --format yson {table} 2>/dev/null > {table_dir}/{table_name} || true
                     attributes_names=(sorted_by)
                     for name in "${{attributes_names[@]}}"; do attr_params="${{attr_params}} --attribute ${{name}}"; done
                     attributes=$({yt} --proxy {proxy} get {table} ${{attr_params}} --format '<format=pretty>yson')
                     attributes=${{attributes:0:-1}}
                     attributes=${{attributes:1:-2}}
                     table_meta='{{"attributes" = {{ '${{attributes}}' }}; "type" = "table"; "format" = "<format=binary>yson";}}'
                     echo "$table_meta" > {table_dir}/{table_name}.meta
                 '''.format(yt=yt,
                            proxy=proxy,
                            table=table,
                            table_dir=table_dir,
                            table_name=table_name)
        return script

    def dump_results(self, stage):
        for raw_table in stage.output_tables:
            script = self.make_dumper_script(raw_table, stage)
            exit_code = self.launcher(script)
            if exit_code != 0:
                return exit_code

            binary_script = self.make_binary_dumper_script(raw_table, stage)
            binary_exit_code = self.launcher(binary_script)
            if binary_exit_code != 0:
                return binary_exit_code
        return 0
