import datetime
import sys
import json

try:
    import pygments
    import pygments.formatters
    import pygments.lexers
except ImportError:
    pygments = None


class Colors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    GRAY = '\033[37m'
    DARK_GRAY = '\033[37m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    DEFAULT = '\033[0m'
    DEFAULT_BG = '\033[49m'
    BG_BLACK = '\033[40m'


def format_json(obj):
    return json.dumps(
        obj,
        indent=2,
        separators=(',', ': '),
        sort_keys=True,
        ensure_ascii=False,
    )


def colorize_json(formatted_json):
    if pygments is None:
        return formatted_json
    return pygments.highlight(
        formatted_json,
        pygments.lexers.JsonLexer(),
        pygments.formatters.TerminalFormatter(),
    )


class BaseReporter:
    def dump_json(self, doc):
        raise NotImplementedError()

    def section(self, text, doc=None):
        raise NotImplementedError()

    def write_log(self, message):
        raise NotImplementedError()

    def to_report(self, text, doc=None):
        raise NotImplementedError()

    def everywhere(self, text, doc=None):
        raise NotImplementedError()

    def call_on_duty(self):
        raise NotImplementedError()


class ConsoleReporter(BaseReporter):
    def __init__(self, file=None, enable_colors=None):
        self._file = file or sys.stdout

        if enable_colors is not None:
            self._enable_colors = enable_colors
        else:
            self._enable_colors = self._file.isatty()

    def dump_json(self, doc):
        formatted_json = format_json(doc)
        if self._enable_colors:
            self._print(colorize_json(formatted_json))
        else:
            self._print(formatted_json)

    def section(self, text, doc=None):
        if self._enable_colors:
            self._print(f'{Colors.GREEN}===> {text}{Colors.DEFAULT}')
            if doc:
                self.dump_json(doc)
        else:
            self._print(f'===> {text}')
            if doc:
                formatted_json = format_json(doc)
                self._print(formatted_json)

    def _print(self, text=''):
        print(text, file=self._file)


class TelegramReporter(BaseReporter):
    def __init__(self, client, enable_alerts=None, report_file_path=None):
        self._enable_alers = enable_alerts
        self._client = client

        if self._enable_alers:
            if report_file_path:
                self._report_file = open(report_file_path, 'w+')
            else:
                raise Exception('report_file_path is required.')

    def send_report(self, parse_mode=None):
        if self._enable_alers:
            self._report_file.seek(0)
            report = ''.join(i for i in self._report_file.readlines())
            self._client.send_message(report, parse_mode)
            self._report_file.close()

    def write_log(self, message, timestamp=True):
        if self._enable_alers:
            if timestamp:
                message = (
                    f"{datetime.datetime.now().strftime('%H:%M:%S')} {message}"
                )
            self._report_file.write(message)
            self._report_file.write('\n')

    def call_on_duty(self):
        msg = '@tseppelin, check this'
        self.write_log(msg, timestamp=False)


class ProxyReporter(BaseReporter):
    def __init__(self, console_reporter, telegram_reporter):
        self._console_reporter = console_reporter
        self._telegram_reporter = telegram_reporter

    def section(self, text, doc=None):
        self._console_reporter.section(text, doc)

    def to_report(self, text, doc=None):
        if self._telegram_reporter:
            self._telegram_reporter.write_log(text)

    def everywhere(self, text, doc=None):
        self.section(text, doc)
        if self._telegram_reporter:
            self.to_report(text)

    def send_report(self, parse_mode=None):
        if self._telegram_reporter:
            self._telegram_reporter.send_report(parse_mode)

    def dump_json(self, doc):
        self._console_reporter.dump_json(doc=doc)

    def call_on_duty(self):
        if self._telegram_reporter:
            self._telegram_reporter.call_on_duty()
