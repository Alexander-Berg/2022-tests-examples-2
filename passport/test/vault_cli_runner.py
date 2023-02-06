# coding: utf-8

import contextlib
import sys

import six


class CLIRunnerResult(object):
    def __init__(self, runner, stdout_bytes, stderr_bytes, exit_code,
                 exception, exc_info=None):
        self.runner = runner
        self.stdout_bytes = stdout_bytes
        self.stderr_bytes = stderr_bytes
        self.exit_code = exit_code
        self.exception = exception
        self.exc_info = exc_info

    @property
    def stdout(self):
        return self.stdout_bytes.decode(self.runner.charset, 'replace').replace('\r\n', '\n')

    def stdout_as_list(self):
        return self.stdout.split('\n')

    @property
    def stderr(self):
        return self.stderr_bytes.decode(self.runner.charset, 'replace').replace('\r\n', '\n')

    def stderr_as_list(self):
        return self.stderr.split('\n')

    def __repr__(self):
        return '<%s %s>' % (
            type(self).__name__,
            self.exception and repr(self.exception) or 'ok',
        )

    def as_dict(self, streams=True, exc_info=False):
        result = {
            'runner_cls': self.runner.__class__.__name__,
            'exit_code': self.exit_code,
            'exception': str(self.exception) if self.exception else None,
        }
        if exc_info:
            result.update({'exc_info': self.exc_info})
        if streams:
            result.update({
                'stdout': self.stdout,
                'stderr': self.stderr,
            })
        return result


class CLIRunner(object):
    def __init__(self, cli_manager, charset=None, mix_stderr=False, stdin=None, stdout=None, stderr=None):
        self.cli_manager = cli_manager
        self.charset = charset or 'utf-8'
        self.mix_stderr = mix_stderr
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    @contextlib.contextmanager
    def isolation(self, stdin=None, stdout=None, stderr=None):
        old_stdin = sys.stdin
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        if not stdout:
            stdout = six.BytesIO()
            sys.stdout = stdout

        if not stderr:
            stderr = stderr or six.BytesIO()
            if self.mix_stderr:
                stderr = stdout
            sys.stderr = stderr

        if isinstance(stdin, six.string_types):
            stdin = six.StringIO(stdin.encode(self.charset))
        stdin = stdin or six.BytesIO()
        sys.stdin = stdin

        try:
            yield (stdout, stderr)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            sys.stdin = old_stdin

    def invoke(self, args=None, stdin=None, catch_exceptions=True):
        exc_info = None

        with self.isolation(stdin=stdin or self.stdin, stdout=self.stdout, stderr=self.stderr) as outstreams:
            exception = None
            exit_code = 0

            try:
                self.cli_manager.process(args)
            except SystemExit as e:
                exc_info = sys.exc_info()
                exit_code = e.code or 0

                if exit_code != 0:
                    exception = e

                if not isinstance(exit_code, int):
                    outstreams[0].write(str(exit_code))
                    outstreams[1].write('\n')
                    exit_code = 1

            except Exception as e:
                if not catch_exceptions:
                    raise
                exception = e
                exit_code = 1
                exc_info = sys.exc_info()
            finally:
                outstreams[0].flush()
                outstreams[1].flush()
                stdout = outstreams[0].getvalue()
                stderr = outstreams[1].getvalue()

            return CLIRunnerResult(
                runner=self,
                stdout_bytes=stdout,
                stderr_bytes=stderr,
                exit_code=exit_code,
                exception=exception,
                exc_info=exc_info,
            )
