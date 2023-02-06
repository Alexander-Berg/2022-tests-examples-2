from security.soc.atp_reader_test.src.nain import division
import logging
from DefenderY import DefenderY


logger = logging.getLogger("test_logger")


def test_one():
    logger.info("start test for division ATP")
    assert division(2) == 2
