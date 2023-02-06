import logging
import subprocess

from sandbox import sdk2


class CollectHandler(logging.Handler):
    def __init__(self, lines=None):
        super().__init__()
        self.lines = lines

    def emit(self, record: logging.LogRecord) -> None:
        str = self.format(record)
        self.lines.append(str)


class ProcessesMixin:
    def _run_ignoring_errors(self, args):
        try:
            self._run(args)
        except:
            pass

    def _run(self, args, log_lines=None):
        # Лог запишется в common.log
        logger = logging.getLogger(args[0])
        if log_lines is None:
            log_lines = []
        logger.addHandler(CollectHandler(log_lines))
        self._run_with_custom_logger(logging.getLogger(args[0]), args)
        return log_lines

    def _run_with_custom_logger(self, logger, args):
        with sdk2.helpers.ProcessLog(self, logger=logger) as pl:
            # Так и задумано, stderr в stdout, чтобы всё сложилось в один файл, так удобнее.
            subprocess.check_call(args, stdout=pl.stdout, stderr=pl.stdout)
