from robot.mercury.cmpy.config import MEDIUM_DEFAULT, MEDIUM_SSD
from robot.mercury.cmpy.common.fast_annotation import Settings

import logging


def test_correct_settings():
    Settings(primary_medium=MEDIUM_DEFAULT, full_table=True).check()
    Settings(primary_medium=MEDIUM_DEFAULT, full_table=False).check()
    Settings(primary_medium=MEDIUM_SSD, full_table=True).check()
    Settings(primary_medium=MEDIUM_SSD, full_table=False).check()

    all_settings = {"Somebody": Settings(primary_medium=MEDIUM_DEFAULT, full_table=True)}
    Settings(share_with="Somebody").check(all_settings)


def test_bad_settings():
    def check_assert(settings, all_settings=None):
        try:
            settings.check(all_settings)
        except AssertionError as e:
            logging.info("Caught assert as expected: {}".format(e))
            pass
        else:
            raise Exception("{} must not pass check".format(settings))
    check_assert(Settings(primary_medium="abc", full_table=True))
    check_assert(Settings(primary_medium=MEDIUM_DEFAULT))
    check_assert(Settings(full_table=False))
    check_assert(Settings(full_table=False, share_with="Nobody"))
    check_assert(Settings(primary_medium=MEDIUM_SSD, share_with="Nobody"))
    check_assert(Settings())

    all_settings = {
        "Somebody": Settings(share_with="Another"),
        "Another": Settings(primary_medium=MEDIUM_DEFAULT, full_table=True),
    }
    check_assert(Settings(share_with="Somebody"), all_settings)
    check_assert(Settings(share_with="Nobody"), all_settings)
    check_assert(Settings(primary_medium=MEDIUM_DEFAULT, full_table=False, share_with="Another"), all_settings)
    check_assert(Settings(primary_medium=MEDIUM_DEFAULT, share_with="Another"), all_settings)
    check_assert(Settings(full_table=False, share_with="Another"), all_settings)
