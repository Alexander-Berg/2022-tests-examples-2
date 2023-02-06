from __future__ import unicode_literals
from __future__ import print_function

from sandbox.projects.yabs.partner_share.lib.config.inspect_functions.inspect_functions import validate_config_functions

from sandbox.projects.yabs.partner_share.lib.config.config import (
    get_config,
)
import logging

logger = logging.getLogger(__name__)


def test_functions():
    config = get_config()
    validate_config_functions(config)
