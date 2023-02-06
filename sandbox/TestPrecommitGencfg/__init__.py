# coding: utf8
import os
import json
import shutil
from datetime import datetime
import logging
from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.sdk2.vcs.svn import Arcadia
import sandbox.projects.common.constants as consts
import sandbox.common.types.client as ctc
from subprocess import Popen, PIPE


class ArcadiaPatch(sdk2.parameters.String):
    name = consts.ARCADIA_PATCH_KEY
    description = (
        "Apply patch (diff file rbtorrent, paste.y-t.ru link or plain text). "
        "Doc: https://nda.ya.ru/3QTTV4"
    )
    default_value = ''
    multiline = True

    @classmethod
    def cast(cls, value):
        if type(value) is str:
            return value.decode("utf-8")
        elif type(value) is unicode:
            return value
        elif value is None:
            return None if cls.required else u''
        else:
            return unicode(value)


class ArcadiaUrl(sdk2.parameters.String):
    name = consts.ARCADIA_URL_KEY
    required = True
    description = 'Svn url for arcadia'
    default_value = '{}/{}'.format(Arcadia.trunk_url(), 'gencfg')


class TestPrecommitGencfg(sdk2.Task):
    """ Installig and Applying patch and run gen.sh for check work """

    class Requirements(sdk2.Task.Requirements):
        client_tags = ctc.Tag.CUSTOM_GENCFG_BUILD

    class Context(sdk2.Task.Context):
        errors = ''
        tracebacks = ''
        errors_json = ''
        tracebacks_json = ''

    class Parameters(sdk2.Task.Parameters):
        arcadia_url = ArcadiaUrl()
        patch_root = sdk2.parameters.String(
            'Relative patch root',
            default=""
        )
        arcadia_patch = ArcadiaPatch()

    def writeln(self, info):
        logging.info('[{}] {}'.format(datetime.now().strftime('%H:%M:%S'),
                                      info))

    def imitation_selective_checkout(self, source_path):
        path = os.path.dirname(source_path)
        lastlevel = os.path.basename(source_path)
        os.rename(source_path, os.path.join(path, 'gencfg'))
        os.mkdir(source_path)
        shutil.move(
            os.path.join(path, 'gencfg'),
            os.path.join(path, lastlevel)
        )
        return source_path

    def start_installing(self, source_path):
        origin_workdir = os.getcwd()
        os.chdir(os.path.join(source_path, 'gencfg'))

        process = Popen(['./install.sh'], stdout=PIPE)
        for line in process.communicate():
            self.writeln(line)
        os.chdir(origin_workdir)

        return process.returncode

    def start_precommit(self, source_path):
        origin_workdir = os.getcwd()
        os.chdir(os.path.join(source_path, 'gencfg'))

        process = Popen(['./gen.sh', 'precommit'], stdout=PIPE)
        for line in process.communicate():
            self.writeln(line)
        os.chdir(origin_workdir)

        return process.returncode

    def move_build_dir(self, source_path):
        build_old = os.path.join(source_path, 'gencfg', 'build')
        if os.path.exists(build_old):
            build_new = str(self.log_path('build'))
            self.writeln('INFO: Moving {} to {}'.format(
                build_old, build_new
            ))
            shutil.move(build_old, build_new)

    def on_execute(self):
        self.writeln('TASK STARTED')
        arcadia_url = self.Parameters.arcadia_url
        patch = self.Parameters.arcadia_patch
        patch_root = self.Parameters.patch_root

        # Download repository
        self.writeln('INFO: Download repository')
        arcadia = Arcadia.get_arcadia_src_dir(arcadia_url)

        # Move gencfg into arcadia_cache
        self.writeln('INFO: Move gencfg into arcadia_cache')
        arcadia = str(self.imitation_selective_checkout(arcadia))

        # Encode patch to unicode
        self.writeln('INFO: Preparing patch')
        if isinstance(patch, unicode):
            patch = patch.encode('utf-8', 'ignore')

        # Appling patch
        self.writeln('INFO: Appling patch')
        Arcadia.apply_patch(
            os.path.join(arcadia, patch_root),
            patch,
            str(self.log_path())
        )

        # Installing (./install.sh)
        self.writeln('INFO: Run ./install.sh')
        code = self.start_installing(arcadia)
        if code:
            self.writeln('EXITCODE: install.sh {}'.format(code))
            raise TaskFailure('install.sh finsished with code {}'.format(
                code
            ))

        # Check (./gen.sh precommit)
        self.writeln('INFO: Run ./gen.sh precommit')
        code = self.start_precommit(arcadia)
        self.move_build_dir(arcadia)
        if code:
            self.writeln('EXITCODE: gen.sh {}'.format(code))
            raise TaskFailure('gen.sh finsished with code {}'.format(
                code
            ))

    def on_finish(self, prev_status, status):
        self.writeln('STATUS: {} {}'.format(prev_status, status))
        if str(status) == 'SUCCESS':
            self.writeln('TASK FINISHED SUCCESS')
            pass

        elif str(status) == 'FAILURE':
            self.writeln('TASK FINISHED FAILURE')

            raw = ''
            traces = self.find_in_log(
                str(self.log_path()), self.get_taceback
            )
            for file, trace_lst in traces.items():
                header = '\n=========={}==========\n'.format(file)
                footer = '\n' + '=' * len(header)

                raw += header
                for trace in trace_lst:
                    raw += trace + '\n'
                raw += footer

            self.Context.tracebacks = raw
            self.Context.tracebacks_json = json.dumps(traces)

            raw = ''
            errors = self.find_in_log(
                str(self.log_path()), self.get_error
            )
            for errs in errors.values():
                for err in errs:
                    raw += err

            self.Context.errors = raw
            self.Context.errors_json = json.dumps(errors)

        else:
            self.writeln('TASK FINISHED {}'.format(status))
            pass

    def find_in_log(self, dirpath, getter):
        if not os.path.exists(dirpath):
            return []

        traces = {}
        items = os.listdir(dirpath)
        for item in items:
            item = os.path.join(dirpath, item)
            if os.path.isfile(item):
                tr = getter(item)
                if tr:
                    traces[item] = tr
            elif os.path.isdir(item):
                traces.update(self.find_in_log(item, getter))
        return traces

    def get_taceback(self, path):
        trace = ''
        traces = []
        traceback = False
        with open(path, 'r') as log:
            for line in log:
                if line.startswith('Traceback'):
                    traceback = True
                    trace += line
                elif traceback and line.startswith(' '):
                    trace += line
                elif traceback:
                    trace += line
                    traces.append(trace)
                    trace = ''
                    traceback = False
        return traces

    def get_error(self, path):
        errors = []
        with open(path, 'r') as log:
            for line in log:
                if 'failed ... exiting' in line:
                    errors.append(line)
        return errors
