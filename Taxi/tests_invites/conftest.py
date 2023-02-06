# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from invites_plugins import *  # noqa: F403 F401
import pytest  # pylint: disable=wrong-import-order

from tests_invites import util


@pytest.fixture
def invites_db(pgsql):
    return util.InvitesDb(pgsql[util.INVITES_DB_NAME].cursor())
