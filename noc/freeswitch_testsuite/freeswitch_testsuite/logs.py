import logging
import logging.config
from freeswitch_testsuite.environment_config import LOG_LEVEL, WARNING
from sys import exc_info
from traceback import format_exc

__all__ = [
    'log_debug',
    'log_info',
    'log_warning',
    'log_error',
    'setup_logger',
]


def setup_logger():
    log_config = {
        'version': 1,
        'handlers': {
            'log_console': {
                'class': 'logging.StreamHandler',
                'level': LOG_LEVEL,
                'stream': 'ext://sys.stdout',
                'formatter': 'common'
            },
        },
        'formatters': {
            'common': {
                'format': '%(asctime)s - %(levelname)s - %(message)s'
            },
        },
        'loggers': {
            'freeswitch_testsuite': {
                'level': LOG_LEVEL,
                'handlers': ['log_console']
            },
            'aiohttp.access': {
                'level': WARNING,
                'handlers': ['log_console']
            },
        },
    }
    logging.config.dictConfig(log_config)


def build_message(data, p_trace):
    def get_trace():
        exc_type, exc_value, _ = exc_info()
        return f'{exc_type.__name__} {exc_value}\n{format_exc()}'

    message = f'{data}'
    if p_trace:
        message = f'{message}\nexception={get_trace()}'
    return message


setup_logger()
logger = logging.getLogger("freeswitch_testsuite")


def log_debug(data):
    logger.debug(build_message(data, False))


def log_info(data):
    logger.info(build_message(data, False))


def log_warning(data, print_trace=False):
    logger.warning(build_message(data, print_trace))


def log_error(data, print_trace=False):
    logger.error(build_message(data, print_trace))
